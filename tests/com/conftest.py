import pathlib
import pytest
import yaml
import os
import shlex
import subprocess


@pytest.fixture(scope="session")
def config():
    """configs/cfg_com.yaml 로드"""

    path = pathlib.Path("configs/cfg_com.yaml")

    if not path.is_file():
        pytest.fail(f"설정 파일 '{path}' 없음")

    return yaml.safe_load(path.read_text(encoding="utf-8"))


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

