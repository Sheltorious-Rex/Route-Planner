"""Tests for the Route Metrics Calculator."""

import pytest

from route_planner.calculator import (
    Activity,
    ActivityType,
    RouteMetrics,
    RouteMetricsCalculator,
)


class TestRouteMetricsCalculator:
    """Test cases for RouteMetricsCalculator."""

    def test_simple_route_no_break_needed(self):
        """Test a short route that doesn't require a break."""
        calculator = RouteMetricsCalculator()
        metrics = calculator.calculate(
            total_miles=300,
            deadhead_miles=50,
            remaining_hours=11,
        )

        assert metrics.total_miles == 300
        assert metrics.deadhead_miles == 50
        assert metrics.loaded_miles == 250
        # 300 miles / 55 mph ≈ 5.45 hours driving
        assert abs(metrics.total_driving_time - (300 / 55)) < 0.01
        assert metrics.total_break_time == 0
        assert metrics.total_load_unload_time == 3.0  # 1.5 + 1.5

    def test_route_requires_one_break(self):
        """Test a route that requires exactly one break."""
        calculator = RouteMetricsCalculator()
        # 700 miles at 55 mph = 12.73 hours > 11 hours, needs 1 break
        metrics = calculator.calculate(
            total_miles=700,
            deadhead_miles=100,
            remaining_hours=11,
        )

        assert metrics.total_miles == 700
        assert metrics.total_break_time == 10  # One 10-hour break
        
        # Check activities include a break
        break_activities = [a for a in metrics.activities if a.activity_type == ActivityType.BREAK]
        assert len(break_activities) == 1

    def test_route_requires_multiple_breaks(self):
        """Test a long route that requires multiple breaks."""
        calculator = RouteMetricsCalculator()
        # 1500 miles at 55 mph = 27.27 hours, needs multiple breaks
        metrics = calculator.calculate(
            total_miles=1500,
            deadhead_miles=200,
            remaining_hours=11,
        )

        assert metrics.total_miles == 1500
        assert metrics.total_break_time >= 20  # At least two 10-hour breaks
        
        break_activities = [a for a in metrics.activities if a.activity_type == ActivityType.BREAK]
        assert len(break_activities) >= 2

    def test_remaining_hours_affects_first_break(self):
        """Test that remaining hours affects when first break occurs."""
        calculator = RouteMetricsCalculator()
        
        # With only 5 remaining hours, break should come sooner
        metrics = calculator.calculate(
            total_miles=700,
            deadhead_miles=0,
            remaining_hours=5,
        )
        
        # First driving segment should be 5 hours max
        driving_activities = [a for a in metrics.activities if a.activity_type == ActivityType.DRIVING]
        assert driving_activities[0].duration <= 5.0

    def test_zero_deadhead_miles(self):
        """Test route with no deadhead miles."""
        calculator = RouteMetricsCalculator()
        metrics = calculator.calculate(
            total_miles=300,
            deadhead_miles=0,
            remaining_hours=11,
        )

        assert metrics.deadhead_miles == 0
        assert metrics.loaded_miles == 300

    def test_all_deadhead_miles(self):
        """Test route that is entirely deadhead."""
        calculator = RouteMetricsCalculator()
        metrics = calculator.calculate(
            total_miles=300,
            deadhead_miles=300,
            remaining_hours=11,
        )

        assert metrics.deadhead_miles == 300
        assert metrics.loaded_miles == 0

    def test_zero_miles_route(self):
        """Test edge case of zero miles."""
        calculator = RouteMetricsCalculator()
        metrics = calculator.calculate(
            total_miles=0,
            deadhead_miles=0,
            remaining_hours=11,
        )

        assert metrics.total_miles == 0
        assert metrics.total_driving_time == 0
        # Still has loading and unloading
        assert metrics.total_load_unload_time == 3.0

    def test_invalid_negative_miles(self):
        """Test that negative miles raises an error."""
        calculator = RouteMetricsCalculator()
        with pytest.raises(ValueError, match="Total miles cannot be negative"):
            calculator.calculate(total_miles=-100, deadhead_miles=0, remaining_hours=11)

    def test_invalid_deadhead_exceeds_total(self):
        """Test that deadhead > total raises an error."""
        calculator = RouteMetricsCalculator()
        with pytest.raises(ValueError, match="Deadhead miles cannot exceed total miles"):
            calculator.calculate(total_miles=100, deadhead_miles=200, remaining_hours=11)

    def test_invalid_negative_remaining_hours(self):
        """Test that negative remaining hours raises an error."""
        calculator = RouteMetricsCalculator()
        with pytest.raises(ValueError, match="Remaining hours cannot be negative"):
            calculator.calculate(total_miles=100, deadhead_miles=0, remaining_hours=-1)

    def test_invalid_remaining_hours_exceeds_max(self):
        """Test that remaining hours > max raises an error."""
        calculator = RouteMetricsCalculator()
        with pytest.raises(ValueError, match="Remaining hours cannot exceed max driving hours"):
            calculator.calculate(total_miles=100, deadhead_miles=0, remaining_hours=15)

    def test_custom_speed(self):
        """Test calculator with custom speed."""
        calculator = RouteMetricsCalculator(speed_mph=60)
        metrics = calculator.calculate(
            total_miles=300,
            deadhead_miles=0,
            remaining_hours=11,
        )
        
        # 300 miles at 60 mph = 5 hours
        assert abs(metrics.total_driving_time - 5.0) < 0.01

    def test_activity_schedule_structure(self):
        """Test that activity schedule has correct structure."""
        calculator = RouteMetricsCalculator()
        metrics = calculator.calculate(
            total_miles=300,
            deadhead_miles=50,
            remaining_hours=11,
        )

        # Should start with loading
        assert metrics.activities[0].activity_type == ActivityType.LOADING
        # Should end with unloading
        assert metrics.activities[-1].activity_type == ActivityType.UNLOADING
        # All activities should have non-negative times
        for activity in metrics.activities:
            assert activity.start_time >= 0
            assert activity.duration >= 0

    def test_activity_times_are_sequential(self):
        """Test that activities don't overlap and are in sequence."""
        calculator = RouteMetricsCalculator()
        metrics = calculator.calculate(
            total_miles=700,
            deadhead_miles=100,
            remaining_hours=11,
        )

        for i in range(len(metrics.activities) - 1):
            current = metrics.activities[i]
            next_activity = metrics.activities[i + 1]
            # End time of current should equal start time of next
            assert abs(current.end_time - next_activity.start_time) < 0.001


class TestRouteMetrics:
    """Test cases for RouteMetrics data class."""

    def test_format_time(self):
        """Test time formatting."""
        metrics = RouteMetrics(
            total_miles=0,
            deadhead_miles=0,
            loaded_miles=0,
            total_driving_time=0,
            total_break_time=0,
            total_load_unload_time=0,
            total_time=0,
            activities=[],
        )
        
        assert metrics.format_time(0) == "00:00"
        assert metrics.format_time(1.5) == "01:30"
        assert metrics.format_time(10.75) == "10:45"
        assert metrics.format_time(24) == "24:00"

    def test_to_table_returns_string(self):
        """Test that to_table returns a non-empty string."""
        calculator = RouteMetricsCalculator()
        metrics = calculator.calculate(
            total_miles=300,
            deadhead_miles=50,
            remaining_hours=11,
        )
        
        table = metrics.to_table()
        assert isinstance(table, str)
        assert len(table) > 0
        assert "ROUTE METRICS SUMMARY" in table
        assert "DRIVER ACTIVITY SCHEDULE" in table


class TestActivity:
    """Test cases for Activity data class."""

    def test_end_time_property(self):
        """Test end_time calculation."""
        activity = Activity(
            activity_type=ActivityType.DRIVING,
            start_time=5.0,
            duration=3.5,
            miles=192.5,
        )
        
        assert activity.end_time == 8.5
