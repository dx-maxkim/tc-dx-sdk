import pytest
import re


@pytest.mark.smoke
@pytest.mark.normal
@pytest.mark.stress
def test_runmodel_vervose(all_suite_path, config, run_cmd):
    """-v 옵션 사용 시 시스템 정보 및 추가 성능 지표가 출력되는지 검증합니다."""

    for arg in ["-v", "--verbose"]:
        model_path = f"{all_suite_path}/{config['runmodel_benchmark']['default_model_path']}"
        cmd_str = f"run_model -m {model_path} {arg}"
        output = run_cmd(cmd_str)

        print(output)

        # 출력 검증
        # 1. 시스템 정보 헤더들이 모두 출력되는지 확인
        assert "--- CPU Information ---" in output
        assert "--- Architecture Information ---" in output
        assert "--- Memory Information ---" in output

        # 2. CPU 모델 이름이 비어있지 않은지 확인
        m_cpu = re.search(r"Model Name:\s+(.+)", output)
        assert m_cpu is not None, "Could not find 'Model Name' in verbose output."
        assert m_cpu.group(1).strip(), "CPU Model Name is empty."

        # 3. 총 메모리(GB) 값 유효한지 확인
        m_mem = re.search(r"Total Physical Memory:\s*([\d.]+)\s*GB", output)
        assert m_mem is not None, "Could not find 'Total Physical Memory' in verbose output."
        mem_val = float(m_mem.group(1))
        assert mem_val > 0, f"Total Physical Memory must be positive. got={mem_val}"

        # 4. 추가 성능 지표 로그 및 값 검증
        assert "NPU Processing Time Average" in output
        assert "Latency Average" in output

        m_time = re.search(r"NPU Processing Time Average\s*:\s*([\d.]+)\s*ms", output)
        m_lat = re.search(r"Latency Average\s*:\s*([\d.]+)\s*ms", output)
        assert m_time is not None, "Could not find NPU Processing Time."
        assert m_lat is not None, "Could not find Latency Average."

        time_val = float(m_time.group(1))
        lat_val = float(m_lat.group(1))
        assert time_val > 0, f"NPU Processing Time must be positive. got={time_val}"
        assert lat_val > 0, f"Latency Average must be positive. got={lat_val}"
