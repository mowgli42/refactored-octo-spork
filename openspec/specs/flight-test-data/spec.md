# Flight Test Data Ingestion and Visualization

## Purpose

Track flight test events, register telemetry file paths, process data into a Parquet cache, and serve downsampled JSON for interactive D3 time-series plots in the Svelte dashboard.

## Requirements

### Requirement: Flight event lifecycle

The system SHALL allow users to create flight test events and track import, parse, and analysis status fields.

#### Scenario: Create and list events

- **GIVEN** an empty or populated event store
- **WHEN** the client POSTs `/events/` with a name and description
- **THEN** the API returns the event with `import_status` Pending
- **AND** GET `/events/` includes the new event

### Requirement: File registration and Parquet processing

The backend SHALL accept file registration on an event, run background processing, and cache telemetry as Parquet.

Supported source paths: local `.parquet`, `.csv`, `.h5`; remote URLs fall back to realistic mock telemetry when the path is not local.

#### Scenario: Register and process Parquet telemetry

- **GIVEN** a flight test event
- **WHEN** a user registers a local `.parquet` file path via POST `/events/{id}/files/`
- **THEN** the backend loads the data (or generates mock telemetry for non-local URLs)
- **AND** caches it as Parquet under `backend/cache/`
- **AND** updates `parse_status` to Complete and `analysis_status` to Ready

#### Scenario: Serve plot data with downsampling

- **GIVEN** a processed file with a Parquet cache path
- **WHEN** the client GETs `/files/{id}/data?limit=N`
- **THEN** the API returns JSON with columns, row_count, and downsampled records
- **AND** timestamps are ISO-formatted for D3 consumption

### Requirement: Interactive D3 plot rendering

The frontend SHALL render multi-parameter time-series with D3 when the user opens the plot modal for a processed file.

#### Scenario: Interactive D3 plot rendering

- **GIVEN** processed telemetry data from `/files/{id}/data`
- **WHEN** the plot view loads in `FlightDataPlot.svelte`
- **THEN** multi-parameter time-series renders with D3
- **AND** users can toggle series, hover for tooltips, and zoom/pan

### Requirement: Sample data and demo readiness

The repository SHALL ship a sample data generator and documented paths for stakeholder demos.

#### Scenario: Generate sample flight telemetry

- **GIVEN** `sample-data/generate_sample_flight_data.py`
- **WHEN** the script runs with default parameters
- **THEN** CSV and JSON sample files are written under `sample-data/`
- **AND** Parquet is written when pyarrow is available

## Verification

- pytest: `backend/tests/test_api.py` (event CRUD, Parquet processing, `/files/{id}/data`)
- Frontend build: `(cd frontend && npm run build)`
- Gherkin mirror: `features/flight-test-data.feature`

## Roadmap (Beads / GitHub #3–#8)

- File upload (multipart) instead of path-only registration
- Watched directory scanner
- Plot presets, export, and limit checking
- MATLAB `.mat` parser support
- Vercel demo mode with embedded sample JSON
