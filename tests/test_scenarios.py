from pathlib import Path

import numpy as np
import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"

SCENARIOS = (
    ("01", {(8, 10), (15, 22), (20, 5)}, {(8, 10), (15, 22), (20, 5)}),
    ("02", {(8, 10), (15, 22), (20, 5)}, {(8, 10), (15, 22), (20, 5)}),
    ("03", set(), set()),
    ("04", set(), {(15, 15)}),
    ("05", {(5, 5), (7, 20), (12, 15), (18, 8), (22, 25)},
     {(5, 5), (7, 20), (12, 15), (18, 8), (22, 25)}),
)


def load_target_coordinates(path: Path) -> set[tuple[int, int]]:
    coordinates = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row, col, _power = line.split()
            coordinates.add((int(row), int(col)))
    return coordinates


@pytest.mark.parametrize(
    ("number", "expected_detections", "described_targets"),
    SCENARIOS,
)
def test_versioned_scenario_detections(
    c_detector,
    number,
    expected_detections,
    described_targets,
):
    data = np.loadtxt(DATA_DIR / f"radar_{number}.txt", dtype=np.float64)
    target_coordinates = load_target_coordinates(
        DATA_DIR / f"radar_{number}_targets.txt"
    )

    detections = c_detector.detect(data, alpha=6.0)
    actual_detections = {
        (int(row), int(col)) for row, col in np.argwhere(detections == 1)
    }

    assert target_coordinates == described_targets
    assert actual_detections == expected_detections
