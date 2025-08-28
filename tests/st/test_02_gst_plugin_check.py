import pytest
import re


@pytest.mark.smoke
@pytest.mark.normal
@pytest.mark.stress
def test_gst_plugin_install(config, run_cmd):
    """
    GStreamer 플러그인들이 잘 설치됐는지 확인
    - Pass: 정상적으로 설치 출력
    - Fail:동작이 되지 않음
    """
    # YAML 파일에서 설정 정보를 불러옵니다.
    cfg = config('st')['gst_plugin_install']
    cmd = cfg.get('command')
    plugins = set(cfg.get('required_plugins'))

    # GStreamer 플러그인이 잘 설치됐는지 확인
    for plugin in plugins:
        cmd_str = f"{cmd} {plugin}"
        output = run_cmd(cmd_str)

        assert "install ok" in output, f"{plugin} 이 설치되지 않음"
