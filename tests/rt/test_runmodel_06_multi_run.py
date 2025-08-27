import pytest
import time
import subprocess
import shlex


@pytest.mark.parametrize("timeout_sec", [
    pytest.param(10, marks=pytest.mark.smoke),
    pytest.param(20, marks=pytest.mark.normal),
    pytest.param(100, marks=pytest.mark.stress),
])
def test_runmodel_multi_run(all_suite_path, config, timeout_sec):
    """
    run_model 을 동시에 2개 이상 실행시켜 동작 확인
    - Pass: 문제없이 실행 후 정상종료
    - Fail: 동작을 안하거나 동작 실패
    """
    # 사용할 모델
    model_path = config['runmodel_benchmark']['default_model_path']
    

    # 동시에 실행할 run_model 수
    run_model_multi_cnt = 3

    print(f"{timeout_sec} 초 동안 {run_model_multi_cnt}개의 run_model 동시 실행")

    processes = []
    try:
        for cnt in range(run_model_multi_cnt):
            cmd = shlex.split(f"run_model -m {model_path} -t {timeout_sec}")
            print(f"### {cmd}")
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=all_suite_path,
                    text=True, encoding="utf-8")
            processes.append(p)

        for p in processes:
            p.wait()
            assert p.returncode == 0, f"프로세스 {p.pid}가 비정상 종료되었습니다. 종료 코드: {p.returncode}"

    except FileNotFoundError:
        pytest.fail("실행 파일 'run_model'을 찾을 수 없습니다. 경로를 확인하세요.")

    except Exception as e:
        pytest.fail(f"프로세스 실행 중 예외가 발생했습니다: {e}")
