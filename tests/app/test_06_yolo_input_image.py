import subprocess
import pytest
import yaml
import shlex # 쉘 명령어를 안전하게 분리하기 위한 모듈
import os
import pathlib

def load_config():
    """config.yaml 파일을 읽어와 설정을 반환합니다."""
    config_path = pathlib.Path('configs/cfg_app.yaml')
    if not config_path.is_file():
        pytest.fail(f"설정 파일 '{config_path}'를 찾을 수 없습니다.")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config['yolo_image']

def get_test_ids(test_cases):
    """테스트 케이스의 'name'을 pytest ID로 사용합니다."""
    return [case['name'] for case in test_cases]


# test mode 에 따라 aging count 변화: 1 / 10 / 1000
@pytest.mark.parametrize("repeat_cnt", [
    pytest.param(1, marks=pytest.mark.smoke),
    pytest.param(10, marks=pytest.mark.normal),
    pytest.param(1000, marks=pytest.mark.stress),
])
@pytest.mark.parametrize(
    "test_case",                # 테스트 함수에 전달될 인자 이름
    load_config(),              # 인자에 주입될 데이터 (테스트 케이스 리스트)
    ids=get_test_ids(load_config()) # 각 테스트를 구별할 ID
)
def test_yolo_aging_from_config(app_base_path, test_case, repeat_cnt):
    """
    yolo 어플리케이션을 파일에 정의된 model 을 사용해서 수행 후 결과 검증 (Input: image)
    - Pass: 문제없이 수행되고 종료 시 결과 파일 <model name>_result.jpg 파일을 output 폴더에 저장
    - Fail: 동작을 안하거나 에러 발생, 또는 결과파일 저장 안되는 경우
    """
    # YAML 파일에서 설정 정보를 불러옵니다.
    command_str = test_case.get('command')
    result_file = pathlib.Path(f"{app_base_path}/{test_case.get('expected_result')}")

    # 설정 파일에 필요한 키가 있는지 확인합니다.
    if not command_str or not result_file:
        pytest.fail(f"설정 파일의 테스트 케이스 '{test_case.get('name')}'에 'command' 또는 'expected_result' 키가 없습니다.")

    command_parts = shlex.split(command_str)

    # 혹시 이전에 실패해서 파일이 남아있다면 미리 삭제하여 테스트 환경을 깨끗하게 합니다.
    if result_file.exists():
        result_file.unlink()

    # 예외 처리를 포함하여 명령어를 실행합니다.
    try:
        for run_cnt in range(repeat_cnt):
            result = subprocess.run(
                command_parts,
                capture_output=True,
                cwd=app_base_path,
                text=True,
                check=True,
                timeout=60
            )
            output = result.stdout

            print(f"'{test_case.get('name')}' 을 image input 으로 추론 성공 - {run_cnt+1}번째 확인")
            assert result_file.is_file(), f"PASS 조건 실패: '{result_file}' 파일이 생성되지 않았습니다."

            # 삭제하여 테스트 환경을 깨끗하게 합니다.
            if result_file.exists():
                output_dir = pathlib.Path(f"output")
                output_dir.mkdir(exist_ok=True)
                result_file.rename(f"output/{test_case.get('name')}_{test_case.get('expected_result')}")

    except FileNotFoundError:
        pytest.fail(f"실행 파일을 찾을 수 없습니다: '{command_parts}'. 경로를 확인해주세요.")

    except subprocess.CalledProcessError as e:
        pytest.fail(
            f"스크립트 실행에 실패했습니다 (종료 코드: {e.returncode}).\n"
            f"명령어: {command_str}\n"
            f"에러 로그: {e.stderr}"
        )
    except subprocess.TimeoutExpired:
        pytest.fail("스크립트 실행 시간이 초과되었습니다.")

    finally:
        result_image_path = f"output/{test_case.get('name')}_{test_case.get('expected_result')}"
        if os.path.exists(result_image_path):
            subprocess.Popen(['xdg-open', str(result_image_path)])
