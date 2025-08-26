import subprocess
import pytest
import shlex # 쉘 명령어를 안전하게 분리하기 위한 모듈
import os
import pathlib
import time
import signal
import re

@pytest.mark.parametrize("timeout_sec", [
    pytest.param(10, marks=pytest.mark.smoke),
    pytest.param(20, marks=pytest.mark.normal),
    pytest.param(120, marks=pytest.mark.stress),
])
def test_yolo_from_config(app_base_path, timeout_sec, config):
    """
    yolo 어플리케이션을 파일에 정의된 model 을 사용해서 수행 후 결과 검증 (Input: camera)
    - Pass: 문제없이 수행되고 지정된 시간까지 실행 후 에러없이 종료
    - Fail: 동작을 안하거나 동작 간 에러 발생
    """
    # YAML 파일에서 설정 정보를 불러옵니다.
    cfg = config['yolo_camera'] # Load cfg_app.yaml >> refer to tests/app/conftest.py
    command_str = cfg.get('command')

    # 설정 파일에 필요한 키가 있는지 확인합니다.
    if not command_str:
        pytest.fail("config 파일에 'command' 키가 없습니다.")

    command_parts = shlex.split(command_str)

    bk_path = os.getcwd()
    os.chdir(app_base_path)

    process = None
    try:
        # 1. Popen으로 백그라운드에서 프로세스 시작
        print(f"\n프로세스 실행: {' '.join(command_parts)}")
        process = subprocess.Popen(
                command_parts,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True  # ensures output is in string format, not bytes
                )
        # 2. config 파일에 지정된 시간(초)만큼 대기
        print(f"{timeout_sec}초 동안 대기합니다...")
        time.sleep(timeout_sec/2)

        print("프로세스 상태 확인...")
        assert process.poll() is None, f"프로세스가 {timeout_sec}초 이내에 비정상 종료되었습니다."

        time.sleep(timeout_sec/2)
        # 3. 대기 시간이 끝난 후, 프로세스에 종료 신호(SIGINT) 전송
        print(f"시간 초과. 프로세스(PID: {process.pid})에 종료 신호를 보냅니다.")
        process.send_signal(signal.SIGINT) # Ctrl+C와 동일한 신호

        # 4. Check the app is running without errors
        stdout, stderr = process.communicate()
        print("STDOUT:\n", stdout)
        print("STDERR:\n", stderr)

        combined_output = stdout + stderr
        error_indicators = [
            "can't open camera",
            "Error:",
            "File not found exception",
            "can't open/read file",
            "dxrt-exception",
            "could not be opened"
        ]
        for err in error_indicators:
            if err in combined_output:
                pytest.fail(f"실행 중 오류 발생: '{err}'")

        # 패턴 설명: '[DXAPP] [INFO] fps: ' 뒤에 오는 숫자(\d)나 점(.)을 캡처
        match = re.search(r"\[DXAPP\] \[INFO\] fps : ([\d.]+)", combined_output)
        if match:
            pytest.fail("Expected FPS output line was not found.")
            fps = float(match.group(1))
            # FPS 값이 25보다 큰지 assert로 확인. 실패 시 메시지 출력
            assert fps > 25, f"FPS check failed: {fps} is not greater than 25."

        # 5. 프로세스가 실제로 종료될 때까지 최대 10초 대기
        process.wait(timeout=10)
        print("프로세스가 정상적으로 종료되었습니다.")

    except FileNotFoundError:
        pytest.fail(f"실행 파일을 찾을 수 없습니다: '{command_parts[0]}'. 경로를 확인해주세요.")

    except subprocess.TimeoutExpired:
        # wait(10) 시간 동안 종료되지 않은 경우
        print("프로세스가 종료 신호에 반응하지 않아 강제 종료합니다.")
        process.kill() # 강제 종료
        pytest.fail("프로세스가 정상적으로 종료되지 않았습니다.")

    except Exception as e:
        # 기타 예외 처리
        if process:
            process.kill()
        pytest.fail(f"테스트 실행 중 예기치 않은 오류 발생: {e}")

    finally:
        os.chdir(bk_path)
