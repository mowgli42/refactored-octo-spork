# Spec Delta: Flight Overview Map Slide

## MODIFIED Requirement: Analysis presentation (map-first)

The analysis station SHALL open on a flight overview map populated from the
event's location data, giving the analyst geographic context before deep-diving
into data plots. The D3 plot builder SHALL be reached via an analysis slide or
an explicit "Open data plots" action.

### Scenario: Map-first entry
- **GIVEN** the analyst clicks Analyze on an event
- **WHEN** the loading sequence completes
- **THEN** the center panel shows a map with the full ground track
- **AND** the "Flight overview — map" slide is active in the slide selector

### Scenario: Overview before deep dive
- **GIVEN** the map overview is shown
- **THEN** an overview strip summarizes duration, max altitude, max speed,
  max g, track distance, and caution time
- **AND** a heading-rotated aircraft marker tracks the timeline position
- **AND** scrubbing or playing extends the flown-track trail

## ADDED Requirement: Captured events on the map

Captured significant/anomalous events SHALL appear as severity-colored markers
at their track position on the overview map.

### Scenario: Marker recall
- **GIVEN** a captured anomaly
- **WHEN** the analyst clicks its marker on the map
- **THEN** the station switches to the plots view with the captured
  configuration restored

## MODIFIED Requirement: Sample location data

Generated sample positions SHALL form a plausible ground track integrated from
heading and airspeed rather than a random walk, so map overviews are realistic.

### Scenario: Circuit track
- **GIVEN** the default generator parameters
- **WHEN** sample data is produced
- **THEN** the lat/lon trace forms a multi-nautical-mile circuit consistent
  with the heading sweep
