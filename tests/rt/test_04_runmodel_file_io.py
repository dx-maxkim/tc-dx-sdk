import pytest
import re


@pytest.mark.smoke
@pytest.mark.normal
@pytest.mark.stress
def test_runmodel_single(all_suite_path, config, run_cmd):
    """-i/-o 옵션의 short/long form 사용 시 벤치마크 및 파일 입출력을 검증합니다."""

    model_path = f"{all_suite_path}/{config['runmodel_benchmark']['default_model_path']}"
    input_path = CONFIG["IO_FILES"]["INPUT"]
    golden_path = CONFIG["IO_FILES"]["GOLDEN_OUTPUT"]
    custom_output_filename = "test_output.bin"

    scenarios = [
        ("default_output", CONFIG["IO_FILES"]["DEFAULT_OUTPUT"], "output.bin", None),
        ("custom_output_short", CONFIG["IO_FILES"]["CUSTOM_OUTPUT"], custom_output_filename, f"-o {custom_output_filename}",
        ("custom_output_long", CONFIG["IO_FILES"]["CUSTOM_OUTPUT"], custom_output_filename, f"--output {custom_output_filename}")
    ]

    for input_opt in ["-i", "--input"]:
        for name, output_path, expected_filename_in_log, extra_opts in scenarios:
            cmd_str = f"run_model -m {model_path} {input_opt} {input_path} {extra_opts}"
            output = run_cmd(cmd_str)

            print(output)

            # 로그 검증
            assert f"modelFile: {model_path}" in output
            assert f"inputFile: {input_path}" in output
            assert f"Output Saved As : {expected_filename_in_log}" in output
            assert "Benchmark Result" in output

            m = re.search(r"FPS\s*:\s*([\d.]+)", output)
            assert m is not None, "FPS 결과를 찾을 수 없습니다."
            fps = float(m.group(1))
            assert fps > 0, f"FPS는 양수여야 합니다. 현재 값: {fps}"

            # 파일 생성/일치 검증
            assert os.path.exists(output_path), f"출력 파일이 생성되지 않았습니다: {output_path}"
            assert filecmp.cmp(output_path, golden_path, shallow=False), (
                f"출력 파일이 골든과 다릅니다: {output_path} != {golden_path}"
            )

            # 정리
            try:
                if os.path.exists(output_path):
                    os.remove(output_path)
            except OSError:
                pass
