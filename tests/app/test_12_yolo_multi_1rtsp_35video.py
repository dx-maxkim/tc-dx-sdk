import subprocess
import pytest
import shlex
import pathlib
import time
import signal
import shutil
import os, select

ERROR_TOKENS = [
    "can't open camera", "File not found exception",
    "can't open/read file", "dxrt-exception",
    "could not be opened", "Error:"
]

@pytest.mark.parametrize("timeout_sec", [
    pytest.param(30, marks=pytest.mark.smoke),
    pytest.param(60, marks=pytest.mark.normal),
    pytest.param(120, marks=pytest.mark.stress),
])
def test_yolo_from_config(app_base_path, timeout_sec, config):
    """
    yolo_multi 어플리케이션을 파일에 정의된 configuration 로 수행 후 결과 검증 (1 rtsp + 35-ch videos)
    - Pass: 문제없이 수행되고 지정된 시간까지 실행 후 에러없이 종료
    - Fail: 동작을 안하거나 동작 간 에러 발생
    """
    cfg = config('app')['yolo_multi_1rtsp_35video']
    command_str = cfg.get('command')
    copy_config = cfg.get('copy_config')
    enable_local_rtsp_server = cfg.get('enable_local_rtsp_server')
    assert command_str, "config 파일에 'command' 키가 없습니다."

    if copy_config == 'true':
        src_file = "utils/yolo_multi_1rtsp_35_demo.json"
        dst_file = f"{app_base_path}/example/yolo_multi/yolo_multi_1rtsp_35_demo.json"
        shutil.copy(src_file, dst_file)
        assert pathlib.Path(dst_file).exists(), "파일이 제대로 복사되지 않았습니다."

    rtsp_server_process = None
    if enable_local_rtsp_server == 'true':
        rtsp_command = shlex.split('python3 utils/rtsp_server.py')
        rtsp_server_process = subprocess.Popen(rtsp_command)
        time.sleep(1) # wait for camera ready

    print(f"Run cmd: {command_str}")
    p = subprocess.Popen(
        shlex.split(command_str),
        cwd=app_base_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,   # 합치기
        text=False,                 # 바이너리로 읽고 직접 decode
        bufsize=0
    )

    CHUNK = 65536
    end = time.time() + timeout_sec
    logs = []
    hit_token = None
    early_exit = False

    while True:
        now = time.time()
        if now >= end:
            break
        if p.poll() is not None:
            # 타임아웃 전에 종료됨 → 실패 조건
            early_exit = True
            break

        r, _, _ = select.select([p.stdout], [], [], 0.5) # 0.5 초마다 확인
        if r:
            data = os.read(p.stdout.fileno(), CHUNK)  # 고정 크기 읽기(블로킹 회피)
            if not data:
                # 파이프 EOF
                early_exit = True
                break
            chunk = data.decode(errors="replace")
            logs.append(chunk)
            for tok in ERROR_TOKENS:
                if tok in chunk:
                    hit_token = tok
                    break
        if hit_token:
            break

    # 종료 시그널 및 마무리
    print("Run for {timeout_sec} sec, Send SIGINT to stop the test!")
    try:
        p.send_signal(signal.SIGINT)
    except ProcessLookupError:
        pass  # 이미 종료된 경우
    finally:
        if rtsp_server_process:
            print(f"RTSP 서버 프로세스 (PID: {rtsp_server_process.pid})를 종료합니다.")
            rtsp_server_process.kill()

    try:
        p.wait(timeout=10)
    except subprocess.TimeoutExpired:
        p.terminate()
        try:
            p.wait(timeout=5)
        except subprocess.TimeoutExpired:
            p.kill()
            p.wait(timeout=5)

    # === 실패 조건 처리 ===
    if hit_token:
        pytest.fail(f"실행 중 오류 패턴 감지: {hit_token}")

    if early_exit:
        pytest.fail(f"프로세스가 타임아웃({timeout_sec}s) 전에 종료되었습니다. rc={p.returncode}")
