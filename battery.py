"""Simple battery health calculations and simulated readings."""

import math
import random


def calculate_soh(current_capacity: float, rated_capacity: float) -> float:
    """Return State of Health as a percentage of rated capacity."""
    if not math.isfinite(current_capacity) or not math.isfinite(rated_capacity):
        raise ValueError("Capacities must be finite numbers.")
    if rated_capacity <= 0:
        raise ValueError("Rated capacity must be greater than zero.")
    if current_capacity < 0:
        raise ValueError("Current capacity cannot be negative.")
    return (current_capacity / rated_capacity) * 100


def classify_health(soh: float) -> str:
    """Classify SOH using simple project thresholds."""
    if not math.isfinite(soh) or soh < 0:
        raise ValueError("SOH must be a non-negative finite number.")
    if soh >= 80:
        return "Good"
    if soh >= 60:
        return "Fair"
    return "Degraded"


def estimate_rul(
    soh: float,
    degradation_rate_per_year: float = 2.5,
    end_of_life_soh: float = 70,
) -> float:
    """Estimate years until the assumed end-of-life SOH threshold is reached."""
    values = (soh, degradation_rate_per_year, end_of_life_soh)
    if not all(math.isfinite(value) for value in values):
        raise ValueError("SOH and life-estimate settings must be finite numbers.")
    if soh < 0 or end_of_life_soh < 0:
        raise ValueError("SOH values cannot be negative.")
    if degradation_rate_per_year <= 0:
        raise ValueError("Degradation rate must be greater than zero.")
    return max(0.0, (soh - end_of_life_soh) / degradation_rate_per_year)


def generate_simulated_reading() -> dict[str, float]:
    """Generate an illustrative reading; it is not measured from real hardware."""
    rated_capacity = 100.0
    current_capacity = round(random.uniform(58.0, 100.0), 1)
    return {
        "voltage_v": round(random.uniform(48.0, 54.0), 2),
        "current_a": round(random.uniform(5.0, 30.0), 2),
        "temperature_c": round(random.uniform(20.0, 45.0), 1),
        "rated_capacity_ah": rated_capacity,
        "current_capacity_ah": current_capacity,
    }
