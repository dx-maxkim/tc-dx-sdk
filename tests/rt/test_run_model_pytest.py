# test_run_model_pytest.py

import unittest
import subprocess
import os
import re
import filecmp

# 중복되는 기본 경로를 변수로 처리하여 가독성 및 유지보수성 향상
BASE_PATH = os.path.expanduser("/home/max/Works/dx-all-suite")

# 테스트 설정을 하나의 딕셔너리로 통합하여 관리
CONFIG = {
    "EXECUTABLE": "run_model",
    "VERSIONS": {
        "RUNTIME": "v3.0.0",
        "DEVICE_DRIVER": "v1.7.1",
        "PCIE_DRIVER": "v1.4.1",
    },
    "MODEL_FILES": {
        "YOLOV7": os.path.join(BASE_PATH, "workspace/res/models/models-1_60_1/YoloV7.dxnn")
    },
    "IO_FILES": {
        "INPUT": os.path.join(BASE_PATH, "YoloV7_input_0.bin"),
        "DEFAULT_OUTPUT": os.path.join(BASE_PATH, "output.bin"),
        "CUSTOM_OUTPUT": os.path.join(BASE_PATH, "test_output.bin"), # -o 옵션용 출력 파일
        "GOLDEN_OUTPUT": os.path.join(BASE_PATH, "YoloV7_npu_0_output_0.bin")
    }
}

class TestRunModel(unittest.TestCase):
    """run_model의 다양한 커맨드 옵션을 검증하는 통합 테스트 클래스"""

    def tearDown(self):
        """각 테스트가 끝난 후 생성된 출력 파일을 삭제합니다."""
        files_to_remove = [
            CONFIG["IO_FILES"]["DEFAULT_OUTPUT"],
            CONFIG["IO_FILES"]["CUSTOM_OUTPUT"]
        ]
        for file_path in files_to_remove:
            if os.path.exists(file_path):
                os.remove(file_path)

    def _run_command(self, args, cwd=BASE_PATH):
        """커맨드를 실행하고 결과를 반환하는 헬퍼 함수"""
        command = [str(arg) for arg in args]
        try:
            result = subprocess.run(
                command, capture_output=True, text=True, check=True, encoding='utf-8',
                cwd=cwd
            )
            return result.stdout
        except (FileNotFoundError, subprocess.CalledProcessError) as e:
            error_message = e.stderr if hasattr(e, 'stderr') and e.stderr else str(e)
            self.fail(f"Command execution failed for '{' '.join(command)}': {error_message}")

    def _run_model_command(self, args):
        """run_model 커맨드를 실행하는 래퍼 함수"""
        executable_path = CONFIG["EXECUTABLE"]
        full_args = [executable_path] + [os.path.expanduser(str(arg)) for arg in args]
        return self._run_command(full_args, cwd=BASE_PATH)

    def test_help_options(self):
        """-h 와 --help 옵션이 모두 동일하게 동작하는지 테스트합니다."""
        for arg in ["-h", "--help"]:
            with self.subTest(arg=arg):
                output_text = self._run_model_command([arg])
                
                versions = CONFIG["VERSIONS"]
                self.assertIn(f"Runtime Framework Version: {versions['RUNTIME']}", output_text)
                self.assertIn(f"Device Driver Version: {versions['DEVICE_DRIVER']}", output_text)
                self.assertIn(f"PCIe Driver Version: {versions['PCIE_DRIVER']}", output_text)

                required_options = [
                    "-m, --model", "-i, --input", "-o, --output", "-b, --benchmark",
                    "-s, --single", "-v, --verbose", "-n, --npu", "-l, --loops",
                    "-t, --time", "-d, --devices", "-f, --fps", "--skip-io",
                    "--use-ort", "-h, --help",
                ]
                
                for option in required_options:
                    self.assertIn(option, output_text, f"'{option}' not found in help message for '{arg}'.")

    def test_benchmark_mode_default(self):
        """-m, --model 옵션으로 기본 벤치마크 모드가 정상 동작하는지 테스트합니다."""
        model_path = CONFIG["MODEL_FILES"]["YOLOV7"]
        for model_opt in ["-m", "--model"]:
            with self.subTest(option=model_opt):
                output_text = self._run_model_command([model_opt, model_path])

                self.assertIn(f"modelFile: {model_path}", output_text)
                self.assertIn("Benchmark Result", output_text)

                match = re.search(r"FPS\s*:\s*([\d.]+)", output_text)
                self.assertIsNotNone(match, "Could not find FPS result in the output.")
                
                fps_string = match.group(1)
                try:
                    fps_value = float(fps_string)
                    self.assertGreater(fps_value, 0, f"FPS value ({fps_value}) must be a positive number.")
                except ValueError:
                    self.fail(f"Extracted FPS value '{fps_string}' is not a valid number.")

    def test_benchmark_with_io(self):
        """-i/-o 옵션의 short/long form 사용 시 벤치마크 및 파일 입출력을 검증합니다."""
        model_path = CONFIG["MODEL_FILES"]["YOLOV7"]
        input_path = CONFIG["IO_FILES"]["INPUT"]
        golden_path = CONFIG["IO_FILES"]["GOLDEN_OUTPUT"]
        custom_output_filename = "test_output.bin"

        scenarios = [
            ("default_output", CONFIG["IO_FILES"]["DEFAULT_OUTPUT"], "output.bin", []),
            ("custom_output_short", CONFIG["IO_FILES"]["CUSTOM_OUTPUT"], custom_output_filename, ["-o", custom_output_filename]),
            ("custom_output_long", CONFIG["IO_FILES"]["CUSTOM_OUTPUT"], custom_output_filename, ["--output", custom_output_filename])
        ]

        for input_opt in ["-i", "--input"]:
            for name, output_path, expected_filename_in_log, options in scenarios:
                with self.subTest(scenario=name, input_opt=input_opt):
                    command_args = ["-m", model_path, input_opt, input_path] + options
                    output_text = self._run_model_command(command_args)

                    self.assertIn(f"modelFile: {model_path}", output_text)
                    self.assertIn(f"inputFile: {input_path}", output_text)
                    self.assertIn(f"Output Saved As : {expected_filename_in_log}", output_text)
                    self.assertIn("Benchmark Result", output_text)

                    match = re.search(r"FPS\s*:\s*([\d.]+)", output_text)
                    self.assertIsNotNone(match, "Could not find FPS result in the output.")
                    try:
                        fps_value = float(match.group(1))
                        self.assertGreater(fps_value, 0, f"FPS value ({fps_value}) must be a positive number.")
                    except ValueError:
                        self.fail(f"Extracted FPS value '{match.group(1)}' is not a valid number.")

                    self.assertTrue(os.path.exists(output_path), f"Output file '{output_path}' was not created.")
                    self.assertTrue(filecmp.cmp(output_path, golden_path, shallow=False),
                                    f"Output file '{output_path}' does not match the golden file '{golden_path}'.")

    def test_single_mode(self):
        """-s, -l 옵션의 short/long form을 사용한 single mode 동작을 검증합니다."""
        model_path = CONFIG["MODEL_FILES"]["YOLOV7"]
        
        for single_opt in ["-s", "--single"]:
            for loops_opt in ["-l", "--loops"]:
                with self.subTest(single_opt=single_opt, loops_opt=loops_opt):
                    command_args = ["-m", model_path, single_opt, loops_opt, "1"]
                    output_text = self._run_model_command(command_args)

                    self.assertIn(f"modelFile: {model_path}", output_text)
                    self.assertIn("Run model target mode : Single Mode", output_text)
                    self.assertIn("Benchmark Result (single input)", output_text)

                    match = re.search(r"FPS\s*:\s*([\d.]+)", output_text)
                    self.assertIsNotNone(match, "Could not find FPS result in the output.")
                    
                    fps_string = match.group(1)
                    try:
                        fps_value = float(fps_string)
                        self.assertGreater(fps_value, 0, f"FPS value ({fps_value}) must be a positive number.")
                    except ValueError:
                        self.fail(f"Extracted FPS value '{fps_string}' is not a valid number.")

    def test_verbose_mode(self):
        """-v 옵션 사용 시 시스템 정보 및 추가 성능 지표가 출력되는지 검증합니다."""
        model_path = CONFIG["MODEL_FILES"]["YOLOV7"]

        for verbose_opt in ["-v", "--verbose"]:
            with self.subTest(option=verbose_opt):
                output_text = self._run_model_command(["-m", model_path, verbose_opt])

                # 1. 시스템 정보 헤더들이 모두 출력되는지 확인
                self.assertIn("--- CPU Information ---", output_text)
                self.assertIn("--- Architecture Information ---", output_text)
                self.assertIn("--- Memory Information ---", output_text)

                # 2. CPU 모델 이름이 비어있지 않은지 확인
                cpu_model_match = re.search(r"Model Name:\s+(.+)", output_text)
                self.assertIsNotNone(cpu_model_match, "Could not find 'Model Name' in verbose output.")
                self.assertTrue(cpu_model_match.group(1).strip(), "CPU Model Name is empty.")

                # 3. 총 메모리 정보가 유효한지 확인
                mem_total_match = re.search(r"Total Physical Memory:\s+([\d.]+)\s+GB", output_text)
                self.assertIsNotNone(mem_total_match, "Could not find 'Total Physical Memory' in verbose output.")
                try:
                    mem_val = float(mem_total_match.group(1))
                    self.assertGreater(mem_val, 0, "Total Physical Memory must be a positive number.")
                except ValueError:
                    self.fail("Could not parse Total Physical Memory value as a number.")

                # 4. 추가 성능 지표 로그 및 값 검증
                self.assertIn("NPU Processing Time Average", output_text)
                self.assertIn("Latency Average", output_text)

                time_match = re.search(r"NPU Processing Time Average\s*:\s*([\d.]+)\s*ms", output_text)
                latency_match = re.search(r"Latency Average\s*:\s*([\d.]+)\s*ms", output_text)

                self.assertIsNotNone(time_match, "Could not find NPU Processing Time.")
                self.assertIsNotNone(latency_match, "Could not find Latency Average.")

                try:
                    time_val = float(time_match.group(1))
                    latency_val = float(latency_match.group(1))
                    self.assertGreater(time_val, 0, "NPU Processing Time must be a positive number.")
                    self.assertGreater(latency_val, 0, "Latency Average must be a positive number.")
                except ValueError:
                    self.fail("Could not parse time or latency values as numbers.")


if __name__ == '__main__':
    unittest.main(verbosity=2)

