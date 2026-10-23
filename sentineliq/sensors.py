"""Validation and deterministic fault analysis for asset sensor readings."""

from __future__ import annotations

import math
from dataclasses import dataclass


LIMITS = {
    "temperature_c": (-40.0, 180.0),
    "vibration_mm_s": (0.0, 50.0),
    "pressure_kpa": (0.0, 2_000.0),
}


@dataclass(frozen=True)
class SensorReport:
    valid: bool
    errors: tuple[str, ...]
    warnings: tuple[str, ...]
    fault_hypotheses: tuple[str, ...]


def validate_and_analyze(readings: dict[str, float | int | None]) -> SensorReport:
    errors: list[str] = []
    warnings: list[str] = []
    faults: list[str] = []

    for name, (minimum, maximum) in LIMITS.items():
        value = readings.get(name)
        if value is None:
            errors.append(f"missing:{name}")
            continue
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            errors.append(f"invalid:{name}")
            continue
        if value < minimum or value > maximum:
            errors.append(f"out_of_range:{name}")

    vibration = readings.get("vibration_mm_s")
    temperature = readings.get("temperature_c")
    pressure = readings.get("pressure_kpa")
    if isinstance(vibration, (int, float)) and vibration >= 7.1:
        warnings.append("high:vibration_mm_s")
        faults.append("possible bearing or rotor imbalance")
    if isinstance(temperature, (int, float)) and temperature >= 85:
        warnings.append("high:temperature_c")
        faults.append("possible cooling problem or excessive load")
    if isinstance(pressure, (int, float)) and pressure <= 100:
        warnings.append("low:pressure_kpa")
        faults.append("possible leak or insufficient supply pressure")

    return SensorReport(not errors, tuple(errors), tuple(warnings), tuple(dict.fromkeys(faults)))
