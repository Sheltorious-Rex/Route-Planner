# Route-Planner

A freight truck route metrics calculator that calculates time slot estimates and driver activity schedules.

## Features

- Calculate route metrics for freight truck hauling
- Generate driver activity schedules with time slots
- Account for driving hours regulations (Hours of Service)
- Handle deadhead (empty) miles vs loaded miles

## Installation

```bash
pip install -e .
```

For development:
```bash
pip install -e ".[dev]"
```

## Usage

### Command Line Interface

```bash
# Basic usage with positional arguments
route-planner <total_miles> <deadhead_miles> <remaining_hours>

# Example: 500-mile route with 50 deadhead miles and 8 remaining hours
route-planner 500 50 8

# Using named arguments
route-planner --total-miles 1000 --deadhead 100 --remaining-hours 5
```

### Python API

```python
from route_planner import RouteMetricsCalculator

calculator = RouteMetricsCalculator()
metrics = calculator.calculate(
    total_miles=500,
    deadhead_miles=50,
    remaining_hours=8,
)

# Print the formatted table
print(metrics.to_table())

# Access individual metrics
print(f"Total driving time: {metrics.total_driving_time} hours")
print(f"Total break time: {metrics.total_break_time} hours")
```

## Parameters

- **total_miles**: Total miles for the route
- **deadhead_miles**: Empty miles (driving without cargo)
- **remaining_hours**: Hours remaining in the current driving window (0-11)

## Constraints

The calculator uses the following trucking industry constraints:

- **Average driving speed**: 55 mph
- **Maximum driving time**: 11 hours before a mandatory break
- **Break duration**: 10 hours
- **Loading time**: 1.5 hours
- **Unloading time**: 1.5 hours

## Example Output

```
=====================================================================================
ROUTE METRICS SUMMARY
=====================================================================================
Total Miles:           500.0 miles
Deadhead Miles:        50.0 miles
Loaded Miles:          450.0 miles
Total Driving Time:    09:05 (9.09 hours)
Total Break Time:      10:00 (10.00 hours)
Load/Unload Time:      03:00 (3.00 hours)
Total Route Time:      22:05 (22.09 hours)

=====================================================================================
DRIVER ACTIVITY SCHEDULE
=====================================================================================
#    Activity             Start Time   End Time     Duration     Miles      Notes
-------------------------------------------------------------------------------------
1    Loading              00:00        01:30        01:30        0.0        Loading cargo at origin
2    Driving              01:30        09:30        08:00        440.0      Deadhead + Loaded
3    Break (10-hour rest) 09:30        19:30        10:00        0.0        Mandatory 10-hour rest
4    Driving              19:30        20:35        01:05        60.0       Loaded haul
5    Unloading            20:35        22:05        01:30        0.0        Unloading cargo at destination
=====================================================================================
```

## Running Tests

```bash
pytest tests/ -v
```

## License

MIT
