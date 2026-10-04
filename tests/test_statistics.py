from itertools import combinations, product

import numpy as np
import pytest

from statistics_support import wilson_interval


SEED = 20261004
ALPHA = 6.0
TRAINING_CELL_COUNT = 72
SAMPLED_INDICES = (4, 13, 22)
SAMPLED_CUTS = tuple(product(SAMPLED_INDICES, repeat=2))


def window_coordinates(center_row: int, center_col: int) -> set[tuple[int, int]]:
    return {
        (row, col)
        for row in range(center_row - 4, center_row + 5)
        for col in range(center_col - 4, center_col + 5)
    }


def test_sampled_windows_do_not_overlap():
    windows = [window_coordinates(row, col) for row, col in SAMPLED_CUTS]

    assert all(len(window) == 81 for window in windows)
    assert all(
        not left.intersection(right)
        for left, right in combinations(windows, 2)
    )
    assert all(
        0 <= row < 30 and 0 <= col < 30
        for window in windows
        for row, col in window
    )


@pytest.mark.statistical
def test_false_alarm_probability_matches_theory(c_detector):
    rng = np.random.default_rng(SEED)
    matrix_count = 5_000
    false_alarms = 0

    for _ in range(matrix_count):
        data = rng.exponential(scale=1.0, size=(30, 30))
        detections = c_detector.detect(data, alpha=ALPHA)
        false_alarms += sum(detections[row, col] for row, col in SAMPLED_CUTS)

    trial_count = matrix_count * len(SAMPLED_CUTS)
    observed_pfa = false_alarms / trial_count
    expected_pfa = (1.0 + ALPHA / TRAINING_CELL_COUNT) ** (-TRAINING_CELL_COUNT)
    lower, upper = wilson_interval(false_alarms, trial_count, confidence=0.99)

    print(
        "Pfa: "
        f"false_alarms={false_alarms}, trials={trial_count}, "
        f"observed={observed_pfa:.12f}, expected={expected_pfa:.12f}, "
        f"wilson99=[{lower:.12f}, {upper:.12f}]"
    )
    assert lower <= expected_pfa <= upper


@pytest.mark.statistical
def test_detection_probability_increases_with_snr(c_detector):
    rng = np.random.default_rng(SEED)
    base_maps = rng.exponential(scale=1.0, size=(1_000, 30, 30))
    snr_levels_db = (0, 5, 10, 15, 20)
    probabilities = []

    for snr_db in snr_levels_db:
        target_power = 10.0 ** (snr_db / 10.0)
        detection_count = 0

        for base_map in base_maps:
            data = base_map.copy()
            data[15, 15] += target_power
            detections = c_detector.detect(data, alpha=ALPHA)
            detection_count += detections[15, 15]

        probabilities.append(detection_count / len(base_maps))

    print(
        "Pd: "
        + ", ".join(
            f"{snr_db}dB={probability:.6f}"
            for snr_db, probability in zip(snr_levels_db, probabilities)
        )
    )
    assert all(
        higher >= lower
        for lower, higher in zip(probabilities, probabilities[1:])
    )
    assert probabilities[snr_levels_db.index(15)] >= 0.95
