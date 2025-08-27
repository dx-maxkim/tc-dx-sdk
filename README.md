<img src="utils/banner.jpg" width="100%" alt="banner">

# tc-dx-sdk
A pre-release SDK validation tool by the CS Team. <br>
It offers both full and smoke tests across four key modules: APP, COM, RT, and STREAM.

## Installation
- Install required deb packages:
    ```shell
    wget https://github.com/allure-framework/allure2/releases/download/2.34.1/allure_2.34.1-1_all.deb --no-check-certificate
    sudo apt install -y ./allure_2.34.1-1_all.deb
    rm allure_2.34.1-1_all.deb
    sudo apt install -y v4l-utils python3-venv
    sudo apt install -y openjdk-11-jdk # If fails, try 'openjdk-17-jdk'
    ```

- Create and activate a virtual environment and then install the required pip packages:
    ```shell
    python3 -m venv .venv-tc
    source .venv-tc/bin/activate
    pip install -U pip
    pip install -r requirements.txt
    ```

## Mandatory Settings
- Set the path to your 'dx-all-suite' directory in the 'pytest.ini':
    ```diff
    --- a/pytest.ini
    +++ b/pytest.ini
    @@ -1,8 +1,8 @@
    [pytest]
    -app_base_path = /home/max/Works/dx-all-suite/dx-runtime/dx_app
    -rt_base_path = /home/max/Works/dx-all-suite/dx-runtime
    -com_base_path = /home/max/Works/dx-all-suite/dx-compiler
    -stream_base_path = /home/max/Works/dx-all-suite/dx-runtime/dx_stream
    +app_base_path = /home/<your path>/dx-all-suite/dx-runtime/dx_app
    +rt_base_path = /home/<your path>/dx-all-suite/dx-runtime
    +com_base_path = /home/<your path>/dx-all-suite/dx-compiler
    +stream_base_path = /home/<your path>/dx-all-suite/dx-runtime/dx_stream
    testpaths = tests
    timeout = 60
    filterwarnings = ignore:The 'py' module is deprecated:DeprecationWarning
    ```

## Usage and Options
- Activate the Python virtual environment
- Full Test
    ```shell
    # Normal mode (standard duration)
    pytest

    # Run with smoke mode (quick check)
    pytest -m smoke

    # Run with stress mode (extended duration)
    pytest -m stress
    ```
- Module Test
    ```shell
    # DX RT test
    pytest tests/rt

    # DX APP test
    pytest tests/app

    # DX Stream test
    pytest tests/stream

    # DX COM test
    pytest tests/com

    # Test a single function:
    # - example: tests/rt/test_dxrt_cli.py -> test_reset_options
    pytest tests/rt/test_dxrt_cli.py -k test_reset_options -s
    ```

### General Options:
- `-s`: Show all messages while running pytest
    ```shell
    pytest -s
    ```

## Report
- Two types of test reports are available: HTML, Dashboard(allure)
- Timestamped HTML reports are auto-generated in the report folder upon test completion `(e.g., report-08-21-20-22.html)`
- Enable dashboard report:
    ```shell
    # Run on your local server only
    allure serve allure-results
    # Run for external view (share your IP in the same network)
    allure serve allure-results --host 192.168.0.114
    ```

## Feedback
- For questions or feedback, please contact the CS team or <dgkim@deepx.ai>
