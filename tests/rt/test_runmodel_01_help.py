import pytest
import subprocess
import os
import shlex
import time
import pathlib


@pytest.mark.smoke
@pytest.mark.normal
@pytest.mark.stress
def test_runmodel_help(config, run_cmd):
    """-h 와 --help 옵션이 모두 동일하게 동작하는지 테스트합니다."""

    for arg in ["-h", "--help"]:
        cmd_str = f"run_model {arg}"
        output_text = run_cmd(cmd_str)

        # 버전 확인
        assert f"Runtime Framework Version: {config['CURRENT_VERSIONS']['DX_RT']}" in output_text
        assert f"Device Driver Version: {config['CURRENT_VERSIONS']['RT_DRIVER']}" in output_text
        assert f"PCIe Driver Version: {config['CURRENT_VERSIONS']['PCIE_DRIVER']}" in output_text

        # 포함성 검증 (빠진 옵션 출력)
        req_opts = config['runmodel_help_required']
        missing = [opt for opt in req_opts if opt not in output_text]
        assert not missing, f"도움말에 누락된 옵션: {missing}"
