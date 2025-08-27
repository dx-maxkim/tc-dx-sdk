import pytest
import os
import yaml
import pathlib
import shlex
import subprocess
from pytest_html import extras
from datetime import datetime
from py.xml import html


def pytest_configure(config):
    """
    pytest 실행 시 --html 옵션이 있으면 동적으로 리포트 파일 이름을 설정합니다.
    """
    # --html 옵션이 지정되지 않았다면 아무것도 하지 않습니다.
    if not config.option.htmlpath:
        return

    # 1. 날짜-시간- 분을 기반으로 새로운 파일 경로를 생성합니다. (예: report/report-08-18-14-51.html)
    now_str = datetime.now().strftime("%m-%d-%H-%M")
    report_dir = "report"
    report_filename = f"report-{now_str}.html"
    report_path = os.path.join(report_dir, report_filename)

    # 2. 리포트 디렉토리 생성 (없는 경우)
    os.makedirs(report_dir, exist_ok=True)

    # 3. pytest 설정(config)의 htmlpath 값을 새로운 경로로 덮어씁니다.
    config.option.htmlpath = report_path


def pytest_addoption(parser):
    """pytest.ini 파일에 사용자 정의 옵션을 등록합니다."""

    custom_options = [
        ("app_base_path", "The base path to the dx_app under test"),    
        ("rt_base_path", "The base path to the dx_rt under test"),    
        ("com_base_path", "The base path to the dx_com under test"),    
        ("stream_base_path", "The base path to the dx_stream under test"),    
        ("all_suite_path", "The base path to the dx-all-suite under test"),    
    ]

    for option, help_txt in custom_options:
        parser.addini(
            option,  # .ini 파일에 사용할 변수 이름
            help=help_txt,  # --help 시 보일 설명
            type="string",
            default=None
        )


@pytest.fixture(scope="session")
def app_base_path(request):
    """
    pytest.ini 파일에서 DX_APP 기본 경로를 읽어와 반환하는 Fixture
    """
    # 1. pytest.ini 파일로부터 'app_base_path' 값 읽기
    path = request.config.getini("app_base_path")

    # 2. 경로 유효성 검사
    if not path:
        pytest.fail("'app_base_path'가 pytest.ini 파일에 정의되지 않았습니다.")
    if not os.path.isdir(path):
        pytest.fail(f"pytest.ini에 지정된 애플리케이션 경로를 찾을 수 없습니다: {path}")
    return path


@pytest.fixture(scope="session")
def rt_base_path(request):
    """
    pytest.ini 파일에서 DX_RT 기본 경로를 읽어와 반환하는 Fixture
    """
    # 1. pytest.ini 파일로부터 'rt_base_path' 값 읽기
    path = request.config.getini("rt_base_path")

    # 2. 경로 유효성 검사
    if not path:
        pytest.fail("'rt_base_path'가 pytest.ini 파일에 정의되지 않았습니다.")
    if not os.path.isdir(path):
        pytest.fail(f"pytest.ini에 지정된 애플리케이션 경로를 찾을 수 없습니다: {path}")
    return path


@pytest.fixture(scope="session")
def com_base_path(request):
    """
    pytest.ini 파일에서 DX_COM 기본 경로를 읽어와 반환하는 Fixture
    """
    # 1. pytest.ini 파일로부터 'com_base_path' 값 읽기
    path = request.config.getini("com_base_path")

    # 2. 경로 유효성 검사
    if not path:
        pytest.fail("'com_base_path'가 pytest.ini 파일에 정의되지 않았습니다.")
    if not os.path.isdir(path):
        pytest.fail(f"pytest.ini에 지정된 애플리케이션 경로를 찾을 수 없습니다: {path}")
    return path


@pytest.fixture(scope="session")
def stream_base_path(request):
    """
    pytest.ini 파일에서 DX_STREAM 기본 경로를 읽어와 반환하는 Fixture
    """
    # 1. pytest.ini 파일로부터 'stream_base_path' 값 읽기
    path = request.config.getini("stream_base_path")

    # 2. 경로 유효성 검사
    if not path:
        pytest.fail("'stream_base_path'가 pytest.ini 파일에 정의되지 않았습니다.")
    if not os.path.isdir(path):
        pytest.fail(f"pytest.ini에 지정된 애플리케이션 경로를 찾을 수 없습니다: {path}")
    return path


@pytest.fixture(scope="session")
def all_suite_path(request):
    """
    pytest.ini 파일에서 dx-all-suite 기본 경로를 읽어와 반환하는 Fixture
    """
    # 1. pytest.ini 파일로부터 'all_suite_path' 값 읽기
    path = request.config.getini("all_suite_path")

    # 2. 경로 유효성 검사
    if not path:
        pytest.fail("'all_suite_path'가 pytest.ini 파일에 정의되지 않았습니다.")
    if not os.path.isdir(path):
        pytest.fail(f"pytest.ini에 지정된 애플리케이션 경로를 찾을 수 없습니다: {path}")
    return path


# @pytest.hookimpl(hookwrapper=True) 데코레이터를 추가하고 함수 내용을 수정합니다.
@pytest.hookimpl(hookwrapper=True)

# @pytest.hookimpl(hookwrapper=True) 데코레이터를 추가하고 함수 내용을 수정합니다.
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    pytest의 기본 makereport 실행을 감싸는(wrap) 훅입니다.
    기본 훅이 실행된 후, 생성된 report 객체를 받아와 수정합니다.
    """
    # 다른 훅들이 실행되도록 하고, 그 결과(outcome)를 받아옵니다.
    outcome = yield

    # outcome에서 report 객체를 추출합니다. 이것이 올바른 방법입니다.
    report = outcome.get_result()

    # 테스트 함수의 docstring(설명)을 가져옵니다.
    # description이 None일 경우를 대비해 str()으로 감싸줍니다.
    description = str(item.function.__doc__)

    # report 객체에 description 속성을 추가합니다.
    report.description = description


def pytest_html_results_table_header(cells):
    """
    결과 테이블의 헤더를 수정하는 훅입니다. 
    'Description' 이라는 새로운 컬럼을 추가합니다.
    """
    cells.insert(-1, html.th('Description', class_='sortable', **{'data-column-type': 'description'}))


def pytest_html_results_table_row(report, cells):
    """
    결과 테이블의 각 행을 수정하는 훅입니다. (이 함수는 변경할 필요가 없습니다)
    makereport 훅에서 저장했던 description을 가져와 새로운 셀(td)로 추가합니다.
    """
    # getattr로 설명을 가져온 뒤, html.td 생성 시 style 속성을 추가합니다.
    desc = getattr(report, 'description', '')
    description_html = html.td(desc, class_='col-description', style="white-space: pre-wrap;")
    cells.insert(-1, description_html)



@pytest.fixture(scope="session")
def config():
    """
    설정 파일을 로드하는 팩토리 함수를 반환합니다.
    사용법: config("app") 또는 config("com")
    """
    def _load_config(cfg_type: str):
        """cfg_type에 따라 적절한 설정 파일을 로드하는 함수"""
        
        # cfg_type 값에 따라 파일 이름을 매핑
        file_map = {
            "app": "configs/cfg_app.yaml",
            "com": "configs/cfg_com.yaml",
            "rt":  "configs/cfg_rt.yaml",
            "st":  "configs/cfg_st.yaml"
        }

        # 유효하지 않은 cfg_type이 들어올 경우 에러 발생
        if cfg_type not in file_map:
            pytest.fail(f"잘못된 cfg_type: '{cfg_type}'")

        config_path = pathlib.Path(file_map[cfg_type])

        if not config_path.is_file():
            pytest.fail(f"설정 파일 '{config_path}' 없음")

        try:
            # 파일 읽기 및 YAML 파싱
            return yaml.safe_load(config_path.read_text(encoding="utf-8"))
        except yaml.YAMLError as e:
            # YAML 형식 오류 발생 시 테스트 실패 처리
            pytest.fail(f"'{config_path}' 파일의 YAML 형식이 잘못되었습니다.\n오류: {e}")

    # 데이터가 아닌 함수 자체를 반환
    return _load_config


@pytest.fixture
def run_cmd():
    """
    사용법:
        stdout = run_cmd("abc --help")
    """
    def _run_command(cmd_str, *, check=True, env=None, cwd=None, timeout=None, echo=True):
        command = shlex.split(cmd_str)
        if echo:
            print(f"### Command: {command}")
        merged_env = {**os.environ, "LC_ALL": "C"}
        if env:
            merged_env.update(env)

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=check,
                encoding="utf-8",
                env=merged_env,
                cwd=cwd,
                timeout=timeout,
            )
            return result.stdout

        except FileNotFoundError as e:
            pytest.fail(f"Command not found: {command[0]}\n{e}")

        except subprocess.CalledProcessError as e:
            err = e.stderr or e.stdout or str(e)
            pytest.fail(f"Command execution failed for '{' '.join(command)}'\n{err}")

        except subprocess.TimeoutExpired as e:
            pytest.fail(f"Command timed out after {timeout}s: {' '.join(command)}\n{e}")

    return _run_command
