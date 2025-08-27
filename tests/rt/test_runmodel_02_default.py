import pytest
import re


@pytest.mark.smoke
@pytest.mark.normal
@pytest.mark.stress
def test_runmodel_default(all_suite_path, config, run_cmd):
    """run_model 의 -m, --model 옵션으로 기본 벤치마크 모드가 정상 동작하는지 테스트합니다."""

    for arg in ["-m", "--model"]:
        model_path = f"{all_suite_path}/{config('rt')['runmodel_benchmark']['default_model_path']}"
        cmd_str = f"run_model {arg} {model_path}"
        output = run_cmd(cmd_str)

        print(output)

        # 출력 검증
        assert f"modelFile: {model_path}" in output
        assert "Benchmark Result" in output

        m = re.search(r"FPS\s*:\s*([\d.]+)", output)
        assert m is not None, "FPS 결과를 찾을 수 없습니다."

        # 숫자 검증
        fps = float(m.group(1))
        assert fps > 0, f"FPS는 양수여야 합니다. 현재 값: {fps}"
