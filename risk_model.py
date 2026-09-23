"""Frozen All Features logistic model from notebook/modeling.ipynb.

Inputs use the same units and 0/1 coding as data/train.csv. The constants
come from fitting the original pipeline on the full 168-row training set.
"""

from math import exp, isfinite
from typing import Mapping


# name: (standardized coefficient, training mean, StandardScaler scale)
FEATURES = {
    "T Kt/v": (-0.6053297694879076, 1.9803125, 0.6059132594490655),
    "Diabetes": (0.320411358505696, 0.22023809523809523, 0.41440713874641555),
    "cTnT": (0.3970488530082909, 0.07486746987951808, 0.08175417145092402),
    "GA": (0.15273586812289178, 13.957228915662649, 2.903370706631556),
    "ALB": (-0.347674557965608, 34.892857142857146, 5.1466999531897395),
    "P": (-0.6264291409204671, 1.7905952380952384, 0.4927530802263567),
    "A2MG": (0.586521659533906, 366.2558333333334, 3326.53743044322),
    "APOB": (1.1633630114019609, 6.007261904761904, 20.374457214575035),
}
INTERCEPT = -0.3960347278661987


def predict_probability(values: Mapping[str, float | None]) -> float:
    """Return P(Endpoint=1) from raw measurements.

    A missing value (None) receives the original pipeline's training mean.
    """
    logit = INTERCEPT
    for name, (coefficient, mean, scale) in FEATURES.items():
        if name not in values:
            raise ValueError(f"Missing feature: {name}")
        value = mean if values[name] is None else float(values[name])
        if not isfinite(value):
            raise ValueError(f"{name} must be a finite number")
        if name == "Diabetes" and value not in (0.0, 1.0):
            raise ValueError("Diabetes must be coded 0 or 1")
        logit += coefficient * ((value - mean) / scale)

    # Stable sigmoid for extreme inputs.
    if logit >= 0:
        return 1.0 / (1.0 + exp(-logit))
    positive = exp(logit)
    return positive / (1.0 + positive)
