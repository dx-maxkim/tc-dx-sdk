import pytest


@pytest.mark.smoke
@pytest.mark.normal
@pytest.mark.stress
def test_parse_model(config, run_cmd, all_suite_path):
    """
    parse_model -m 정상 동작하는지 확인하는 테스트
    - Pass: Test 결과가 모두 OK
    - Fail: 원하는 결과가 나오지 않을 경우
    """
    cfg = config('rt')['parse_model']
    model_path = f"{all_suite_path}/{cfg.get('model_path')}"
    expected_output = cfg.get('expected_output')

    # 설정 파일에 필요한 키가 있는지 확인합니다.
    if not model_path or not expected_output:
        pytest.fail("config 파일에 'model_path' 또는 'expected_output' 키가 없습니다.")

    cmd_str = f"parse_model -m {model_path}"
    output_text = run_cmd(cmd_str)

    print(output_text)
    # 각 핵심 라인이 전체 출력(output)에 포함되어 있는지 확인
    for expected_line in expected_output:
        # 각 라인의 앞뒤 공백을 제거하고 비교하여 안정성을 높입니다.
        assert expected_line.strip() in output_text.replace(" ", ""), \
            f"기대 결과('{expected_line}')가 출력에 없습니다.\n전체 출력:\n{output}"
