import os
import subprocess
from pathlib import Path

import pytest

from cfar_test_support import build_cfar_library


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def c_detector(tmp_path_factory):
    output_dir = tmp_path_factory.mktemp("cfar-library")
    return build_cfar_library(output_dir, compiler=os.environ.get("CC", "cc"))


@pytest.fixture(scope="session")
def cfar_executable(tmp_path_factory):
    output_dir = tmp_path_factory.mktemp("cfar-executable")
    executable = output_dir / "cfar"
    subprocess.run(
        [
            os.environ.get("CC", "cc"),
            "-std=c11",
            "-Wall",
            "-Wextra",
            "-Wpedantic",
            "-Werror",
            str(PROJECT_ROOT / "src" / "main.c"),
            str(PROJECT_ROOT / "src" / "cfar.c"),
            "-o",
            str(executable),
        ],
        cwd=PROJECT_ROOT,
        check=True,
    )
    return executable
