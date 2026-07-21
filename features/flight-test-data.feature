Feature: Flight Test Data Ingestion and Visualization

  Scenario: Create and list events
    Given an empty or populated event store
    When the client creates an event via POST /events/
    Then the API returns the event with import_status Pending
    And GET /events/ includes the new event

  Scenario: Register and process Parquet telemetry
    Given a flight test event
    When a user registers a file path via POST /events/{id}/files/
    Then the backend caches telemetry as Parquet
    And updates parse_status to Complete and analysis_status to Ready

  Scenario: Serve plot data with downsampling
    Given a processed file with a Parquet cache path
    When the client GETs /files/{id}/data with a row limit
    Then the API returns JSON columns and downsampled records

  Scenario: Interactive D3 plot rendering
    Given processed telemetry data
    When the plot view loads
    Then multi-parameter time-series renders with D3
    And users can toggle series, hover for tooltips, and zoom or pan
