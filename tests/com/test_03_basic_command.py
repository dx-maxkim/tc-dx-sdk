import subprocess
import pytest
import os
import shutil
from pathlib import Path


@pytest.mark.timeout(60*30) # 30 min timeout for this test
@pytest.mark.smoke
@pytest.mark.normal
@pytest.mark.stress
def test_com_basic_command(com_base_path, config, run_cmd):
    """
    dx_com 의 기본 명령어로 compile 이 잘 동작하는지 확인
    - Pass: 정상적으로 dxnn 파일 생성됨
    - Fail: 동작이 되지 않음
    """
    # YAML 파일에서 설정 정보를 불러옵니다.
    cfg = config['basic_cmd']
    cmd_list = [ cfg.get('cmd1'), cfg.get('cmd2'), cfg.get('cmd3') ]
    out_list = [ cfg.get('out1'), cfg.get('out2'), cfg.get('out3') ]
    timeout_sec = cfg.get('timeout')

    # 실행 전 output 파일들 있을경우 삭제
    for outfile in out_list:
        out_path = Path(f"{com_base_path}/dx_com") / outfile
        if out_path.exists():
            out_path.unlink()
            print(f"Deleted old file: {out_path}")

    for cmd, outfile in zip(cmd_list, out_list):
        # ResNet50 의 경우 compile time 이 정해진 시간안에 되는지 확인
        if Path(outfile).name == 'ResNet50-1.dxnn':
            print(f"{Path(outfile).name} compile 이 {timeout_sec} sec 안에 완료되는지 확인")
            run_cmd(cmd, cwd=f"{com_base_path}/dx_com", timeout=timeout_sec)
        else:
            run_cmd(cmd, cwd=f"{com_base_path}/dx_com")

        # 파일 생성 확인
        out_path = Path(f"{com_base_path}/dx_com") / outfile
        assert out_path.exists(), f"Output file not found: {out_path}"

        # 생성된 파일 이동
        dest_dir = Path("output/compile")
        dest_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(out_path), dest_dir / out_path.name)
        print(f"Moved {out_path} → {dest_dir/out_path.name}")


@pytest.mark.timeout(60*30) # 30 min timeout for this test
@pytest.mark.smoke
@pytest.mark.normal
@pytest.mark.stress
def test_com_basic_shrink_acommand(com_base_path, config, run_cmd):
    """
    dx_com 의 기본 명령어로 compile 이 --shrink 로 잘 동작하는지 확인
    - Pass: 정상적으로 dxnn 파일이 생성되며 shrink 옵션이 없을때와 파일 사이즈 차이 20% 이상 확인 확인
    - Fail: 동작이 되지 않음
    """
    # YAML 파일에서 설정 정보를 불러옵니다.
    cfg = config['basic_cmd']
    cmd_list = [ cfg.get('cmd1'), cfg.get('cmd2'), cfg.get('cmd3') ]
    out_list = [ cfg.get('out1'), cfg.get('out2'), cfg.get('out3') ]

    # 실행 전 output 파일들 있을경우 삭제
    for outfile in out_list:
        out_path = Path(f"{com_base_path}/dx_com") / outfile
        if out_path.exists():
            out_path.unlink()
            print(f"Deleted old file: {out_path}")

    for cmd, outfile in zip(cmd_list, out_list):
        cmd_str = f"{cmd} --shrink"
        run_cmd(cmd_str, cwd=f"{com_base_path}/dx_com")

        # 파일 생성 확인
        out_path = Path(f"{com_base_path}/dx_com") / outfile
        assert out_path.exists(), f"Output file not found: {out_path}"

        # 생성된 파일 이동
        dest_dir = Path("output/compile_shrink")
        dest_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(out_path), dest_dir / out_path.name)
        print(f"Moved {out_path} → {dest_dir/out_path.name}")

    # shrink 옵션의 결과물 dxnn file size 20% 이상 작은지 검증
    # 비교할 파일 리스트 (상대경로 기준)
    file_pairs = [
        (f"output/compile/{Path(out_list[0]).name}", f"output/compile_shrink/{Path(out_list[0]).name}"),
        (f"output/compile/{Path(out_list[1]).name}", f"output/compile_shrink/{Path(out_list[1]).name}"),
        (f"output/compile/{Path(out_list[2]).name}", f"output/compile_shrink/{Path(out_list[2]).name}"),
    ]
    SHRINK_RATIO_MAX = 0.8  # shrink_size <= 80% * base_size

    errors = []
    for base_path, shrink_path in file_pairs:
        base = Path(base_path)
        shrink = Path(shrink_path)

        assert base.exists(), f"Base file not found: {base}"
        assert shrink.exists(), f"Shrink file not found: {shrink}"

        base_sz = base.stat().st_size
        shrink_sz = shrink.stat().st_size
        ratio = shrink_sz / base_sz if base_sz > 0 else 1.0

        if ratio > SHRINK_RATIO_MAX:
            errors.append(
                f"[FAIL] {shrink_rel}: shrink too big "
                f"(base={base_sz}, shrink={shrink_sz}, ratio={ratio:.2f} > {SHRINK_RATIO_MAX})"
            )
        else:
            print(f"[Success] <{base.name}> vs <{shrink.name}>")
            print(f"         : base={base_sz}, shrink={shrink_sz}, ratio={ratio:.2f} < {SHRINK_RATIO_MAX}")

    if errors:
        pytest.fail("\n".join(errors))
