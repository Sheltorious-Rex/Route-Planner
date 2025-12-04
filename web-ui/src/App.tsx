import { useState } from 'react'
import {
  calculateRouteMetrics,
  formatTime,
  DEFAULT_CONFIG,
  ActivityType,
} from './calculator'
import type { RouteMetrics, CalculatorConfig, ActivityTypeValue } from './calculator'
import './App.css'

/**
 * Get CSS class name for activity type rows in the schedule table.
 * Maps activity types to consistent class names for styling.
 */
function getActivityClassName(activityType: ActivityTypeValue): string {
  switch (activityType) {
    case ActivityType.LOADING:
      return 'activity-loading'
    case ActivityType.DRIVING:
      return 'activity-driving'
    case ActivityType.BREAK:
      return 'activity-break'
    case ActivityType.UNLOADING:
      return 'activity-unloading'
    default:
      return ''
  }
}

function App() {
  // Input state
  const [totalMiles, setTotalMiles] = useState<string>('500')
  const [deadheadMiles, setDeadheadMiles] = useState<string>('50')
  const [remainingHours, setRemainingHours] = useState<string>('8')

  // Advanced settings state
  const [showAdvanced, setShowAdvanced] = useState(false)
  const [speedMph, setSpeedMph] = useState<string>(DEFAULT_CONFIG.speedMph.toString())
  const [maxDrivingHours, setMaxDrivingHours] = useState<string>(DEFAULT_CONFIG.maxDrivingHours.toString())
  const [breakDuration, setBreakDuration] = useState<string>(DEFAULT_CONFIG.breakDuration.toString())
  const [loadingDuration, setLoadingDuration] = useState<string>(DEFAULT_CONFIG.loadingDuration.toString())
  const [unloadingDuration, setUnloadingDuration] = useState<string>(DEFAULT_CONFIG.unloadingDuration.toString())

  // Results state
  const [metrics, setMetrics] = useState<RouteMetrics | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleCalculate = () => {
    setError(null)
    setMetrics(null)

    const config: CalculatorConfig = {
      speedMph: parseFloat(speedMph) || DEFAULT_CONFIG.speedMph,
      maxDrivingHours: parseFloat(maxDrivingHours) || DEFAULT_CONFIG.maxDrivingHours,
      breakDuration: parseFloat(breakDuration) || DEFAULT_CONFIG.breakDuration,
      loadingDuration: parseFloat(loadingDuration) || DEFAULT_CONFIG.loadingDuration,
      unloadingDuration: parseFloat(unloadingDuration) || DEFAULT_CONFIG.unloadingDuration,
    }

    try {
      const result = calculateRouteMetrics(
        parseFloat(totalMiles) || 0,
        parseFloat(deadheadMiles) || 0,
        parseFloat(remainingHours) || 0,
        config
      )
      setMetrics(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    }
  }

  const handleClear = () => {
    setTotalMiles('500')
    setDeadheadMiles('50')
    setRemainingHours('8')
    setMetrics(null)
    setError(null)
  }

  const getActivityIcon = (type: ActivityTypeValue) => {
    switch (type) {
      case ActivityType.LOADING:
        return '📦'
      case ActivityType.DRIVING:
        return '🚛'
      case ActivityType.BREAK:
        return '💤'
      case ActivityType.UNLOADING:
        return '📤'
    }
  }

  return (
    <div className="app">
      <header className="header">
        <h1>🚛 Route Planner</h1>
        <p className="subtitle">Freight Truck Route Metrics Calculator</p>
      </header>

      <main className="main">
        <section className="input-section" aria-label="Route input parameters">
          <h2>Route Parameters</h2>
          <div className="form-grid">
            <div className="form-group">
              <label htmlFor="totalMiles">Total Miles</label>
              <input
                id="totalMiles"
                type="number"
                min="0"
                value={totalMiles}
                onChange={(e) => setTotalMiles(e.target.value)}
                aria-describedby="totalMiles-help"
              />
              <small id="totalMiles-help">Total distance for the route</small>
            </div>

            <div className="form-group">
              <label htmlFor="deadheadMiles">Deadhead Miles</label>
              <input
                id="deadheadMiles"
                type="number"
                min="0"
                value={deadheadMiles}
                onChange={(e) => setDeadheadMiles(e.target.value)}
                aria-describedby="deadheadMiles-help"
              />
              <small id="deadheadMiles-help">Empty miles (driving without cargo)</small>
            </div>

            <div className="form-group">
              <label htmlFor="remainingHours">Remaining Hours</label>
              <input
                id="remainingHours"
                type="number"
                min="0"
                max="11"
                step="0.5"
                value={remainingHours}
                onChange={(e) => setRemainingHours(e.target.value)}
                aria-describedby="remainingHours-help"
              />
              <small id="remainingHours-help">Hours left in current driving window (0-11)</small>
            </div>
          </div>

          <div className="advanced-toggle">
            <button
              type="button"
              className="toggle-btn"
              onClick={() => setShowAdvanced(!showAdvanced)}
              aria-expanded={showAdvanced}
              aria-controls="advanced-settings"
            >
              {showAdvanced ? '▼' : '▶'} Advanced Settings
            </button>
          </div>

          {showAdvanced && (
            <div id="advanced-settings" className="advanced-settings">
              <div className="form-grid">
                <div className="form-group">
                  <label htmlFor="speedMph">Average Speed (mph)</label>
                  <input
                    id="speedMph"
                    type="number"
                    min="1"
                    value={speedMph}
                    onChange={(e) => setSpeedMph(e.target.value)}
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="maxDrivingHours">Max Driving Hours</label>
                  <input
                    id="maxDrivingHours"
                    type="number"
                    min="1"
                    value={maxDrivingHours}
                    onChange={(e) => setMaxDrivingHours(e.target.value)}
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="breakDuration">Break Duration (hours)</label>
                  <input
                    id="breakDuration"
                    type="number"
                    min="0"
                    step="0.5"
                    value={breakDuration}
                    onChange={(e) => setBreakDuration(e.target.value)}
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="loadingDuration">Loading Time (hours)</label>
                  <input
                    id="loadingDuration"
                    type="number"
                    min="0"
                    step="0.25"
                    value={loadingDuration}
                    onChange={(e) => setLoadingDuration(e.target.value)}
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="unloadingDuration">Unloading Time (hours)</label>
                  <input
                    id="unloadingDuration"
                    type="number"
                    min="0"
                    step="0.25"
                    value={unloadingDuration}
                    onChange={(e) => setUnloadingDuration(e.target.value)}
                  />
                </div>
              </div>
            </div>
          )}

          <div className="button-group">
            <button className="btn primary" onClick={handleCalculate}>
              Calculate Route
            </button>
            <button className="btn secondary" onClick={handleClear}>
              Clear
            </button>
          </div>
        </section>

        {error && (
          <div className="error-message" role="alert">
            <strong>Error:</strong> {error}
          </div>
        )}

        {metrics && (
          <section className="results-section" aria-label="Calculation results">
            <h2>Route Metrics Summary</h2>

            <div className="metrics-grid">
              <div className="metric-card">
                <div className="metric-value">{metrics.totalMiles.toFixed(1)}</div>
                <div className="metric-label">Total Miles</div>
              </div>
              <div className="metric-card">
                <div className="metric-value">{metrics.deadheadMiles.toFixed(1)}</div>
                <div className="metric-label">Deadhead Miles</div>
              </div>
              <div className="metric-card">
                <div className="metric-value">{metrics.loadedMiles.toFixed(1)}</div>
                <div className="metric-label">Loaded Miles</div>
              </div>
              <div className="metric-card highlight">
                <div className="metric-value">{formatTime(metrics.totalDrivingTime)}</div>
                <div className="metric-label">Driving Time</div>
                <div className="metric-subvalue">{metrics.totalDrivingTime.toFixed(2)} hours</div>
              </div>
              <div className="metric-card">
                <div className="metric-value">{formatTime(metrics.totalBreakTime)}</div>
                <div className="metric-label">Break Time</div>
                <div className="metric-subvalue">{metrics.totalBreakTime.toFixed(2)} hours</div>
              </div>
              <div className="metric-card">
                <div className="metric-value">{formatTime(metrics.totalLoadUnloadTime)}</div>
                <div className="metric-label">Load/Unload Time</div>
                <div className="metric-subvalue">{metrics.totalLoadUnloadTime.toFixed(2)} hours</div>
              </div>
              <div className="metric-card total">
                <div className="metric-value">{formatTime(metrics.totalTime)}</div>
                <div className="metric-label">Total Route Time</div>
                <div className="metric-subvalue">{metrics.totalTime.toFixed(2)} hours</div>
              </div>
            </div>

            <h3>Driver Activity Schedule</h3>
            <div className="schedule-table-wrapper">
              <table className="schedule-table" aria-label="Driver activity schedule">
                <thead>
                  <tr>
                    <th scope="col">#</th>
                    <th scope="col">Activity</th>
                    <th scope="col">Start</th>
                    <th scope="col">End</th>
                    <th scope="col">Duration</th>
                    <th scope="col">Miles</th>
                    <th scope="col">Notes</th>
                  </tr>
                </thead>
                <tbody>
                  {metrics.activities.map((activity, index) => (
                    <tr key={index} className={getActivityClassName(activity.activityType)}>
                      <td>{index + 1}</td>
                      <td>
                        <span className="activity-icon">{getActivityIcon(activity.activityType)}</span>
                        {activity.activityType}
                      </td>
                      <td>{formatTime(activity.startTime)}</td>
                      <td>{formatTime(activity.endTime)}</td>
                      <td>{formatTime(activity.duration)}</td>
                      <td>{activity.miles.toFixed(1)}</td>
                      <td>{activity.notes}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}
      </main>

      <footer className="footer">
        <dl className="constraints-list" aria-label="Current calculation constraints">
          <div className="constraint-item">
            <dt>Average Speed</dt>
            <dd>{speedMph} mph</dd>
          </div>
          <div className="constraint-item">
            <dt>Max Driving</dt>
            <dd>{maxDrivingHours} hrs</dd>
          </div>
          <div className="constraint-item">
            <dt>Break Duration</dt>
            <dd>{breakDuration} hrs</dd>
          </div>
          <div className="constraint-item">
            <dt>Load/Unload</dt>
            <dd>{loadingDuration}/{unloadingDuration} hrs</dd>
          </div>
        </dl>
        <p className="copyright">Route Planner &copy; 2024</p>
      </footer>
    </div>
  )
}

export default App
