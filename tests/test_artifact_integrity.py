import subprocess
import sys
from pathlib import Path
from zipfile import ZipFile

from tools.report_scaffold_v3.package_contract import CORE_MODULES

ROOT = Path(__file__).resolve().parents[1]


def test_built_wheel_contains_core_modules(tmp_path: Path):
    dist_dir = tmp_path / "dist"
    dist_dir.mkdir()

    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "wheel",
            str(ROOT),
            "--no-deps",
            "--no-build-isolation",
            "-w",
            str(dist_dir),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    wheels = sorted(dist_dir.glob("*.whl"))
    assert len(wheels) == 1

    with ZipFile(wheels[0]) as archive:
        archive_names = set(archive.namelist())

    for spec in CORE_MODULES:
        expected_path = f"tools/report_scaffold_v3/{spec.file_name}"
        assert expected_path in archive_names
