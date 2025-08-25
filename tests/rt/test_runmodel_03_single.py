import pytest
import re


@pytest.mark.smoke
@pytest.mark.normal
@pytest.mark.stress
def test_runmodel_single(all_suite_path, config, run_cmd):
    """-s, -l 옵션의 short/long form을 사용한 single mode 동작을 검증합니다."""

    model_path = f"{all_suite_path}/{config['runmodel_benchmark']['default_model_path']}"

    for single_opt in ["-s", "--single"]:
        for loops_opt in ["-l", "--loops"]:
            cmd_str = f"run_model -m {model_path} {single_opt} {loops_opt} 1"
            output = run_cmd(cmd_str)

            print(output)

            # 공통 검증
            assert f"modelFile: {model_path}" in output
            assert "Run model target mode : Single Mode" in output
            assert "Benchmark Result (single input)" in output

            m = re.search(r"FPS\s*:\s*([\d.]+)", output)
            assert m is not None, "FPS 결과를 찾을 수 없습니다."

            fps = float(m.group(1))
            assert fps > 0, f"FPS는 양수여야 합니다. 현재 값: {fps}"
