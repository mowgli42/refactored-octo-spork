# Spec Delta: Immersive Analysis Station

## MODIFIED Requirement: Analysis presentation

The analysis experience SHALL be a full-screen station (not a modal) entered from
the events dashboard, with a themed loading sequence that names the selected event
and its associated data products before the workspace becomes interactive.

### Scenario: Enter the analysis station
- **GIVEN** the events dashboard in demo mode
- **WHEN** the user clicks Analyze on an event
- **THEN** a loading screen lists the event's associated data products as they load
- **AND** the full-screen analysis station replaces the dashboard when ready
- **AND** "← Events" returns to the dashboard

## ADDED Requirement: Interactive D3 plot builder

The station SHALL let the analyst compose the center plot from grouped parameters
(Performance, Attitude, Propulsion, Subsystems), choose a plot format (multi-line,
step/digital, area), and narrow the plotted time snippet.

### Scenario: Build a step plot of a gear transient
- **GIVEN** the analysis station is ready
- **WHEN** the analyst enables Throttle % and Landing gear, selects Step (digital),
  and narrows the time snippet to the end of the flight
- **THEN** the D3 plot re-renders with step traces for the selected window
- **AND** at least one parameter must always remain selected

## ADDED Requirement: Analysis slides

The station SHALL support named, saved plot configurations ("analysis slides") so
the analyst can switch between views without losing setup.

### Scenario: Create and switch slides
- **GIVEN** the default "Overview — performance" slide is active
- **WHEN** the analyst edits the plot and clicks "+ New slide"
- **THEN** a new slide is created from the current configuration and becomes active
- **AND** selecting a slide restores its parameters, format, and time window

## ADDED Requirement: Significant / anomalous event capture

The station SHALL let the analyst capture the current plot configuration and time
window as a significant / anomalous event with a severity (note, anomaly, critical)
and summary, listed for recall and deletion.

### Scenario: Capture and recall an anomaly
- **GIVEN** a configured plot showing a transient of interest
- **WHEN** the analyst captures it with severity "anomaly" and a summary
- **THEN** the event appears in the Significant / anomalous panel with its
  time-window labels, parameter count, and format
- **AND** selecting it restores the captured plot configuration

## ADDED Requirement: Timeline scrub and live state readout

The station SHALL provide a flight-length timeline with click-to-scrub and
play/pause, and a state panel showing the aircraft snapshot (altitude, airspeed,
throttle, RPM, gear, pumps, hydraulics, master caution) at the cursor time.

### Scenario: Scrub to a caution period
- **GIVEN** the demo flight contains pump dropouts that assert master caution
- **WHEN** the analyst scrubs the timeline into a dropout window
- **THEN** the state panel shows the affected pump OFF and Caution ACTIVE
- **AND** the plot shows a time cursor at the scrubbed position when in window
