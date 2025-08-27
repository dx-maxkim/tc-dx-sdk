import pytest
import re
import time
import subprocess
import shlex


@pytest.mark.smoke
@pytest.mark.normal
@pytest.mark.stress
def test_runmodel_bound_single(all_suite_path, config, run_cmd):
    """
    run_model 에서 bound 옵션을 사용해서 모델을 device 별로 할당해 동작 확인
    - Pass: 각 option 별 NPU device 별로 할당되어 동작
    - Fail: 동작을 안하거나 NPU device 별로 할당되어 동작 안할 경우
    """

    # 정규표현식 패턴: 'Core #:0'과 'Util:' 문자열 사이의 숫자([\d.]+)를 찾습니다.
    match_0 = re.compile(r"0\D+til:\D+([\d\.]+)%", re.I)
    match_1 = re.compile(r"1\D+til:\D+([\d\.]+)%", re.I)
    match_2 = re.compile(r"2\D+til:\D+([\d\.]+)%", re.I)

    # NPU bounding
    # 0: NPU_ALL
    # 1: NPU_0
    # 2: NPU_1
    # 3: NPU_2
    # 4: NPU_0/1
    # 5: NPU_1/2
    # 6: NPU_0/2
    options = 7
    for opt in range(options):
        model_path = f"{all_suite_path}/{config('rt')['runmodel_benchmark']['default_model_path']}"
        run_model_cmd = shlex.split(f"run_model -m {model_path} -t 3 -n {opt}")
        dxtop_cmd = ['dxtop']

        # 성능 측정을 위한 dxtop 실행
        p_dxtop = subprocess.Popen(dxtop_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         text=True, encoding="utf-8")

        p_runmodel = subprocess.Popen(run_model_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         text=True, encoding="utf-8")

        deadline = time.time() + 6 # 6초간 성능 측정
        util_core_0 = util_core_1 = util_core_2 = None
        try:
            line_n = 0
            for line in p_dxtop.stdout:
                if time.time() > deadline:
                    break
                line = re.sub(r"\x1B\[[0-9;?]*[ -/]*[@-~]", "", line).replace("\r", " ").replace("\u00A0"," ").replace("\u202F"," ").replace("\u2009"," ")
                util_core_0 = match_0.search(line)
                util_core_1 = match_1.search(line)
                util_core_2 = match_2.search(line)

                # 매칭된 결과가 있는지 확인합니다. 없으면 테스트는 실패합니다.
                if util_core_0 and util_core_1 and util_core_2:
                    u0 = float(util_core_0.group(1))
                    u1 = float(util_core_1.group(1))
                    u2 = float(util_core_2.group(1))
                    print(f"Core_0: {u0}, Core_1: {u1}. Core_2: {u2}, Opt: {opt}")
                    if u0 == 0.0 and u1 == 0.0 and u2 == 0.0:
                        continue
                    if opt == 0:
                        assert u0 > 0 and u1 > 0 and u2 > 0, f"Unexpected Core_0: {u0}, Core_1: {u1}. Core_2: {u2} with option: {opt}"
                    elif opt == 1:
                        assert u0 > 0 and u1 == 0 and u2 == 0, f"Unexpected Core_0: {u0}, Core_1: {u1}. Core_2: {u2} with option: {opt}"
                    elif opt == 2:
                        assert u0 == 0 and u1 > 0 and u2 == 0, f"Unexpected Core_0: {u0}, Core_1: {u1}. Core_2: {u2} with option: {opt}"
                    elif opt == 3:
                        assert u0 == 0 and u1 == 0 and u2 > 0, f"Unexpected Core_0: {u0}, Core_1: {u1}. Core_2: {u2} with option: {opt}"
                    elif opt == 4:
                        assert u0 > 0 and u1 > 0 and u2 == 0, f"Unexpected Core_0: {u0}, Core_1: {u1}. Core_2: {u2} with option: {opt}"
                    elif opt == 5:
                        assert u0 == 0 and u1 > 0 and u2 > 0, f"Unexpected Core_0: {u0}, Core_1: {u1}. Core_2: {u2} with option: {opt}"
                    elif opt == 6:
                        assert u0 > 0 and u1 == 0 and u2 > 0, f"Unexpected Core_0: {u0}, Core_1: {u1}. Core_2: {u2} with option: {opt}"


        finally:
            p_dxtop.terminate()
            try:
                p_dxtop.wait(timeout=1)
                p_runmodel.wait(timeout=5)
            except subprocess.TimeoutExpired:
                p_dxtop.kill()


@pytest.mark.smoke
@pytest.mark.normal
@pytest.mark.stress
def test_runmodel_bound_double(all_suite_path, config, run_cmd):
    """
    run_model 에서 bound 옵션을 사용해서 두개의 모델을 device 별로 할당해 동작 확인
    - Pass: 각 NPU device 별로 할당되어 동작
    - Fail: 동작을 안하거나 NPU device 별로 할당되어 동작 안할 경우
    """

    # 정규표현식 패턴: 'Core #:0'과 'Util:' 문자열 사이의 숫자([\d.]+)를 찾습니다.
    match_0 = re.compile(r"0\D+til:\D+([\d\.]+)%", re.I)
    match_1 = re.compile(r"1\D+til:\D+([\d\.]+)%", re.I)
    match_2 = re.compile(r"2\D+til:\D+([\d\.]+)%", re.I)

    # NPU bounding options
    # 0: NPU_ALL
    # 1: NPU_0
    # 2: NPU_1
    # 3: NPU_2
    opt_list = [
        (1, 2),
        (2, 3),
        (3, 1)
    ]
    for opt1, opt2 in opt_list:
        model_path = f"{all_suite_path}/{config('rt')['runmodel_benchmark']['default_model_path']}"
        run_model_cmd1 = shlex.split(f"run_model -m {model_path} -t 3 -n {opt1}")
        print(run_model_cmd1)
        run_model_cmd2 = shlex.split(f"run_model -m {model_path} -t 3 -n {opt2}")
        dxtop_cmd = ['dxtop']

        # 성능 측정을 위한 dxtop 실행
        p_dxtop = subprocess.Popen(dxtop_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         text=True, encoding="utf-8")

        p_runmodel1 = subprocess.Popen(run_model_cmd1, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         text=True, encoding="utf-8")
        p_runmodel2 = subprocess.Popen(run_model_cmd2, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         text=True, encoding="utf-8")

        deadline = time.time() + 6 # 6초간 성능 측정
        util_core_0 = util_core_1 = util_core_2 = None
        try:
            line_n = 0
            for line in p_dxtop.stdout:
                if time.time() > deadline:
                    break
                line = re.sub(r"\x1B\[[0-9;?]*[ -/]*[@-~]", "", line).replace("\r", " ").replace("\u00A0"," ").replace("\u202F"," ").replace("\u2009"," ")
                util_core_0 = match_0.search(line)
                util_core_1 = match_1.search(line)
                util_core_2 = match_2.search(line)

                # 매칭된 결과가 있는지 확인합니다. 없으면 테스트는 실패합니다.
                if util_core_0 and util_core_1 and util_core_2:
                    u0 = float(util_core_0.group(1))
                    u1 = float(util_core_1.group(1))
                    u2 = float(util_core_2.group(1))
                    print(f"Core_0: {u0}, Core_1: {u1}. Core_2: {u2}, Opt: {opt1}, {opt2}")
                    if u0 == 0.0 and u1 == 0.0 and u2 == 0.0:
                        continue
                    if opt1 == 1 and opt2 == 2:
                        assert u0 > 0 and u1 > 0 and u2 == 0, f"Unexpected Core_0: {u0}, Core_1: {u1}. Core_2: {u2} with {opt1},{opt2}"
                    elif opt1 == 2 and opt2 == 3:
                        assert u0 == 0 and u1 > 0 and u2 > 0, f"Unexpected Core_0: {u0}, Core_1: {u1}. Core_2: {u2} with {opt1},{opt2}"
                    elif opt1 == 3 and opt2 == 1:
                        assert u0 > 0 and u1 == 0 and u2 > 0, f"Unexpected Core_0: {u0}, Core_1: {u1}. Core_2: {u2} with {opt1},{opt2}"

        finally:
            p_dxtop.terminate()
            try:
                p_dxtop.wait(timeout=1)
                p_runmodel1.wait(timeout=5)
                p_runmodel2.wait(timeout=5)
            except subprocess.TimeoutExpired:
                p_dxtop.kill()
