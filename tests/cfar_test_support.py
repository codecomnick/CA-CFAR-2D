import ctypes
import platform
import subprocess
from pathlib import Path

import numpy as np


ROWS = 30
COLS = 30
PROJECT_ROOT = Path(__file__).resolve().parents[1]


class CfarCLibrary:
    def __init__(self, library_path: Path):
        self._library = ctypes.CDLL(str(library_path))
        self._cfar_2d = self._library.cfar_2d
        self._cfar_2d.argtypes = (
            ctypes.POINTER(ctypes.c_double),
            ctypes.POINTER(ctypes.c_int),
            ctypes.c_double,
        )
        self._cfar_2d.restype = None

    def detect(self, data: np.ndarray, alpha: float) -> np.ndarray:
        matrix = np.ascontiguousarray(data, dtype=np.float64)
        if matrix.shape != (ROWS, COLS):
            raise ValueError("data must be a 30 x 30 matrix")

        detections = np.zeros((ROWS, COLS), dtype=np.int32)
        self._cfar_2d(
            matrix.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
            detections.ctypes.data_as(ctypes.POINTER(ctypes.c_int)),
            ctypes.c_double(alpha),
        )
        return detections.copy()


def build_cfar_library(output_dir: Path, compiler: str = "cc") -> CfarCLibrary:
    output_dir.mkdir(parents=True, exist_ok=True)
    system = platform.system()
    if system == "Darwin":
        library_path = output_dir / "libcfar.dylib"
        link_flags = ["-dynamiclib", "-fPIC"]
    elif system == "Linux":
        library_path = output_dir / "libcfar.so"
        link_flags = ["-shared", "-fPIC"]
    else:
        raise RuntimeError(f"unsupported test platform: {system}")

    command = [
        compiler,
        "-std=c11",
        "-Wall",
        "-Wextra",
        "-Wpedantic",
        "-Werror",
        *link_flags,
        str(PROJECT_ROOT / "src" / "cfar.c"),
        "-o",
        str(library_path),
    ]
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)
    return CfarCLibrary(library_path)
