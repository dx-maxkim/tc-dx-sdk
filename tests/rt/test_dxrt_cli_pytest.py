# test_dxrt_cli.py

import unittest
import subprocess
import re
import time
import os

# 테스트 설정을 하나의 딕셔너리로 통합하여 관리
CONFIG = {
    "EXECUTABLE": "dxrt-cli",
    "CURRENT_VERSIONS": {
        "CLI": "v3.0.0",
        "RT_DRIVER": "v1.7.1",
        "PCIE_DRIVER": "v1.4.1",
        "FIRMWARE": "v2.1.4",
    },
    "MINIMUM_VERSIONS": {
        "FIRMWARE": "v2.1.0",
        "COMPILER": "v1.18.1",
        "DXNN_FORMAT": "v6",
    },
    "FIRMWARE_FILES": {
        "LATEST": os.path.expanduser("~/Works/dx-all-suite/dx-runtime/dx_fw/m1/2.1.4/mdot2/fw.bin"),
        "OLD": os.path.expanduser("~/Works/dx-all-suite/dx-runtime/dx_fw/m1/2.1.0/mdot2/fw.bin"),
    }
}

class TestDxrtCli(unittest.TestCase):
    """dxrt-cli의 다양한 커맨드 옵션을 검증하는 통합 테스트 클래스"""

    def _run_command(self, args):
        """커맨드를 실행하고 결과를 반환하는 헬퍼 함수"""
        command = [CONFIG["EXECUTABLE"]] + [os.path.expanduser(str(arg)) for arg in args]
        try:
            result = subprocess.run(
                command, capture_output=True, text=True, check=True, encoding='utf-8'
            )
            return result.stdout
        except (FileNotFoundError, subprocess.CalledProcessError) as e:
            error_message = e.stderr if hasattr(e, 'stderr') and e.stderr else str(e)
            self.fail(f"Command execution failed for '{' '.join(command)}': {error_message}")

    def _get_dxrt_device_count(self):
        """/dev/dxrt* 패턴에 해당하는 디바이스 개수를 반환합니다."""
        try:
            # /dev 디렉토리에서 'dxrt'로 시작하는 파일 개수를 셉니다.
            count = sum(1 for filename in os.listdir('/dev') if filename.startswith('dxrt'))
            return count
        except (FileNotFoundError, PermissionError) as e:
            self.fail(f"Cannot determine dxrt device count due to: {e}")
        except Exception as e:
            self.fail(f"An unexpected error occurred while counting /dev/dxrt* devices: {e}")
        return 0

    def test_help_options(self):
        """-h 와 --help 옵션이 모두 동일하게 동작하는지 테스트합니다."""
        for arg in ["-h", "--help"]:
            with self.subTest(arg=arg):
                output_text = self._run_command([arg])
                required_items = [
                    f"DXRT {CONFIG['CURRENT_VERSIONS']['CLI']}", "-s", "-m", "-r", "-d", "-u",
                    "-g", "-C", "-v", "-h"
                ]
                for item in required_items:
                    self.assertIn(item, output_text, f"'{item}' not found in help message for '{arg}'.")

    def test_status_options(self):
        """-s 와 --status 옵션이 모두 동일하게 동작하는지 테스트합니다."""
        for arg in ["-s", "--status"]:
            with self.subTest(arg=arg):
                output_text = self._run_command([arg])
                
                versions = CONFIG["CURRENT_VERSIONS"]
                self.assertIn(versions["CLI"], output_text.splitlines()[0], "CLI version mismatch.")
                self.assertIn(f"RT Driver version   : {versions['RT_DRIVER']}", output_text)
                self.assertIn(f"PCIe Driver version : {versions['PCIE_DRIVER']}", output_text)
                self.assertIn(f"FW version          : {versions['FIRMWARE']}", output_text)

                for keyword in ["Memory", "Board", "PCIe"]:
                    self.assertIn(keyword, output_text, f"'{keyword}' info is missing.")

                npu_pattern = re.compile(r"NPU (\d+): voltage (\d+) mV, clock (\d+) MHz, temperature (\d+)'C")
                npu_matches = npu_pattern.findall(output_text)
                
                dxrt_device_count = self._get_dxrt_device_count()
                expected_total_npu_count = dxrt_device_count * 3

                self.assertEqual(len(npu_matches), expected_total_npu_count, 
                                 f"Expected {expected_total_npu_count} NPU stats (from {dxrt_device_count} dxrt devices), but found {len(npu_matches)}.")

    def _validate_monitor_block(self, block_text, expected_npu_count_per_block):
        """모니터링 출력의 한 블록 내용을 검증하는 헬퍼 함수"""
        npu_pattern = re.compile(r"NPU (\d+): voltage (\d+) mV, clock (\d+) MHz, temperature (\d+)'C")
        npu_matches = npu_pattern.findall(block_text)
        
        self.assertEqual(len(npu_matches), expected_npu_count_per_block, 
                         f"NPU info count mismatch in monitor block. Expected {expected_npu_count_per_block}, got {len(npu_matches)}.")
        self.assertIn("dvfs", block_text, "DVFS info is missing.")

    def test_monitor_options(self):
        """-m, --monitor 옵션이 주기적으로 정상 출력을 내보내는지 테스트합니다."""
        dxrt_device_count = self._get_dxrt_device_count()
        expected_npu_count_for_monitor = dxrt_device_count * 3 

        for arg in ["-m", "--monitor"]:
            with self.subTest(arg=arg):
                command = [CONFIG["EXECUTABLE"], arg, "1"] 
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
                    self.assertIn(CONFIG["CURRENT_VERSIONS"]["CLI"], header)

                    for line in process.stdout:
                        if time.time() - start_time > timeout:
                            self.fail("Test timed out after 10 seconds.")

                        if "===" in line:
                            self._validate_monitor_block(current_block, expected_npu_count_for_monitor)
                            blocks_verified += 1
                            current_block = "" 
                            if blocks_verified >= blocks_to_check:
                                break 
                        else:
                            current_block += line
                    self.assertGreaterEqual(blocks_verified, blocks_to_check, "Did not receive the expected number of blocks.")
                finally:
                    process.terminate() 
                    try:
                        process.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        process.kill()

    # def test_reset_options(self):
    #     """-r 0, --reset 0 옵션이 디바이스 리셋을 정상적으로 수행하는지 테스트합니다."""
    #     for arg_pair in [["-r", "0"], ["--reset", "0"]]:
    #         with self.subTest(arg=" ".join(arg_pair)):
    #             output_text = self._run_command(arg_pair)
    #             self.assertIn(CONFIG["CURRENT_VERSIONS"]["CLI"], output_text)
    #             self.assertIn("Device 0 reset", output_text)
    #             self.assertIn("Device reset is complete!", output_text)

    def _get_current_fw_version(self):
        """-s 명령을 실행하여 현재 펌웨어 버전을 추출합니다."""
        status_output = self._run_command(["-s"])
        match = re.search(r"FW version\s*:\s*(v\d+\.\d+\.\d+)", status_output)
        if not match:
            self.fail("Could not find firmware version in status output.")
        return match.group(1)

    def test_firmware_update_scenario(self):
        """펌웨어 다운그레이드 후 다시 업그레이드하는 전체 시나리오를 테스트합니다."""
        latest_fw_version = CONFIG["CURRENT_VERSIONS"]["FIRMWARE"]
        latest_fw_path = CONFIG["FIRMWARE_FILES"]["LATEST"]
        old_fw_version = CONFIG["MINIMUM_VERSIONS"]["FIRMWARE"]
        old_fw_path = CONFIG["FIRMWARE_FILES"]["OLD"]
       
        initial_version = self._get_current_fw_version()
        if initial_version != latest_fw_version:
            self._run_command(["-u", latest_fw_path, "force"])
            sleep(5)
            initial_version = self._get_current_fw_version()
        self.assertEqual(initial_version, latest_fw_version)
       
        self.assertIn("SUCCESS", self._run_command(["-u", old_fw_path, "-u", "force"]))
        sleep(5)
        self.assertEqual(self._get_current_fw_version(), old_fw_version)
        self.assertIn("SUCCESS", self._run_command(["-u", latest_fw_path]))
        sleep(5)
        self.assertEqual(self._get_current_fw_version(), latest_fw_version)

    def test_get_fw_version_options(self):
        """-g, --fwversion 옵션이 펌웨어 파일의 버전 정보를 정확히 읽어오는지 테스트합니다."""
        fw_path_to_test = CONFIG["FIRMWARE_FILES"]["LATEST"]
        expected_version_str = CONFIG["CURRENT_VERSIONS"]["FIRMWARE"].replace('v', '')

        for arg in ["-g", "--fwversion"]:
            with self.subTest(arg=arg, path=fw_path_to_test):
                output_text = self._run_command([arg, fw_path_to_test])
                self.assertIn(CONFIG["CURRENT_VERSIONS"]["CLI"], output_text)
                self.assertIn("FW Binary Information", output_text)
                self.assertIn(f"fwFile:{fw_path_to_test}", output_text)

                match = re.search(r"Firmware Ver\s*:\s*(\d+\.\d+\.\d+)", output_text)
                self.assertIsNotNone(match, "Could not find 'Firmware Ver' in output.")
                
                extracted_version = match.group(1)
                self.assertEqual(extracted_version, expected_version_str,
                                 f"FW version mismatch for {fw_path_to_test}.")

    def test_version_options(self):
        """-v, --version 옵션이 최소 요구 버전을 정확히 출력하는지 테스트합니다."""
        for arg in ["-v", "--version"]:
            with self.subTest(arg=arg):
                output_text = self._run_command([arg])
                
                current_versions = CONFIG["CURRENT_VERSIONS"]
                min_versions = CONFIG["MINIMUM_VERSIONS"]

                self.assertIn(current_versions["CLI"], output_text)
                self.assertIn(f"Device Driver: {current_versions['RT_DRIVER']}", output_text)
                self.assertIn(f"PCIe Driver: {current_versions['PCIE_DRIVER']}", output_text)
                self.assertIn(f"Firmware: {min_versions['FIRMWARE']}", output_text)
                self.assertIn(f"Compiler: {min_versions['COMPILER']}", output_text)
                self.assertIn(f".dxnn File Format: {min_versions['DXNN_FORMAT']}", output_text)

if __name__ == '__main__':
    unittest.main(verbosity=2)
