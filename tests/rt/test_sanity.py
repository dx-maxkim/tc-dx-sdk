import pytest
import subprocess
import os
import shlex
import time
import pathlib


@pytest.mark.smoke
@pytest.mark.normal
@pytest.mark.stress
def test_sanity_check(config, run_cmd, rt_base_path):
    """
    SanityCheck.sh 가 정상 동작하는지 확인하는 테스트
    - Pass: Test 결과가 모두 OK, 결과 리포트도 잘 생성
    - Fail: Test 결과에 Error 가 있어가 결과 리포트 생성 안될 경우
    """
    report_path = pathlib.Path(rt_base_path) / "dx_rt/dx_report/sanity/result"
    before_log_cnt = len(list(report_path.glob("*.log")))
    print(f"report log count = {before_log_cnt}")

    cmd_str = f"sudo ./SanityCheck.sh"
    output_text = run_cmd(cmd_str, cwd=f"{rt_base_path}/dx_rt")

    # SanityCheck Pass or Fail
    assert "Sanity check PASSED" in output_text, f"Sanity check fail: {output_text}"

    # Check if test report log is generated
    after_log_cnt = len(list(report_path.glob("*.log")))
    print(f"report log count = {after_log_cnt}")

    # 4. 검증 (정확히 1 증가해야 함)
    assert after_log_cnt == before_log_cnt + 1, (
        f"로그 파일 개수가 예상과 다릅니다. "
        f"before={before_log_cnt}, after={after_log_cnt}"
    )
