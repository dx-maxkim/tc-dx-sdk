import re, time, subprocess, pytest


@pytest.mark.parametrize("timeout_sec", [
    pytest.param(2, marks=pytest.mark.smoke),
    pytest.param(5, marks=pytest.mark.normal),
    pytest.param(60, marks=pytest.mark.stress),
])
def test_dxtop_default(config, timeout_sec):
    """
    dxtop 기본 동작 확인:
    - 버전 매칭(DX-RT, NPU driver, DX-TOP)
    - 각 Temp/Voltage/Clock > 0
    """
    cmd = ["dxtop"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         text=True, encoding="utf-8")

    # 정규식으로 필요한 부분만 filtering
    RE_RT  = re.compile(r"DX-RT:\s*(v\d+\.\d+\.\d+)", re.I)
    RE_DRV = re.compile(r"NPU Device driver:\s*(v\d+\.\d+\.\d+)", re.I)
    RE_TOP = re.compile(r"DX-TOP:\s*(v\d+\.\d+\.\d+)", re.I)
    RE_MET = re.compile(r"Temp:\D*(\d+)\D*Voltage:\D*(\d+)\D*Clock:\D*(\d+)", re.I)

    deadline = time.time() + timeout_sec
    m_rt = m_drv = m_top = None
    metrics_seen = 0  # 코어 3개 예시xx

    try:
        line_n = 0
        for line in p.stdout:
            if time.time() > deadline:
                break

            # 루프 안, 정규식 매칭 직전에 추가 (한 줄)
            line = re.sub(r"\x1B\[[0-9;?]*[ -/]*[@-~]", "", line).replace("\r", " ").replace("\u00A0"," ").replace("\u202F"," ").replace("\u2009"," ")

            if not m_rt:  m_rt  = RE_RT.search(line)
            if not m_drv: m_drv = RE_DRV.search(line)
            if not m_top: m_top = RE_TOP.search(line)

            m = RE_MET.search(line)
            print(f"m = {m}")
            if m:
                t, v, c = map(int, m.groups())
                assert t > 0 and v > 0 and c > 0, f"Invalid values: T={t}, V={v}, C={c}"
                print(f"T={t}, V={v}, C={c}")
                metrics_seen += 1
    finally:
        p.terminate()
        try:
            p.wait(timeout=1)
        except subprocess.TimeoutExpired:
            p.kill()

    # 버전 존재 확인
    assert m_rt,  "DX-RT 버전이 출력에 없음"
    assert m_drv, "NPU Device driver 버전이 출력에 없음"
    assert m_top, "DX-TOP 버전이 출력에 없음"

    # 버전 값 비교 (키 이름은 환경에 맞게 조정)
    v_rt, v_drv, v_top = m_rt.group(1), m_drv.group(1), m_top.group(1)
    assert v_rt  == config('rt')['CURRENT_VERSIONS']['DX_RT'],        f"DX-RT mismatch: {v_rt}"
    assert v_drv == config('rt')['CURRENT_VERSIONS']['RT_DRIVER'],    f"Driver mismatch: {v_drv}"
    assert v_top == config('rt')['CURRENT_VERSIONS']['DX_TOP'],       f"DX-TOP mismatch: {v_top}"
    assert metrics_seen >= 1, f"Not enough metric lines: {metrics_seen} < 1"

