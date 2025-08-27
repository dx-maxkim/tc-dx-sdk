import pytest

# test mode 에 따라 loop count 변화: 50 / 500 / 5000
@pytest.mark.parametrize("loop_cnt", [
    pytest.param(50, marks=pytest.mark.smoke),
    pytest.param(500, marks=pytest.mark.normal),
    pytest.param(5000, marks=pytest.mark.stress),
])
def test_python_examples(config, run_cmd, all_suite_path, loop_cnt):
    """
    parse_model -m 정상 동작하는지 확인하는 테스트
    - Pass: Test 결과가 모두 OK
    - Fail: 원하는 결과가 나오지 않을 경우
    """
    model_path = f"{all_suite_path}/{config('rt')['bin_examples']['model_path']}"
    python_path = f"{all_suite_path}/dx-runtime/dx_rt/examples/python"
    venv_path = f"{all_suite_path}/dx-runtime/venv-dx-runtime/bin/python3"

    # 설정 파일에 필요한 키가 있는지 확인합니다.
    if not model_path or not python_path:
        pytest.fail("config 파일에 'model_path' 또는 'python_path' 키가 없습니다.")

    cmd_list = [
        ['./multi_input_model_inference.py', model_path, None],
        ['./run_async_model_callback.py', f"--model {model_path}", f"--loops {loop_cnt}"],
        ['./run_async_model_conf.py', model_path, loop_cnt],
        ['./run_async_model_profiler.py', model_path, loop_cnt],
        ['./run_async_model.py', model_path, loop_cnt],
        ['./run_async_model_thread.py', model_path, loop_cnt],
        ['./run_async_model_wait.py', model_path, loop_cnt],
        ['./run_batch_model.py', model_path, f"{loop_cnt} 4"], # batch size 4
        ['./run_sync_model_bound.py', model_path, loop_cnt],
        ['./run_sync_model.py', model_path, loop_cnt]
    ]

    for cmd, path, cnt in cmd_list:
        cmd_str = f"{venv_path} {cmd} {path} {cnt}"
        output_text = run_cmd(cmd_str, cwd=python_path)
        print(output_text)
