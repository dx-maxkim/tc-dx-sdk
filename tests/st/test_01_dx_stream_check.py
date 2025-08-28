import pytest
import re


@pytest.mark.smoke
@pytest.mark.normal
@pytest.mark.stress
def test_dx_st_install(config, run_cmd):
    """
    Gstreamer dxstream 플러그인들이 잘 설치됐는지 확인
    - Pass: 정상적으로 설치 출력
    - Fail:동작이 되지 않음
    """
    # YAML 파일에서 설정 정보를 불러옵니다.
    cfg = config('st')['dx_st_install']
    cmd = cfg.get('command')
    expected = cfg.get('expected')

    # dxstream 플러그인이 잘 설치됐는지 확인
    output = run_cmd(cmd)
    output = re.sub(r'^ +', '', output, flags=re.MULTILINE) # 각 라인 앞의 space 제거

    assert expected in output, \
            f"dxstream 이 잘 설치되지 않음\n----expected:\n{expected}\n----actual out:\n{output}\n"
