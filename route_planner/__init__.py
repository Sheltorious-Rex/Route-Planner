"""
Route Planner - A freight truck route metrics calculator.

This tool calculates metrics for a freight truck hauling commodities,
including time slot estimates and driver activity schedules.
"""

from .calculator import RouteMetricsCalculator

__version__ = "1.0.0"
__all__ = ["RouteMetricsCalculator"]
