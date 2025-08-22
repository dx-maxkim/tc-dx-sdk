import subprocess
import pytest
import shlex # 쉘 명령어를 안전하게 분리하기 위한 모듈
import os
import pathlib

@pytest.mark.smoke
@pytest.mark.normal
@pytest.mark.stress
def test_run_detector_from_config(app_base_path, config):
    """
    run_detector 를 정의된 configuration 으로  실행하고 결과를 검증
    - Pass: 문제없이 수행되고 예상되는 결과를 출력
    - Fail: 동작을 안하거나 예상된 결과와 다른 결과를 출력
    """
    # YAML 파일에서 설정 정보를 불러옵니다.
    cfg = config['run_detector_test'] # Load 'cfg_app.yaml' from 'tests/app/conftest.py'
    command_str = cfg.get('command')
    expected_output = cfg.get('expected_output')

    # 설정 파일에 필요한 키가 있는지 확인합니다.
    if not command_str or not expected_output:
        pytest.fail("config 파일에 'command' 또는 'expected_output' 키가 없습니다.")

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

        # 각 핵심 라인이 전체 출력(output)에 포함되어 있는지 확인
        for expected_line in expected_output:
            # 각 라인의 앞뒤 공백을 제거하고 비교하여 안정성을 높입니다.
            assert expected_line.strip() in output.replace(" ", ""), \
                   f"기대 결과('{expected_line}')가 출력에 없습니다.\n전체 출력:\n{output}"

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


