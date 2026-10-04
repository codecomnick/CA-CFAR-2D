import os

import pytest

from cfar_test_support import build_cfar_library


@pytest.fixture(scope="session")
def c_detector(tmp_path_factory):
    output_dir = tmp_path_factory.mktemp("cfar-library")
    return build_cfar_library(output_dir, compiler=os.environ.get("CC", "cc"))
