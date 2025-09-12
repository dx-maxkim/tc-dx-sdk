#!/bin/bash

# 스크립트가 중단되면 에러를 출력하도록 설정
set -e

# 도움말을 출력하는 함수
display_help() {
    echo ""
    echo "Usage: ./run_pytest.sh [PYTEST_OPTIONS]"
    echo ""
    echo "  Python 가상 환경('venv_tc')을 자동으로 설정하고 pytest를 실행합니다."
    echo "  가상 환경이 없으면 자동으로 생성하고 'requirements.txt'의 패키지를 설치합니다."
    echo ""
    echo "Options:"
    echo "  [PYTEST_OPTIONS]  pytest에 전달할 모든 옵션 (예: -m smoke, -s, --junitxml=report.xml 등)"
    echo "  --help            이 도움말 메시지를 표시하고 종료합니다."
    echo ""
    echo "Examples:"
    echo "  ./run_pytest.sh               # 모든 테스트 실행"
    echo "  ./run_pytest.sh tests/app     # tests/app 폴더 아래에 있는 TC 들만 test"
    echo "  ./run_pytest.sh tests/app/test_01_compiled_bins.py"
    echo "                                # tests/app/est_01_compiled_bins.py 만 test"
    echo "  ./run_pytest.sh tests/rt      # tests/rt 폴더 아래에 있는 TC 들만 test"
    echo "  ./run_pytest.sh tests/com     # tests/com 폴더 아래에 있는 TC 들만 test"
    echo "  ./run_pytest.sh tests/stream  # tests/stream 폴더 아래에 있는 TC 들만 test"
    echo "  ./run_pytest.sh -m smoke -s   # 'smoke' 마커가 있는 테스트(짧은)를 log 를 보면서 실행"
    echo "  ./run_pytest.sh -m stress -s  # 'stress' 마커가 있는 테스트(장시간)를 log 를 보면서 실행"
    echo "  ./run_pytest.sh --help        # 도움말 보기"
    echo ""
}

# 첫 번째 인자가 -h 또는 --help 인지 확인
case "$1" in
    -h|--help)
        display_help
        exit 0
        ;;
esac

# 가상 환경 디렉터리 이름
VENV_DIR=".venv_tc"

# 1. 가상 환경 디렉터리가 없는지 확인
if [ ! -d "$VENV_DIR" ]; then
    echo "--- 가상 환경 '$VENV_DIR'을(를) 찾을 수 없습니다. 새로 생성합니다. ---"
    
    # 가상 환경 생성
    python3 -m venv "$VENV_DIR"
    
    # 가상 환경 활성화
    source "$VENV_DIR/bin/activate"
    
    # pip 업그레이드 및 패키지 설치
    echo "--- pip 업그레이드 및 패키지를 설치합니다. ---"
    pip install -U pip
    pip install -r requirements.txt
    
    echo "--- 가상 환경 설정 완료. ---"
else
    echo "--- 기존 가상 환경 '$VENV_DIR'을(를) 사용합니다. ---"
fi

# 2. 가상 환경 활성화
source "$VENV_DIR/bin/activate"

# 3. pytest 실행 (스크립트에 전달된 모든 인자를 그대로 넘겨줌)
echo "--- pytest를 실행합니다: pytest $@ ---"
pytest "$@"
