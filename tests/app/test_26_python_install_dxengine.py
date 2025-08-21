import subprocess
import pytest
import yaml
import shlex # 쉘 명령어를 안전하게 분리하기 위한 모듈
import os
from pathlib import Path

def load_config():
    """config.yaml 파일을 읽어와 설정을 반환합니다."""
    config_path = Path('configs/cfg_app.yaml')
    if not config_path.is_file():
        pytest.fail(f"설정 파일 '{config_path}'를 찾을 수 없습니다.")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config['dxengine_install_test']

@pytest.mark.smoke
@pytest.mark.normal
@pytest.mark.stress
def test_run_imagenet_from_config(app_base_path):
    """
    파일에 정의된 설치 경로에 따라 dx-engine install 잘 되는지 검증
    - Pass: 정상적으로 설치 완료된 출력문 확인
    - Fail:설치가 되지 않거나 예상된 설치 완료 출력문 불일치
    """
    # YAML 파일에서 설정 정보를 불러옵니다.
    config = load_config()
    expected_output = config.get('expected_output')
    target_venv_python = Path(config.get('venv_python'))
    dxengine_install_path = Path(config.get('dxengine_path'))

    # 설정 파일에 필요한 키가 있는지 확인합니다.
    if not expected_output or not target_venv_python or not dxengine_install_path:
        pytest.fail("config_26.yaml 파일에 'expected_output' or  'target_venv_python' or 'dxengine_install_path' 키가 없습니다.")

    bk_path = os.getcwd()
    os.chdir(app_base_path)

    # Python venv 스크립트가 존재하는지 확인
    assert os.path.exists(dxengine_install_path), f"지정한 파이썬 경로를 찾을 수 없습니다: {dxengine_install_path}"

    # 1. 경로 및 실행 파일 설정
    # 사용할 가상환경 내부의 pip 실행 파일 경로를 지정합니다.
    pip_executable = target_venv_python / "bin" / "pip"

    # 2. 사전 조건 확인 (테스트 환경이 올바른지 검증)
    assert (dxengine_install_path / pip_executable).exists(), \
        f"지정한 가상환경의 pip를 찾을 수 없습니다: {pip_executable}"
    assert (dxengine_install_path / "pyproject.toml").exists() or \
           (dxengine_install_path / "setup.py").exists(), \
           f"{dxengine_install_path}에서 패키지 설정 파일(pyproject.toml 또는 setup.py)을 찾을 수 없습니다."

    # 3. 명령어 구성 및 실행
    command = [
        str(pip_executable),  # Path 객체를 문자열로 변환
        "install",
        "."
    ]

    # 예외 처리를 포함하여 명령어를 실행합니다.
    try:
        result = subprocess.run(
            command,
            cwd=dxengine_install_path,
            capture_output=True,
            text=True,
            check=True,
            timeout=60
        )
        output = result.stdout

        # 표준 출력(output)에 기대하는 문자열(expected_output)이 포함되어 있는지 확인합니다.
        assert expected_output in output, \
            f"기대 결과('{expected_output}')가 출력에 없습니다.\n전체 출력:\n{output}"

    except FileNotFoundError:
        pytest.fail(f"실행 파일을 찾을 수 없습니다: '{command}'. 경로를 확인해주세요.")

    except subprocess.CalledProcessError as e:
        pytest.fail(
            f"스크립트 실행에 실패했습니다 (종료 코드: {e.returncode}).\n"
            f"명령어: {command}\n"
            f"에러 로그: {e.stderr}"
        )

    except subprocess.TimeoutExpired:
        pytest.fail("스크립트 실행 시간이 초과되었습니다.")

    finally:
        os.chdir(bk_path)


