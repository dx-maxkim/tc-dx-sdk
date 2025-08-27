import subprocess
import pytest
import shlex # 쉘 명령어를 안전하게 분리하기 위한 모듈
import os
import re
from pathlib import Path


@pytest.mark.smoke
@pytest.mark.normal
@pytest.mark.stress
def test_com_version(com_base_path, config, run_cmd):
    """
    dx_com 의 -v, --version 옵션이 잘 동작하는지 확인
    - Pass: 정상적으로 version 정보 출력
    - Fail:동작이 되지 않음
    """
    # YAML 파일에서 설정 정보를 불러옵니다.
    dx_com_path = config['dx_com_path']

    # 설정 파일에 필요한 키가 있는지 확인합니다.
    if not dx_com_path:
        pytest.fail("config 파일에 'dx_com_path' 키가 없습니다.")

    dx_com_ver_from_src = None
    # dx-compile SDK 에서 버전 정보 읽어오기
    with open(f"{com_base_path}/compiler.properties", 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip().startswith('COM_VERSION='):
                dx_com_ver_from_src = line.split('=')[1].strip()
                print(f"DX_COM version from src: {dx_com_ver_from_src}")

    for arg in ['-v', '--version']:
        cmd_str = f"{dx_com_path} {arg}"
        output = run_cmd(cmd_str, cwd=com_base_path)
        match = re.search(r"DX-COM Version:\s*(\d+\.\d+\.\d+)", output)
        if not match:
            pytest.fail("Could not find DX-COM Version")
        dx_com_ver = match.group(1)
        print(f"DX_COM version: {dx_com_ver}")

        # Version matching
        assert dx_com_ver_from_src == dx_com_ver, f"버전 정보 다름 {dx_com_ver} - {dx_com_ver_from_src}"


@pytest.mark.smoke
@pytest.mark.normal
@pytest.mark.stress
def test_com_info(com_base_path, config, run_cmd):
    """
    dx_com 의 -i, --info 옵션이 잘 동작하는지 확인
    - Pass: 정상적으로 version 정보 출력
    - Fail:동작이 되지 않음
    """
    # YAML 파일에서 설정 정보를 불러옵니다.
    dx_com_path = config['dx_com_path']
    expected_info = config['dx_com_info']

    # 설정 파일에 필요한 키가 있는지 확인합니다.
    if not dx_com_path and not expected_info:
        pytest.fail("config 파일에 'dx_com_path' or 'dx_com_info' 키가 없습니다.")

    for arg in ['-i', '--info']:
        cmd_str = f"{dx_com_path} {arg}"
        output = run_cmd(cmd_str, cwd=com_base_path)

        # Check the expected output
        assert expected_info in output, f"기대하는 출력:\n{expected_info}\n실제출력:\n{output}"

    print(f"기대하는 출력값이 모두 존재:\n{expected_info}")
