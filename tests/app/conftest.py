import pathlib
import pytest
import yaml


@pytest.fixture(scope="session")
def config():
    """configs/cfg_app.yaml 로드해서 dict 반환"""
    config_path = pathlib.Path("configs/cfg_app.yaml")

    if not config_path.is_file():
        pytest.fail(f"설정 파일 '{config_path}' 없음")

    return yaml.safe_load(config_path.read_text(encoding="utf-8"))
