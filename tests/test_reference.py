import numpy as np
import pytest

from reference_cfar import ca_cfar_2d_reference


INNER = (slice(4, 26), slice(4, 26))


def test_reference_rejects_wrong_shape():
    with pytest.raises(ValueError, match="30 x 30"):
        ca_cfar_2d_reference(np.zeros((29, 30), dtype=np.float64), alpha=6.0)


def test_reference_has_72_training_cells():
    data = np.zeros((30, 30), dtype=np.float64)
    data[11, 11] = 72.0

    result = ca_cfar_2d_reference(data, alpha=6.0)

    assert result.noise_estimate[15, 15] == 1.0
    assert result.threshold[15, 15] == 6.0


def test_c_matches_reference_for_exact_threshold_cases(c_detector):
    data = np.ones((30, 30), dtype=np.float64)
    data[15, 15] = 6.0

    oracle = ca_cfar_2d_reference(data, alpha=6.0)
    c_result = c_detector.detect(data, alpha=6.0)

    assert not oracle.detections[15, 15]
    assert c_result[15, 15] == 0

    data[15, 15] = np.nextafter(6.0, np.inf)
    oracle = ca_cfar_2d_reference(data, alpha=6.0)
    c_result = c_detector.detect(data, alpha=6.0)

    assert oracle.detections[15, 15]
    assert c_result[15, 15] == 1


def test_c_matches_reference_for_seeded_random_maps(c_detector):
    rng = np.random.default_rng(20261004)

    for _ in range(20):
        data = rng.exponential(scale=1.0, size=(30, 30))
        oracle = ca_cfar_2d_reference(data, alpha=6.0)
        c_result = c_detector.detect(data, alpha=6.0)

        np.testing.assert_array_equal(
            c_result[INNER].astype(bool),
            oracle.detections[INNER],
        )


def test_c_and_reference_leave_border_clear(c_detector):
    data = np.ones((30, 30), dtype=np.float64)
    data[:4, :] = 1e9
    data[-4:, :] = 1e9
    data[:, :4] = 1e9
    data[:, -4:] = 1e9

    oracle = ca_cfar_2d_reference(data, alpha=6.0)
    c_result = c_detector.detect(data, alpha=6.0)

    border_mask = np.ones((30, 30), dtype=bool)
    border_mask[INNER] = False
    assert not oracle.detections[border_mask].any()
    assert not c_result[border_mask].any()
