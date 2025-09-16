import subprocess
import pytest
import shlex # 쉘 명령어를 안전하게 분리하기 위한 모듈
import pathlib
import time
import yaml


def load_st_options():
    """parametrize를 위해 설정 파일에서 옵션 리스트를 로드하는 함수"""
    config_path = pathlib.Path("configs/cfg_st.yaml")
    if not config_path.is_file():
        pytest.fail(f"설정 파일 '{config_path}' 없음")

    with open(config_path, 'r', encoding='utf-8') as f:
        config_data = yaml.safe_load(f)

    return config_data['run_demo']['options']


@pytest.mark.timeout(60*5) # 5 min timeout for each test
@pytest.mark.parametrize('option_value', load_st_options())
@pytest.mark.smoke
@pytest.mark.normal
@pytest.mark.stress
def test_run_demo(stream_base_path, option_value, config):
    """
    run_demo.sh 를 option 별로 실행/결과를 검증
    - Pass: 문제없이 수행되고 예상되는 결과를 출력
    - Fail: 동작을 안하거나 예상된 결과와 다른 결과를 출력
    """
    # YAML 파일에서 설정 정보를 불러옵니다.
    cfg = config('st')['run_demo']
    cmd = cfg.get('command')

    process = None
    try:
        process = subprocess.Popen(
            shlex.split(cmd),
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL, # stdout은 완전히 무시
            stderr=subprocess.PIPE,
            cwd=stream_base_path,
            bufsize=1, # line buffering
            text=True  # ensures output is in string format, not bytes
        )
        print(f"### cmd(Popen): {cmd} with option: {option_value}")
        time.sleep(1)

        # run_demo.sh 에 option 값을 넣어주는 부분
        process.stdin.write(f"{option_value}\n")
        process.stdin.flush()
        time.sleep(1)

        print("프로세스 상태 확인...")
        assert process.poll() is None, f"프로세스가 비정상 종료되었습니다."

        error_indicators = [
            "can't open camera",
            "Error:",
            "ERROR:",
            "File not found exception",
            "can't open/read file",
            "dxrt-exception",
            "could not be opened"
        ]
        # process.stderr에서 직접 한 줄씩 반복하여 읽어오며 에러 체크
        # 프로세스가 종료되고 스트림이 닫힐 때까지 이 루프는 계속됩니다.
        for line in process.stderr:
            print(f"STDERR: {line}", end='')
            for err in error_indicators:
                if err in line:
                    pytest.fail(f"실행 중 오류 발생: '{line}'")

        # 프로세스가 완전히 종료될 때까지 기다린다.
        process.wait()
        print("프로세스가 정상적으로 종료되었습니다.")

    except FileNotFoundError:
        pytest.fail(f"실행 파일을 찾을 수 없습니다: '{cmd}'. 경로를 확인해주세요.")

    except subprocess.TimeoutExpired:
        print("프로세스가 종료되지 않아 강제 종료합니다.")
        process.kill() # 강제 종료
        pytest.fail("프로세스가 정상적으로 종료되지 않았습니다.")

    except Exception as e:
        # 기타 예외 처리
        if process:
            process.kill()
        pytest.fail(f"테스트 실행 중 예기치 않은 오류 발생: {e}")
