# Formula 1 Historical Analytics & Cinematic Experience

A world class motorsport data intelligence platform combining high precision empirical data science with cinematic interactive storytelling.

## Project Overview

This platform delivers an end to end analytical engine covering the complete history of the FIA Formula One World Championship from the inaugural 1950 British Grand Prix at Silverstone through to the latest available season in the connected datasets and live Jolpica API.

## Core Features

* Overview Cockpit: Real time dynamic KPIs covering total seasons, races, drivers, constructors, circuits, race entries, wins, and podiums.
* Historical Drivers Database: Filterable directory of all 861 drivers with nationality, starts, victories, podiums, poles, points, and win rates.
* Driver Profile Telemetry: Deep career trajectory analysis, points scored by season, grid position vs finish correlation, and full Grand Prix race classification history.
* Multi Driver Comparison: Side by side benchmarking of 2 to 5 drivers across multi dimensional radar charts, career points progression, and era aware normalized metrics.
* Historical Seasons Explorer: Season by season records (1950 to 2026), official driver and constructor championship standings, and Grand Prix calendar results.
* Historical Race Archive: Classification telemetry for 1,125+ Grands Prix with starting grid vs finish position deltas and fastest lap times.
* Global Circuits Explorer: Interactive geographic world map of 77 circuits across 34 nations with track telemetry, inaugural race years, and win distributions.
* Historical Constructors Database: Comprehensive records of 212 constructors, historical dominance periods, and driver points contributions.
* Qualifying & Pole Position Analytics: Single lap pace analysis, qualifying consistency, and empirical pole to win conversion rates.
* Standings Progression: Historical championship points progression charts for Driver and Constructor World Championships.
* Saturday Sprint Race Telemetry: Dedicated classification and points tracking for Saturday sprint sessions introduced in 2021.
* Stationary Pit Stop Benchmarks: Constructor servicing efficiency benchmarks and average stationary pit stop durations recorded since 2011.
* Historical EDA & Empirical Analysis: In depth analysis answering 11 foundational historical research questions backed by verified calculations.
* Era & Regulatory Evolution: Statistical comparisons across 7 regulatory eras (Early Formula 1, Classic Era, Ground Effect and Turbo, High Tech V10, V8 Era, Turbo Hybrid, and Modern Ground Effect).
* Relational Data Explorer: Direct SQL query interface with pagination, sorting, filtering, and dynamic CSV downloads.
* Data Quality & Governance: Automated schema validation, completeness scoring, null audits, and data provenance telemetry.

## System Architecture

```
Formula 1 Historical Analytics Platform
├── Presentation Tier
│   ├── Cinematic 3D Landing Page (571 sequential frames, audio synthesis, smooth scrub)
│   └── Plotly Dash Analytics Platform (Dark motorsport theme, F1 Torque typography)
├── Application Tier (Flask + Plotly Dash)
│   ├── Dynamic Multi Page Router (19 dedicated analytical modules)
│   └── Reusable Motorsport Components (Navbar, Sidebar, KPI Cards, Plotly Charts, DataTables)
├── Analytics & Modeling Tier
│   ├── Empirical EDA & 11 Core Historical Questions
│   ├── Statistical Methods, IQR Outlier Detection, Correlation Matrices
│   └── Derived Motorsport Metrics (Win rates, pole conversion, finish rates)
└── Data & Storage Tier
    ├── SQLite Relational Engine (data/processed/f1_historical.db)
    ├── Local Historical CSV Archive (data/raw/)
    └── Jolpica Ergast Compatible Live API Client with TTL Cache (data/cache/)
```

## Data Sources

1. Historical Archive: Comprehensive CSV datasets covering 1950 to 2024 (circuits, constructors, drivers, races, race results, qualifying, sprints, pit stops, seasons, status).
2. Live API Source: Jolpica Ergast Compatible F1 API (https://api.jolpi.ca/ergast/f1/) for live championship standings and telemetry updates.
3. Zero Fabrication Mandate: Missing or unrecorded historical values are strictly represented as N/A without synthetic interpolation.

## Installation & Setup

1. Clone or navigate to the repository directory.
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Initialize the historical relational database:
   ```bash
   python scripts/build_dataset.py
   ```
4. Run the unified application server locally:
   ```bash
   python app.py
   ```
5. Access the application:
   * Cinematic Experience: http://localhost:3000/
   * Analytics Platform:   http://localhost:3000/dashboard/

## Production Deployment

Configured for production deployment on Render, Railway, Google Cloud, AWS, or Heroku via the included Procfile:
```
web: gunicorn app:server --workers 2 --threads 4 --timeout 120
```

## Disclaimer

Unofficial Formula 1 historical analytics project. Not affiliated with Formula 1, FIA, Formula One Licensing B.V., or Formula One Management. All trademarks and logos belong to their respective owners.