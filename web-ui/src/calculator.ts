/**
 * Route Metrics Calculator Module
 * 
 * TypeScript implementation of the Python route planner calculator.
 * Calculates time slot estimates and driver activity schedules for freight truck routes.
 */

export const ActivityType = {
  LOADING: "Loading",
  DRIVING: "Driving",
  BREAK: "Break (10-hour rest)",
  UNLOADING: "Unloading",
} as const;

export type ActivityTypeValue = typeof ActivityType[keyof typeof ActivityType];

export interface Activity {
  activityType: ActivityTypeValue;
  startTime: number; // Hours from start
  duration: number; // Hours
  miles: number; // Miles covered (0 for non-driving activities)
  notes: string;
  endTime: number; // Calculated end time
}

export interface RouteMetrics {
  totalMiles: number;
  deadheadMiles: number;
  loadedMiles: number;
  totalDrivingTime: number; // Hours
  totalBreakTime: number; // Hours
  totalLoadUnloadTime: number; // Hours
  totalTime: number; // Hours
  activities: Activity[];
}

export interface CalculatorConfig {
  speedMph: number;
  maxDrivingHours: number;
  breakDuration: number;
  loadingDuration: number;
  unloadingDuration: number;
}

export const DEFAULT_CONFIG: CalculatorConfig = {
  speedMph: 55,
  maxDrivingHours: 11,
  breakDuration: 10,
  loadingDuration: 1.5,
  unloadingDuration: 1.5,
};

/**
 * Format hours as HH:MM string.
 * Handles edge cases like negative numbers and very large values.
 */
export function formatTime(hours: number): string {
  // Handle invalid input
  if (!Number.isFinite(hours)) {
    return '00:00';
  }
  
  // Handle negative hours by treating as absolute value
  const absHours = Math.abs(hours);
  
  // Cap at reasonable maximum (999 hours)
  const cappedHours = Math.min(absHours, 999);
  
  const totalMinutes = Math.floor(cappedHours * 60);
  const hrs = Math.floor(totalMinutes / 60);
  const mins = totalMinutes % 60;
  return `${hrs.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}`;
}

/**
 * Calculate route metrics and generate activity schedule.
 */
export function calculateRouteMetrics(
  totalMiles: number,
  deadheadMiles: number,
  remainingHours: number,
  config: CalculatorConfig = DEFAULT_CONFIG
): RouteMetrics {
  // Validation
  if (totalMiles < 0) {
    throw new Error("Total miles cannot be negative");
  }
  if (deadheadMiles < 0) {
    throw new Error("Deadhead miles cannot be negative");
  }
  if (deadheadMiles > totalMiles) {
    throw new Error("Deadhead miles cannot exceed total miles");
  }
  if (remainingHours < 0) {
    throw new Error("Remaining hours cannot be negative");
  }
  if (remainingHours > config.maxDrivingHours) {
    throw new Error(`Remaining hours cannot exceed max driving hours (${config.maxDrivingHours})`);
  }

  const loadedMiles = totalMiles - deadheadMiles;
  const activities: Activity[] = [];
  let currentTime = 0;
  let milesDriven = 0;
  let hoursUntilBreak = remainingHours;
  let totalDrivingTime = 0;
  let totalBreakTime = 0;

  // Start with loading
  const loadingActivity: Activity = {
    activityType: ActivityType.LOADING,
    startTime: currentTime,
    duration: config.loadingDuration,
    miles: 0,
    notes: "Loading cargo at origin",
    endTime: currentTime + config.loadingDuration,
  };
  activities.push(loadingActivity);
  currentTime += config.loadingDuration;

  // Calculate driving schedule
  let milesRemaining = totalMiles;

  while (milesRemaining > 0) {
    // Calculate how far we can drive before needing a break
    const maxMilesBeforeBreak = hoursUntilBreak * config.speedMph;
    const milesThisSegment = Math.min(milesRemaining, maxMilesBeforeBreak);
    const segmentDuration = milesThisSegment / config.speedMph;

    // Determine if this segment is deadhead or loaded
    let segmentNote: string;
    if (milesDriven < deadheadMiles) {
      const deadheadRemaining = deadheadMiles - milesDriven;
      if (milesThisSegment <= deadheadRemaining) {
        segmentNote = "Deadhead (empty)";
      } else {
        segmentNote = "Deadhead + Loaded";
      }
    } else {
      segmentNote = "Loaded haul";
    }

    const drivingActivity: Activity = {
      activityType: ActivityType.DRIVING,
      startTime: currentTime,
      duration: segmentDuration,
      miles: milesThisSegment,
      notes: segmentNote,
      endTime: currentTime + segmentDuration,
    };
    activities.push(drivingActivity);

    currentTime += segmentDuration;
    milesDriven += milesThisSegment;
    milesRemaining -= milesThisSegment;
    totalDrivingTime += segmentDuration;
    hoursUntilBreak -= segmentDuration;

    // If we need a break and there's still miles to drive
    if (hoursUntilBreak <= 0 && milesRemaining > 0) {
      const breakActivity: Activity = {
        activityType: ActivityType.BREAK,
        startTime: currentTime,
        duration: config.breakDuration,
        miles: 0,
        notes: "Mandatory 10-hour rest",
        endTime: currentTime + config.breakDuration,
      };
      activities.push(breakActivity);
      currentTime += config.breakDuration;
      totalBreakTime += config.breakDuration;
      hoursUntilBreak = config.maxDrivingHours;
    }
  }

  // End with unloading
  const unloadingActivity: Activity = {
    activityType: ActivityType.UNLOADING,
    startTime: currentTime,
    duration: config.unloadingDuration,
    miles: 0,
    notes: "Unloading cargo at destination",
    endTime: currentTime + config.unloadingDuration,
  };
  activities.push(unloadingActivity);
  currentTime += config.unloadingDuration;

  const totalLoadUnloadTime = config.loadingDuration + config.unloadingDuration;

  return {
    totalMiles,
    deadheadMiles,
    loadedMiles,
    totalDrivingTime,
    totalBreakTime,
    totalLoadUnloadTime,
    totalTime: currentTime,
    activities,
  };
}
