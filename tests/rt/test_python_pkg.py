import pytest
import subprocess
import os
import shlex
import time
from pathlib import Path


@pytest.mark.smoke
@pytest.mark.normal
@pytest.mark.stress
def test_python_package(config, run_cmd, rt_base_path):
    """
    python_package/make_whl.sh 정상동작 확인
    - Pass: dx_engine whl 파일이 생성됨
    - Fail: 스크립트 실행간 에러가 발생하거나 dx_engine whl 파일 생성 안됨
    """
    print("python_package/make_whl.sh 정상동작 확인")
    whl_path = f"{rt_base_path}/dx_rt/python_package"
    whl_files = list(Path(whl_path).glob("*.whl"))

    if not whl_files:
        print("이전에 빌드된 whl 파일 없음")
    else:
        print(f"이전에 빌드된 whl 파일들{whl_files} 이 있어서 삭제")
        for whl_file in whl_files:
            whl_file.unlink()

    # Python venv
    venv_path = f"{rt_base_path}/{config['python_package']['venv_python']}"
    venv_bin_path = f"{venv_path}/bin"

    env = os.environ.copy()
    env['PATH'] = f"{venv_bin_path}{os.pathsep}{env['PATH']}"
    env['VIRTUAL_ENV'] = str(venv_path)

    cmd_str = f"./make_whl.sh"
    output_text = run_cmd(cmd_str, cwd=whl_path, env=env)

    # Script Pass or Fail
    assert "Successfully built dx-engine" in output_text, f"make_whl.sh fail: {output_text}"

    # 생성된 whl 파일 검증
    whl_files = list(Path(whl_path).glob("*.whl"))
    assert whl_files, f"whl 파일이 생성되지 않았습니다!!"

    print("python_package/make_whl.sh 정상동작 확인 Success!!")
