import pathlib
import pytest
import yaml
import os


@pytest.fixture(scope="session")
def config():
    """configs/cfg_rt.yaml 로드"""

    path = pathlib.Path("configs/cfg_rt.yaml")

    if not path.is_file():
        pytest.fail(f"설정 파일 '{path}' 없음")

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    # ~, $HOME 등을 확장
    def _expand(obj):
        if isinstance(obj, dict):
            return {k: _expand(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_expand(v) for v in obj]
        if isinstance(obj, str):
            return os.path.expanduser(os.path.expandvars(obj))
        return obj

    return _expand(data)
