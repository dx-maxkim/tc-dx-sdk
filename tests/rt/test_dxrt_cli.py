import pytest
import subprocess
import re
import shlex
import time
import os
import pathlib


# --- 헬퍼 함수들 ---
def _run_command(cmd_str):
    """커맨드를 실행하고 결과를 반환하는 헬퍼 함수"""
    command = shlex.split(cmd_str)
    print(f"### Command: {command} ###")
    try:
        result = subprocess.run(
            command, capture_output=True, text=True, check=True, encoding='utf-8'
        )
        return result.stdout
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        error_message = e.stderr if hasattr(e, 'stderr') and e.stderr else str(e)
        pytest.fail(f"Command execution failed for '{' '.join(command)}': {error_message}")

def _get_dxrt_device_count():
    """/dev/dxrt* 패턴에 해당하는 디바이스 개수를 반환합니다."""
    try:
        count = sum(1 for filename in os.listdir('/dev') if filename.startswith('dxrt'))
        return count
    except (FileNotFoundError, PermissionError) as e:
        pytest.fail(f"Cannot determine dxrt device count due to: {e}")
    except Exception as e:
        pytest.fail(f"An unexpected error occurred while counting /dev/dxrt* devices: {e}")
    return 0

def _validate_monitor_block(block_text, expected_npu_count_per_block):
    """모니터링 출력의 한 블록 내용을 검증하는 헬퍼 함수"""
    npu_pattern = re.compile(r"NPU (\d+): voltage (\d+) mV, clock (\d+) MHz, temperature (\d+)'C")
    npu_matches = npu_pattern.findall(block_text)

    assert len(npu_matches) == expected_npu_count_per_block, \
        f"NPU info count mismatch in monitor block. Expected {expected_npu_count_per_block}, got {len(npu_matches)}."
    assert "dvfs" in block_text, "DVFS info is missing."

def _get_current_fw_version(config):
    """-s 명령을 실행하여 현재 펌웨어 버전을 추출합니다."""
    status_output = _run_command(f"{config['EXECUTABLE']} -s")
    match = re.search(r"FW version\s*:\s*(v\d+\.\d+\.\d+)", status_output)
    if not match:
        pytest.fail("Could not find firmware version in status output.")
    return match.group(1)


# --- 테스트 함수들 ---
@pytest.mark.smoke
@pytest.mark.normal
@pytest.mark.stress
@pytest.mark.parametrize("arg", ["-h", "--help"])
def test_help_options(arg, config):
    """dxrt-cli 의 -h 와 --help 옵션이 모두 동일하게 동작하는지 테스트합니다."""
    cmd_str = config['EXECUTABLE'] + ' ' + arg
    output_text = _run_command(cmd_str)
    required_items = [
        f"DXRT {config['CURRENT_VERSIONS']['DXRT']}", "-s", "-m", "-r", "-d", "-u",
        "-g", "-C", "-v", "-h"
    ]
    for item in required_items:
        assert item in output_text, f"'{item}' not found in help message for '{arg}'."


@pytest.mark.smoke
@pytest.mark.normal
@pytest.mark.stress
@pytest.mark.parametrize("arg", ["-s", "--status"])
def test_status_options(arg, config):
    """-s 와 --status 옵션이 모두 동일하게 동작하는지 테스트합니다."""
    cmd_str = config['EXECUTABLE'] + ' ' + arg
    output_text = _run_command(cmd_str)
    versions = config['CURRENT_VERSIONS']
    assert versions['DXRT'] in output_text.splitlines()[0]
    assert f"RT Driver version   : {versions['RT_DRIVER']}" in output_text
    assert f"PCIe Driver version : {versions['PCIE_DRIVER']}" in output_text
    assert f"FW version          : {versions['FIRMWARE']}" in output_text

    for keyword in ["Memory", "Board", "PCIe"]:
        assert keyword in output_text, f"'{keyword}' info is missing."

    npu_pattern = re.compile(r"NPU (\d+): voltage (\d+) mV, clock (\d+) MHz, temperature (\d+)'C")
    npu_matches = npu_pattern.findall(output_text)

    dxrt_device_count = _get_dxrt_device_count()
    expected_total_npu_count = dxrt_device_count * 3

    assert len(npu_matches) == expected_total_npu_count, \
        f"Expected {expected_total_npu_count} NPU stats (from {dxrt_device_count} dxrt devices), but found {len(npu_matches)}."


@pytest.mark.smoke
@pytest.mark.normal
@pytest.mark.stress
@pytest.mark.parametrize("arg", ["-m", "--monitor"])
def test_monitor_options(arg, config):
    """-m, --monitor 옵션이 주기적으로 정상 출력을 내보내는지 테스트합니다."""
    dxrt_device_count = _get_dxrt_device_count()
    expected_npu_count_for_monitor = dxrt_device_count * 3

    command = [config['EXECUTABLE'], arg, '1']
    print(f"### Command: {command} ###")
    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8'
    )
    try:
        blocks_verified = 0
        blocks_to_check = 3
        current_block = ""
        start_time = time.time()
        timeout = 10

        header = process.stdout.readline()
        assert config['CURRENT_VERSIONS']['DXRT'] in header

        for line in process.stdout:
            if time.time() - start_time > timeout:
                pytest.fail("Test timed out after 10 seconds.")

            if "===" in line:
                _validate_monitor_block(current_block, expected_npu_count_for_monitor)
                blocks_verified += 1
                current_block = ""
                if blocks_verified >= blocks_to_check:
                    break
            else:
                current_block += line
        assert blocks_verified >= blocks_to_check, "Did not receive the expected number of blocks."
    finally:
        process.terminate()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()


@pytest.mark.smoke
@pytest.mark.normal
@pytest.mark.stress
def test_firmware_update_scenario(rt_base_path, config):
    """펌웨어 다운그레이드 후 다시 업그레이드하는 전체 시나리오를 테스트합니다."""
    latest_fw_version = config["CURRENT_VERSIONS"]["FIRMWARE"]
    latest_fw_path = f"{rt_base_path}/{config['FIRMWARE_FILES']['LATEST']}"
    old_fw_version = config["MINIMUM_VERSIONS"]["FIRMWARE"]
    old_fw_path = f"{rt_base_path}/{config['FIRMWARE_FILES']['OLD']}"

    initial_version = _get_current_fw_version(config)
    print(f"initial_version = {initial_version}")
    if initial_version != latest_fw_version:
        print(f"FW update - old({initial_version}), new({latest_fw_version:})")
        _run_command(f"{config['EXECUTABLE']}  -u {latest_fw_path} -u force")
        time.sleep(5)
        initial_version = _get_current_fw_version(config)
        print(f"initial_version = {initial_version}")
    assert initial_version == latest_fw_version

    assert "SUCCESS" in _run_command(f"{config['EXECUTABLE']} -u {old_fw_path} -u force")
    time.sleep(5)
    assert _get_current_fw_version(config) == old_fw_version

    assert "SUCCESS" in _run_command(f"{config['EXECUTABLE']}  -u {latest_fw_path} -u force")
    time.sleep(5)
    assert _get_current_fw_version(config) == latest_fw_version


@pytest.mark.smoke
@pytest.mark.normal
@pytest.mark.stress
@pytest.mark.parametrize("arg", ["-g", "--fwversion"])
def test_get_fw_version_options(arg, rt_base_path, config):
    """-g, --fwversion 옵션이 펌웨어 파일의 버전 정보를 정확히 읽어오는지 테스트합니다."""
    fw_path_to_test = f"{rt_base_path}/{config['FIRMWARE_FILES']['LATEST']}"
    expected_version_str = config["CURRENT_VERSIONS"]["FIRMWARE"].replace('v', '')

    output_text = _run_command(f"{config['EXECUTABLE']} {arg} {fw_path_to_test}")
    assert config["CURRENT_VERSIONS"]["DXRT"] in output_text
    assert "FW Binary Information" in output_text
    assert f"fwFile:{fw_path_to_test}" in output_text

    match = re.search(r"Firmware Ver\s*:\s*(\d+\.\d+\.\d+)", output_text)
    assert match is not None, "Could not find 'Firmware Ver' in output."

    extracted_version = match.group(1)
    assert extracted_version == expected_version_str, f"FW version mismatch for {fw_path_to_test}."


@pytest.mark.smoke
@pytest.mark.normal
@pytest.mark.stress
@pytest.mark.parametrize("arg", ["-v", "--version"])
def test_version_options(arg, config):
    """-v, --version 옵션이 최소 요구 버전을 정확히 출력하는지 테스트합니다."""
    output_text = _run_command(f"{config['EXECUTABLE']} {arg}")

    current_versions = config["CURRENT_VERSIONS"]
    min_versions = config["MINIMUM_VERSIONS"]

    assert current_versions["DXRT"] in output_text
    assert f"Device Driver: {current_versions['RT_DRIVER']}" in output_text
    assert f"PCIe Driver: {current_versions['PCIE_DRIVER']}" in output_text
    assert f"Firmware: {min_versions['FIRMWARE']}" in output_text
    assert f"Compiler: {min_versions['COMPILER']}" in output_text
    assert f".dxnn File Format: {min_versions['DXNN_FORMAT']}" in output_text
