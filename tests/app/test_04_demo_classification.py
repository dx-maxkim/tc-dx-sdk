import subprocess
import pytest
import shlex # 쉘 명령어를 안전하게 분리하기 위한 모듈
import os
import pathlib
import re

@pytest.mark.smoke
@pytest.mark.normal
@pytest.mark.stress
def test_classification_from_config(app_base_path, config):
    """
    classificaiton 을 실행하고 결과를 검증 (Input: image)
    - Pass: Inference 결과 출력
    - Fail: 실행이 안되거나 다른 결과를 출력
    """
    # YAML 파일에서 설정 정보를 불러옵니다.
    cfg = config('app')['classification_image'] # Load cfg_app.yaml >> refer to tests/app/conftest.py
    command_str = cfg.get('command')
    expected_output = cfg.get('expected_output')

    # 설정 파일에 필요한 키가 있는지 확인합니다.
    if not command_str or not expected_output:
        pytest.fail("config 파일에 'command' 또는 'expected_output' 키가 없습니다.")

    command_parts = shlex.split(command_str)

    # 예외 처리를 포함하여 명령어를 실행합니다.
    try:
        result = subprocess.run(
            command_parts,
            capture_output=True,
            cwd=app_base_path,
            text=True,
            check=True,
            timeout=60
        )
        output = result.stdout

        # 표준 출력(output)에 기대하는 문자열(expected_output)이 포함되어 있는지 확인합니다.
        assert expected_output in output, \
            f"기대 결과('{expected_output}')가 출력에 없습니다.\n전체 출력:\n{output}"

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


@pytest.mark.smoke
@pytest.mark.normal
@pytest.mark.stress
def test_classification_async_from_config(app_base_path, config):
    """
    classificaiton_async 을 실행하고 결과를 검증 (Input: image)
    - Pass: Inference 결과 출력, FPS 가 최소 기준 이상
    - Fail: 실행이 안되거나 다른 결과를 출력, FPS가 기준 미달
    """
    # YAML 파일에서 설정 정보를 불러옵니다.
    cfg = config('app')['classification_image'] # Load cfg_app.yaml >> refer to tests/app/conftest.py
    command_str = cfg.get('command_async')
    expected_output = cfg.get('expected_output')
    minimum_fps = cfg.get('minimum_fps')

    # 설정 파일에 필요한 키가 있는지 확인합니다.
    if not command_str or not expected_output or not minimum_fps:
        pytest.fail("config 파일에 'command' 또는 'expected_output' 또는 'minimum_fps' 키가 없습니다.")

    command_parts = shlex.split(command_str)

    # 예외 처리를 포함하여 명령어를 실행합니다.
    try:
        result = subprocess.run(
            command_parts,
            capture_output=True,
            cwd=app_base_path,
            text=True,
            check=True,
            timeout=60
        )
        output = result.stdout

        # 표준 출력(output)에 기대하는 문자열(expected_output)이 포함되어 있는지 확인합니다.
        assert expected_output in output, \
            f"기대 결과('{expected_output}')가 출력에 없습니다.\n전체 출력:\n{output}"

        m = re.search(r"fps\s*:\s*([\d.]+)", output)
        assert m is not None, "FPS 결과를 찾을 수 없습니다."

        fps = float(m.group(1))
        assert fps > minimum_fps, f"FPS({fps}) 최소 기준({minimum_fps}) 보다 낮습니다"

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
