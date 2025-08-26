import pathlib
import subprocess
import pytest
import os

@pytest.mark.smoke
@pytest.mark.normal
@pytest.mark.stress
def test_directory_contains_exact_files_from_config(app_base_path, config):
    """
    dx_app/bin 폴더 아래에 빌드된 demo excutable 실행파일들이 있는지 확인
     - Pass: 목록에 있는 파일들이 모두 존재하는 경우
     - Fail: 목록에 있는 파일들이 없거나 목록 외의  다른 파일이 있을 경우
    """
    CONFIG = config['file_bin'] # Load cfg_app.yaml >> refer to tests/app/conftest.py
    APP_DIR = pathlib.Path(CONFIG['directory'])
    EXPECTED_FILES = set(CONFIG['expected_files']) # 리스트를 집합(set)으로 변환

    # 1. 테스트할 폴더가 존재하는지 확인합니다.
    BASE_PATH = pathlib.Path(app_base_path)
    APP_PATH = BASE_PATH / APP_DIR

    if not APP_PATH.is_dir():
        pytest.fail(f"테스트 대상 폴더 '{APP_PATH}'가 존재하지 않습니다.")

    # 2. 폴더 안의 실제 파일 목록을 집합(set)으로 가져옵니다.
    actual_files = {f.name for f in APP_PATH.glob('*') if f.is_file()}

    # 3. YAML에서 로드한 기대 파일 목록과 실제 파일 목록이 정확히 일치하는지 검증합니다.
    assert actual_files == EXPECTED_FILES, (
        "폴더의 내용이 설정 파일(config.yaml)과 다릅니다.\n"
        f"  - 누락된 파일: {sorted(list(EXPECTED_FILES - actual_files))}\n"
        f"  - 불필요한 파일: {sorted(list(actual_files - EXPECTED_FILES))}"
    )


@pytest.mark.smoke
@pytest.mark.normal
@pytest.mark.stress
def test_bin_help_from_config(app_base_path, config):
    """
    dx_app/bin 폴더 아래에 빌드된 demo excutable 실행파일들이 -h, --help 옵션을 지원하는지 확인
     - Pass: help 옵션을 통해 기능별 설명이 출력
     - Fail: 기능 설명 출력되지 않음
    """
    CONFIG = config['file_bin'] # Load cfg_app.yaml >> refer to tests/app/conftest.py
    APP_DIR = pathlib.Path(CONFIG['directory'])
    EXPECTED_FILES = set(CONFIG['expected_files']) # 리스트를 집합(set)으로 변환

    bk_path = os.getcwd()
    os.chdir(app_base_path)

    for exe in sorted(EXPECTED_FILES):
        exe = f"{APP_DIR}/{exe}"
        # 실행권한 확인
        assert os.access(exe, os.X_OK), f"실행 권한 없음: {exe}"

        # -h. --help도 시도
        for args in (["-h"], ["--help"]):
            try:
                res = subprocess.run(
                    [str(exe), *args],
                    capture_output=True, text=True, encoding="utf-8",
                    timeout=5, check=False
                )
            except subprocess.TimeoutExpired:
                pytest.fail(f"도움말 출력 타임아웃(5s): {exe} {' '.join(args)}")

            # 성공 기준: 종료코드 0, stderr 비어있음, stdout에 뭔가 있음
            assert res.returncode == 0 and res.stdout.strip() and not res.stderr.strip(), f"출력이 없음"
