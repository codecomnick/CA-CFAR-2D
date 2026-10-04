from math import sqrt
from statistics import NormalDist


def wilson_interval(
    successes: int,
    trials: int,
    confidence: float,
) -> tuple[float, float]:
    if trials <= 0:
        raise ValueError("trials must be positive")
    if successes < 0 or successes > trials:
        raise ValueError("successes must be between zero and trials")
    if confidence <= 0.0 or confidence >= 1.0:
        raise ValueError("confidence must be between zero and one")

    probability = successes / trials
    z_score = NormalDist().inv_cdf(0.5 + confidence / 2.0)
    z_squared = z_score * z_score
    denominator = 1.0 + z_squared / trials
    center = (probability + z_squared / (2.0 * trials)) / denominator
    margin = (
        z_score
        / denominator
        * sqrt(
            probability * (1.0 - probability) / trials
            + z_squared / (4.0 * trials * trials)
        )
    )
    return center - margin, center + margin
