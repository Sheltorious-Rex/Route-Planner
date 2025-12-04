"""
Command-line interface for the Route Planner.
"""

import argparse
import sys

from .calculator import RouteMetricsCalculator


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Calculate freight truck route metrics and driver activity schedule.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s 500 50 8
      Calculate metrics for a 500-mile route with 50 deadhead miles
      and 8 remaining hours in the current driving window.
  
  %(prog)s --total-miles 1000 --deadhead 100 --remaining-hours 5
      Calculate metrics using named arguments.

Constraints:
  - Average driving speed: 55 mph
  - Maximum driving time before break: 11 hours
  - Mandatory break duration: 10 hours
  - Loading time: 1.5 hours
  - Unloading time: 1.5 hours
"""
    )

    parser.add_argument(
        "total_miles",
        type=float,
        nargs="?",
        help="Total miles for the route"
    )
    parser.add_argument(
        "deadhead",
        type=float,
        nargs="?",
        help="Deadhead (empty) miles"
    )
    parser.add_argument(
        "remaining_hours",
        type=float,
        nargs="?",
        help="Remaining hours in current driving window (0-11)"
    )

    # Named argument alternatives
    parser.add_argument(
        "--total-miles", "-m",
        type=float,
        dest="total_miles_opt",
        help="Total miles for the route"
    )
    parser.add_argument(
        "--deadhead", "-d",
        type=float,
        dest="deadhead_opt",
        help="Deadhead (empty) miles"
    )
    parser.add_argument(
        "--remaining-hours", "-r",
        type=float,
        dest="remaining_hours_opt",
        help="Remaining hours in current driving window (0-11)"
    )

    args = parser.parse_args()

    # Resolve positional vs named arguments
    total_miles = args.total_miles if args.total_miles is not None else args.total_miles_opt
    deadhead = args.deadhead if args.deadhead is not None else args.deadhead_opt
    remaining_hours = args.remaining_hours if args.remaining_hours is not None else args.remaining_hours_opt

    # Check all required values are provided
    if total_miles is None or deadhead is None or remaining_hours is None:
        parser.print_help()
        print("\nError: All three arguments are required: total_miles, deadhead, remaining_hours")
        sys.exit(1)

    try:
        calculator = RouteMetricsCalculator()
        metrics = calculator.calculate(
            total_miles=total_miles,
            deadhead_miles=deadhead,
            remaining_hours=remaining_hours,
        )
        print(metrics.to_table())
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
