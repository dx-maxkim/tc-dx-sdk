import subprocess
import pytest
import shlex # 쉘 명령어를 안전하게 분리하기 위한 모듈
import os
from pathlib import Path


@pytest.mark.timeout(60*30) # 30 min timeout for this test 
@pytest.mark.smoke
@pytest.mark.normal
@pytest.mark.stress
def test_com_getting_start(all_suite_path, config, run_cmd):
    """
    dx-all-suite 에 있는 DX-Compiler getting-start script 를 실행 후 정상동작 확인
    - compiler-1_download_onnx.sh
    - compiler-2_setup_calibration_dataset.sh
    - compiler-3_setup_output_path.sh
    - compiler-4_model_compile.sh
    - Pass: 정상적으로 동작 완료된 출력문 확인
    - Fail:동작이 되지 않거나 예상된 완료 출력문 불일치
    """
    # YAML 파일에서 설정 정보를 불러옵니다.
    cfg = config['getting_start'] # Load 'cfg_app.yaml' from 'tests/app/conftest.py'
    step1_sh = f"{all_suite_path}/{cfg.get('step1')}"
    step2_sh = f"{all_suite_path}/{cfg.get('step2')}"
    step3_sh = f"{all_suite_path}/{cfg.get('step3')}"
    step4_sh = f"{all_suite_path}/{cfg.get('step4')}"

    # 해당 스크립트가 존재하는지 확인
    assert os.path.exists(step1_sh), f"지정한 경로를 찾을 수 없습니다: {step1_sh}"
    assert os.path.exists(step2_sh), f"지정한 경로를 찾을 수 없습니다: {step2_sh}"
    assert os.path.exists(step3_sh), f"지정한 경로를 찾을 수 없습니다: {step3_sh}"
    assert os.path.exists(step4_sh), f"지정한 경로를 찾을 수 없습니다: {step4_sh}"

    # 스크립트 실행
    script_path = f"{all_suite_path}/getting-start"
    output = run_cmd(step1_sh, cwd=script_path)
    print(output)
    output = run_cmd(step2_sh, cwd=script_path)
    print(output)
    output = run_cmd(step3_sh, cwd=script_path)
    print(output)
    output = run_cmd(step4_sh, cwd=script_path)
    print(output)
