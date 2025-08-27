import pytest

@pytest.mark.smoke
@pytest.mark.normal
@pytest.mark.stress
def test_dxtop_help(run_cmd):
    """dxtop 의 -h 와 --help 옵션이 모두 동일하게 동작하는지 테스트합니다."""

    output_h = run_cmd("dxtop -h")
    output_help = run_cmd("dxtop --help")

    # Check the same output
    assert output_h == output_help, (
        "Output mismatch between `dxtop -h` and `dxtop --help`\n\n"
        f"-h output:\n{output_h}\n\n--help output:\n{output_help}"
    )
