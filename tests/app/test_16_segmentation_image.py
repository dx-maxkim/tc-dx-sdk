import subprocess
import pytest
import shlex # 쉘 명령어를 안전하게 분리하기 위한 모듈
import os
import pathlib

@pytest.mark.smoke
@pytest.mark.normal
@pytest.mark.stress
def test_pose_from_config(app_base_path, config):
    """
    segmentstion 을 지정된 image input 으로  실행하고 결과를 검증
    - Pass: 문제없이 수행되고 결과를 이미지 파일로 <model name>_result.jpg 로 output 폴더에 저장
    - Fail: 동작을 안하거나 동작 간 에러 발생, 또는 결과파일 생성 안됨
    """
    # YAML 파일에서 설정 정보를 불러옵니다.
    cfg = config['segmentation_image'] # Load cfg_app.yaml >> refer to tests/app/conftest.py
    command_str = cfg.get('command')
    result_file = pathlib.Path(cfg.get('expected_result'))

    # 혹시 이전에 실패해서 파일이 남아있다면 미리 삭제하여 테스트 환경을 깨끗하게 합니다.
    if result_file.exists():
        result_file.unlink()

    # 설정 파일에 필요한 키가 있는지 확인합니다.
    if not command_str or not result_file:
        pytest.fail("config 파일에 'command' 또는 'expected_result' 키가 없습니다.")

    command_parts = shlex.split(command_str)

    bk_path = os.getcwd()
    os.chdir(app_base_path)

    # 예외 처리를 포함하여 명령어를 실행합니다.
    try:
        result = subprocess.run(
            command_parts,
            capture_output=True,
            text=True,
            check=True,
            timeout=60
        )
        output = result.stdout

        print(f"'{result_file}' 파일의 존재를 확인합니다.")
        assert result_file.is_file(), f"PASS 조건 실패: '{result_file}' 파일이 생성되지 않았습니다."

        # 삭제하여 테스트 환경을 깨끗하게 합니다.
        if result_file.exists():
            output_dir = pathlib.Path(f"{bk_path}/output")
            output_dir.mkdir(exist_ok=True)
            result_file.rename(f"{bk_path}/output/segmentation_{config.get('expected_result')}")

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
        os.chdir(bk_path)

