import subprocess
import pytest
import shlex # 쉘 명령어를 안전하게 분리하기 위한 모듈
import os
from pathlib import Path


@pytest.mark.smoke
@pytest.mark.normal
@pytest.mark.stress
def test_com_help(com_base_path, config, run_cmd):
    """
    dx_com 의 help 옵션이 잘 동작하는지 확인
    - Pass: 정상적으로 help 출력문 확인
    - Fail:동작이 되지 않음
    """
    # YAML 파일에서 설정 정보를 불러옵니다.
    dx_com_path = config['dx_com_path']

    # 설정 파일에 필요한 키가 있는지 확인합니다.
    if not dx_com_path:
        pytest.fail("config 파일에 'dx_com_path' 키가 없습니다.")

    # -h, --help 옵션 각각 실행 후 동일여부 확인
    cmd_str = f"{dx_com_path} -h"
    output_h = run_cmd(cmd_str, cwd=com_base_path)
    cmd_str = f"{dx_com_path} --help"
    output_help = run_cmd(cmd_str, cwd=com_base_path)

    # 해당 스크립트가 존재하는지 확인
    assert output_h == output_help, f"-h, --help 결과가 동일하지 않음"

    print(output_h)
