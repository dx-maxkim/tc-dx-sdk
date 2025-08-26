import subprocess
import pytest
import shlex # 쉘 명령어를 안전하게 분리하기 위한 모듈
import os
import pathlib
import time
import signal


@pytest.mark.smoke
@pytest.mark.normal
@pytest.mark.stress
def test_run_detector_from_config(app_base_path, config):
    """
    run_detector 를 정의된 configuration 으로  실행하고 결과를 검증
    - Pass: 문제없이 수행되고 예상되는 결과를 출력
    - Fail: 동작을 안하거나 예상된 결과와 다른 결과를 출력
    """
    # YAML 파일에서 설정 정보를 불러옵니다.
    cfg = config['run_detector_test'] # Load 'cfg_app.yaml' from 'tests/app/conftest.py'
    command_str = cfg.get('command')
    expected_output = cfg.get('expected_output')
    result_file1 = pathlib.Path(cfg.get('expected_result1'))
    result_file2 = pathlib.Path(cfg.get('expected_result2'))
    result_file3 = pathlib.Path(cfg.get('expected_result3'))
    result_file4 = pathlib.Path(cfg.get('expected_result4'))
    result_file5 = pathlib.Path(cfg.get('expected_result5'))

    # 설정 파일에 필요한 키가 있는지 확인합니다.
    if not command_str or not expected_output:
        pytest.fail("config 파일에 'command' 또는 'expected_output' 키가 없습니다.")

    command_parts = shlex.split(command_str)

    bk_path = os.getcwd()
    os.chdir(app_base_path)

    # 예외 처리를 포함하여 명령어를 실행합니다.
    try:
        result = subprocess.run(
            command_parts,
            capture_output=True,
            text=True,
            check=True,
            timeout=60
        )
        output = result.stdout

        # 표준 출력(output)에 기대하는 문자열(expected_output)이 포함되어 있는지 확인합니다.
        assert expected_output in output, \
            f"기대 결과('{expected_output}')가 출력에 없습니다.\n전체 출력:\n{output}"

        # 삭제하여 테스트 환경을 깨끗하게 합니다.
        if result_file1.exists():
            output_dir = pathlib.Path(f"{bk_path}/output")
            output_dir.mkdir(exist_ok=True)
            result_file1.rename(f"{bk_path}/output/run_det_{cfg.get('expected_result1')}")
        if result_file2.exists(): result_file2.rename(f"{bk_path}/output/run_det_{cfg.get('expected_result2')}")
        if result_file3.exists(): result_file3.rename(f"{bk_path}/output/run_det_{cfg.get('expected_result3')}")
        if result_file4.exists(): result_file4.rename(f"{bk_path}/output/run_det_{cfg.get('expected_result4')}")
        if result_file5.exists(): result_file5.rename(f"{bk_path}/output/run_det_{cfg.get('expected_result5')}")

    except FileNotFoundError:
        pytest.fail(f"실행 파일을 찾을 수 없습니다: '{command_parts}'. 경로를 확인해주세요.")

    except subprocess.CalledProcessError as e:
        pytest.fail(
            f"스크립트 실행에 실패했습니다 (종료 코드: {e.returncode}).\n"
            f"명령어: {command_str}\n"
            f"에러 로그: {e.stderr}"
        )

    except subprocess.TimeoutExpired:
        pytest.fail("스크립트 실행 시간이 초과되었습니다.")

    finally:
        os.chdir(bk_path)
        result_image_path1 = f"{bk_path}/output/run_det_{cfg.get('expected_result1')}"
        result_image_path2 = f"{bk_path}/output/run_det_{cfg.get('expected_result2')}"
        result_image_path3 = f"{bk_path}/output/run_det_{cfg.get('expected_result3')}"
        result_image_path4 = f"{bk_path}/output/run_det_{cfg.get('expected_result4')}"
        result_image_path5 = f"{bk_path}/output/run_det_{cfg.get('expected_result5')}"
        if os.path.exists(result_image_path1): subprocess.Popen(['xdg-open', str(result_image_path1)])
        if os.path.exists(result_image_path2): subprocess.Popen(['xdg-open', str(result_image_path2)])
        if os.path.exists(result_image_path3): subprocess.Popen(['xdg-open', str(result_image_path3)])
        if os.path.exists(result_image_path4): subprocess.Popen(['xdg-open', str(result_image_path4)])
        if os.path.exists(result_image_path5): subprocess.Popen(['xdg-open', str(result_image_path5)])


@pytest.mark.timeout(60*10) # 10 min timeout for this test 
@pytest.mark.smoke
@pytest.mark.normal
@pytest.mark.stress
def test_run_detector_all_from_config(app_base_path, config):
    """
    run_detector 를 정의된 모든 configuration  실행/결과를 검증
    - Pass: 문제없이 수행되고 예상되는 결과를 출력
    - Fail: 동작을 안하거나 예상된 결과와 다른 결과를 출력
    """
    cmd_extra_list = [
        'command_extra_01', 'command_extra_02', 'command_extra_03', 'command_extra_04',
        'command_extra_05', 'command_extra_06', 'command_extra_07', 'command_extra_08',
        'command_extra_09', 'command_extra_10', 'command_extra_11', 'command_extra_12',
        'command_extra_13', 'command_extra_14', 'command_extra_15', 'command_extra_16',
        'command_extra_17', 'command_extra_18'
    ]

    for cfg_idx in cmd_extra_list:
        # YAML 파일에서 설정 정보를 불러옵니다.
        command_str = config['run_detector_test'][cfg_idx]

        # Preview demo
        if 'realtime' or 'multi_input' in command_str:
            process = None
            timeout_sec = 6
            try:
                process = subprocess.Popen(
                        shlex.split(command_str),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        cwd=app_base_path,
                        text=True  # ensures output is in string format, not bytes
                        )
                print(f"{timeout_sec}초 동안 대기합니다...")
                time.sleep(timeout_sec/2)

                print("프로세스 상태 확인...")
                assert process.poll() is None, f"프로세스가 {timeout_sec}초 이내에 비정상 종료되었습니다."

                time.sleep(timeout_sec/2)
                # 대기 시간이 끝난 후, 프로세스에 종료 신호(SIGINT) 전송
                print(f"시간 초과. 프로세스(PID: {process.pid})에 종료 신호를 보냅니다.")
                process.send_signal(signal.SIGINT) # Ctrl+C와 동일한 신호

                # Check the app is running without errors
                stdout, stderr = process.communicate()
                print("STDOUT:\n", stdout)
                print("STDERR:\n", stderr)

                combined_output = stdout + stderr
                error_indicators = [
                    "can't open camera",
                    "Error:",
                    "File not found exception",
                    "can't open/read file",
                    "dxrt-exception",
                    "could not be opened"
                ]
                for err in error_indicators:
                    if err in combined_output:
                        pytest.fail(f"실행 중 오류 발생: '{err}'")

                # 프로세스가 실제로 종료될 때까지 최대 10초 대기
                process.wait(timeout=10)
                print("프로세스가 정상적으로 종료되었습니다.")

            except FileNotFoundError:
                pytest.fail(f"실행 파일을 찾을 수 없습니다: '{command_parts[0]}'. 경로를 확인해주세요.")

            except subprocess.TimeoutExpired:
                # wait(10) 시간 동안 종료되지 않은 경우
                print("프로세스가 종료 신호에 반응하지 않아 강제 종료합니다.")
                process.kill() # 강제 종료
                pytest.fail("프로세스가 정상적으로 종료되지 않았습니다.")

            except Exception as e:
                # 기타 예외 처리
                if process:
                    process.kill()
                pytest.fail(f"테스트 실행 중 예기치 않은 오류 발생: {e}")

        # Image demo
        else:
            try:
                result = subprocess.run(
                    shlex.split(command_str),
                    capture_output=True,
                    text=True,
                    check=True,
                    cwd=app_base_path,
                    timeout=10
                )
                output = result.stdout

            except FileNotFoundError:
                pytest.fail(f"실행 파일을 찾을 수 없습니다: '{command_parts}'. 경로를 확인해주세요.")

            except subprocess.CalledProcessError as e:
                pytest.fail(
                    f"스크립트 실행에 실패했습니다 (종료 코드: {e.returncode}).\n"
                    f"명령어: {command_str}\n"
                    f"에러 로그: {e.stderr}"
                )

            except subprocess.TimeoutExpired:
                pytest.fail("스크립트 실행 시간이 초과되었습니다.")
