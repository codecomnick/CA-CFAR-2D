from typing import NamedTuple

import numpy as np


ROWS = 30
COLS = 30
TRAINING_ROWS = 3
TRAINING_COLS = 3
GUARD_ROWS = 1
GUARD_COLS = 1
MARGIN_ROWS = TRAINING_ROWS + GUARD_ROWS
MARGIN_COLS = TRAINING_COLS + GUARD_COLS
TRAINING_CELL_COUNT = 72


class CfarReferenceResult(NamedTuple):
    detections: np.ndarray
    threshold: np.ndarray
    noise_estimate: np.ndarray


def ca_cfar_2d_reference(data: np.ndarray, alpha: float) -> CfarReferenceResult:
    matrix = np.asarray(data)
    if matrix.shape != (ROWS, COLS):
        raise ValueError("data must be a 30 x 30 matrix")
    if matrix.dtype != np.float64:
        raise TypeError("data must use float64 values")
    if not np.isfinite(alpha) or alpha <= 0.0:
        raise ValueError("alpha must be finite and positive")

    detections = np.zeros((ROWS, COLS), dtype=bool)
    threshold = np.zeros((ROWS, COLS), dtype=np.float64)
    noise_estimate = np.zeros((ROWS, COLS), dtype=np.float64)

    for row in range(MARGIN_ROWS, ROWS - MARGIN_ROWS):
        for col in range(MARGIN_COLS, COLS - MARGIN_COLS):
            training_sum = 0.0
            training_count = 0

            for window_row in range(row - MARGIN_ROWS, row + MARGIN_ROWS + 1):
                for window_col in range(col - MARGIN_COLS, col + MARGIN_COLS + 1):
                    in_guard_and_cut = (
                        abs(window_row - row) <= GUARD_ROWS
                        and abs(window_col - col) <= GUARD_COLS
                    )
                    if in_guard_and_cut:
                        continue

                    training_sum += matrix[window_row, window_col]
                    training_count += 1

            if training_count != TRAINING_CELL_COUNT:
                raise AssertionError("reference window must contain 72 training cells")

            noise = training_sum / TRAINING_CELL_COUNT
            cell_threshold = alpha * noise
            noise_estimate[row, col] = noise
            threshold[row, col] = cell_threshold
            detections[row, col] = matrix[row, col] > cell_threshold

    return CfarReferenceResult(detections, threshold, noise_estimate)
