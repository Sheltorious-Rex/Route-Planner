"""
Route Metrics Calculator Module.

Calculates time slot estimates and driver activity schedules for freight truck routes.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List


class ActivityType(Enum):
    """Types of driver activities."""
    LOADING = "Loading"
    DRIVING = "Driving"
    BREAK = "Break (10-hour rest)"
    UNLOADING = "Unloading"


@dataclass
class Activity:
    """Represents a single activity in the route schedule."""
    activity_type: ActivityType
    start_time: float  # Hours from start
    duration: float  # Hours
    miles: float  # Miles covered (0 for non-driving activities)
    notes: str = ""

    @property
    def end_time(self) -> float:
        """Calculate end time of activity."""
        return self.start_time + self.duration


@dataclass
class RouteMetrics:
    """Contains calculated route metrics and schedule."""
    total_miles: float
    deadhead_miles: float
    loaded_miles: float
    total_driving_time: float  # Hours
    total_break_time: float  # Hours
    total_load_unload_time: float  # Hours
    total_time: float  # Hours
    activities: List[Activity]

    def format_time(self, hours: float) -> str:
        """Format hours as HH:MM string."""
        total_minutes = int(hours * 60)
        hrs = total_minutes // 60
        mins = total_minutes % 60
        return f"{hrs:02d}:{mins:02d}"

    def to_table(self) -> str:
        """Generate a formatted table of the route schedule."""
        lines = []
        lines.append("=" * 85)
        lines.append("ROUTE METRICS SUMMARY")
        lines.append("=" * 85)
        lines.append(f"Total Miles:           {self.total_miles:.1f} miles")
        lines.append(f"Deadhead Miles:        {self.deadhead_miles:.1f} miles")
        lines.append(f"Loaded Miles:          {self.loaded_miles:.1f} miles")
        lines.append(f"Total Driving Time:    {self.format_time(self.total_driving_time)} ({self.total_driving_time:.2f} hours)")
        lines.append(f"Total Break Time:      {self.format_time(self.total_break_time)} ({self.total_break_time:.2f} hours)")
        lines.append(f"Load/Unload Time:      {self.format_time(self.total_load_unload_time)} ({self.total_load_unload_time:.2f} hours)")
        lines.append(f"Total Route Time:      {self.format_time(self.total_time)} ({self.total_time:.2f} hours)")
        lines.append("")
        lines.append("=" * 85)
        lines.append("DRIVER ACTIVITY SCHEDULE")
        lines.append("=" * 85)
        lines.append(f"{'#':<4} {'Activity':<20} {'Start Time':<12} {'End Time':<12} {'Duration':<12} {'Miles':<10} {'Notes'}")
        lines.append("-" * 85)

        for i, activity in enumerate(self.activities, 1):
            lines.append(
                f"{i:<4} {activity.activity_type.value:<20} "
                f"{self.format_time(activity.start_time):<12} "
                f"{self.format_time(activity.end_time):<12} "
                f"{self.format_time(activity.duration):<12} "
                f"{activity.miles:<10.1f} "
                f"{activity.notes}"
            )

        lines.append("=" * 85)
        return "\n".join(lines)


class RouteMetricsCalculator:
    """
    Calculator for freight truck route metrics.
    
    Calculates time slot estimates and driver activity schedules based on:
    - Average speed of 55 mph
    - Maximum 11 hours of driving before a mandatory 10-hour break
    - 3 hours total for loading and unloading (1.5 hours each)
    """

    DEFAULT_SPEED_MPH = 55
    MAX_DRIVING_HOURS = 11
    BREAK_DURATION_HOURS = 10
    LOADING_DURATION_HOURS = 1.5
    UNLOADING_DURATION_HOURS = 1.5

    def __init__(
        self,
        speed_mph: float = DEFAULT_SPEED_MPH,
        max_driving_hours: float = MAX_DRIVING_HOURS,
        break_duration: float = BREAK_DURATION_HOURS,
        loading_duration: float = LOADING_DURATION_HOURS,
        unloading_duration: float = UNLOADING_DURATION_HOURS,
    ):
        """
        Initialize the calculator with configurable parameters.
        
        Args:
            speed_mph: Average driving speed in miles per hour (default: 55)
            max_driving_hours: Maximum hours of driving before a break (default: 11)
            break_duration: Duration of mandatory break in hours (default: 10)
            loading_duration: Time for loading cargo in hours (default: 1.5)
            unloading_duration: Time for unloading cargo in hours (default: 1.5)
        """
        self.speed_mph = speed_mph
        self.max_driving_hours = max_driving_hours
        self.break_duration = break_duration
        self.loading_duration = loading_duration
        self.unloading_duration = unloading_duration

    def calculate(
        self,
        total_miles: float,
        deadhead_miles: float,
        remaining_hours: float,
    ) -> RouteMetrics:
        """
        Calculate route metrics and generate activity schedule.
        
        Args:
            total_miles: Total miles for the route
            deadhead_miles: Empty miles (no load)
            remaining_hours: Hours remaining in current driving window
            
        Returns:
            RouteMetrics object with calculated metrics and schedule
        """
        if total_miles < 0:
            raise ValueError("Total miles cannot be negative")
        if deadhead_miles < 0:
            raise ValueError("Deadhead miles cannot be negative")
        if deadhead_miles > total_miles:
            raise ValueError("Deadhead miles cannot exceed total miles")
        if remaining_hours < 0:
            raise ValueError("Remaining hours cannot be negative")
        if remaining_hours > self.max_driving_hours:
            raise ValueError(f"Remaining hours cannot exceed max driving hours ({self.max_driving_hours})")

        loaded_miles = total_miles - deadhead_miles
        activities: List[Activity] = []
        current_time = 0.0
        miles_driven = 0.0
        hours_until_break = remaining_hours
        total_driving_time = 0.0
        total_break_time = 0.0

        # Start with loading (assumes we start at the pickup location)
        activities.append(Activity(
            activity_type=ActivityType.LOADING,
            start_time=current_time,
            duration=self.loading_duration,
            miles=0,
            notes="Loading cargo at origin"
        ))
        current_time += self.loading_duration

        # Calculate driving schedule
        miles_remaining = total_miles

        while miles_remaining > 0:
            # Calculate how far we can drive before needing a break
            max_miles_before_break = hours_until_break * self.speed_mph
            miles_this_segment = min(miles_remaining, max_miles_before_break)
            segment_duration = miles_this_segment / self.speed_mph

            # Determine if this segment is deadhead or loaded
            if miles_driven < deadhead_miles:
                # Still in deadhead portion
                deadhead_remaining = deadhead_miles - miles_driven
                if miles_this_segment <= deadhead_remaining:
                    segment_note = "Deadhead (empty)"
                else:
                    segment_note = "Deadhead + Loaded"
            else:
                segment_note = "Loaded haul"

            activities.append(Activity(
                activity_type=ActivityType.DRIVING,
                start_time=current_time,
                duration=segment_duration,
                miles=miles_this_segment,
                notes=segment_note
            ))

            current_time += segment_duration
            miles_driven += miles_this_segment
            miles_remaining -= miles_this_segment
            total_driving_time += segment_duration
            hours_until_break -= segment_duration

            # If we need a break and there's still miles to drive
            if hours_until_break <= 0 and miles_remaining > 0:
                activities.append(Activity(
                    activity_type=ActivityType.BREAK,
                    start_time=current_time,
                    duration=self.break_duration,
                    miles=0,
                    notes="Mandatory 10-hour rest"
                ))
                current_time += self.break_duration
                total_break_time += self.break_duration
                hours_until_break = self.max_driving_hours

        # End with unloading
        activities.append(Activity(
            activity_type=ActivityType.UNLOADING,
            start_time=current_time,
            duration=self.unloading_duration,
            miles=0,
            notes="Unloading cargo at destination"
        ))
        current_time += self.unloading_duration

        total_load_unload_time = self.loading_duration + self.unloading_duration

        return RouteMetrics(
            total_miles=total_miles,
            deadhead_miles=deadhead_miles,
            loaded_miles=loaded_miles,
            total_driving_time=total_driving_time,
            total_break_time=total_break_time,
            total_load_unload_time=total_load_unload_time,
            total_time=current_time,
            activities=activities,
        )
