# Spec Delta: Multiple Time-Aligned Panels per Slide

## MODIFIED Requirement: Interactive D3 plot builder (multi-panel)

A plot slide SHALL support multiple stacked panels, each with its own parameter
selection and plot format, all sharing the slide's time snippet and the
timeline scrub cursor so different data can be correlated on one time base.

### Scenario: Subsystem drop-out with corresponding telemetry
- **GIVEN** the "Subsystem drop-outs" slide
- **WHEN** the analyst reviews a master caution assertion
- **THEN** the top panel shows the caution and pump/hydraulic discretes as
  step traces, each in its own labeled lane (logic-analyzer style) so traces
  never draw on top of each other
- **AND** the bottom panel shows oil pressure, fuel flow, and RPM telemetry
  aligned to the same time axis
- **AND** the scrub cursor appears at the same time in every panel

### Scenario: Build a panel stack
- **GIVEN** an open plot slide
- **WHEN** the analyst clicks "+ Add panel"
- **THEN** a new panel is appended and becomes the active edit target
- **AND** parameter and format chips modify only the active panel
- **AND** removing a panel is possible while more than one remains

### Scenario: Capture the full stack
- **GIVEN** a multi-panel configuration showing a finding
- **WHEN** the analyst captures a significant / anomalous event
- **THEN** all panels (parameters, formats) and the time window are saved
- **AND** recalling the event restores the complete panel stack
