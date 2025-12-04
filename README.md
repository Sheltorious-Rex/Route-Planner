# Route-Planner

A freight truck route metrics calculator that calculates time slot estimates and driver activity schedules.

## Features

- Calculate route metrics for freight truck hauling
- Generate driver activity schedules with time slots
- Account for driving hours regulations (Hours of Service)
- Handle deadhead (empty) miles vs loaded miles
- **Web UI** for easy access via browser (deployable to GitHub Pages)

## Web UI

The Route Planner includes a responsive single-page web interface that provides all the functionality of the command-line tool in an easy-to-use browser-based format.

### Live Demo

Visit the live demo at: `https://<username>.github.io/Route-Planner/`

### Web UI Features

- Input route parameters (total miles, deadhead miles, remaining hours)
- Advanced settings for customizing calculator parameters (speed, break duration, etc.)
- Visual display of route metrics summary
- Detailed driver activity schedule table
- Responsive design that works on desktop and mobile devices
- Dark mode support

### Running the Web UI Locally

```bash
cd web-ui
npm install
npm run dev
```

Then open http://localhost:5173/Route-Planner/ in your browser.

### Building for Production

```bash
cd web-ui
npm run build
```

The built files will be in the `web-ui/dist` directory.

## Deploying to GitHub Pages

To deploy the web UI to GitHub Pages:

### Option 1: Manual Deployment

1. Build the web UI:
   ```bash
   cd web-ui
   npm install
   npm run build
   ```

2. Copy the contents of `web-ui/dist` to the `gh-pages` branch or configure GitHub Pages to serve from the `web-ui/dist` folder.

### Option 2: GitHub Actions (Recommended)

Create a `.github/workflows/deploy.yml` file:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: web-ui/package-lock.json
      - name: Install dependencies
        run: cd web-ui && npm ci
      - name: Build
        run: cd web-ui && npm run build
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: web-ui/dist

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

Then enable GitHub Pages in your repository settings and select "GitHub Actions" as the source.

## Installation (Python CLI)

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

The calculator uses the following trucking industry constraints (configurable in the web UI):

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

## Contributing

### Web UI Development

The web UI is built with:
- React 19 + TypeScript
- Vite for build tooling
- CSS with responsive design and dark mode support

To contribute to the web UI:

1. Navigate to the web-ui directory: `cd web-ui`
2. Install dependencies: `npm install`
3. Start development server: `npm run dev`
4. Make your changes
5. Run linting: `npm run lint`
6. Build to verify: `npm run build`

## License

MIT
