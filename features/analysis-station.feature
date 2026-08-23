Feature: Immersive Flight Test Analysis Station
  Full-screen debrief workspace entered from the events dashboard.
  Automated by scripts/capture-screenshots.mjs against the demo build.

  Background:
    Given the frontend is built with VITE_DEMO_MODE
    And the events dashboard shows "Demo Test Flight - Tail 652"

  Scenario: Enter the analysis station through the loading sequence
    When the user clicks Analyze on the demo event
    Then a loading screen lists the associated data products as they load
    And the full-screen analysis station opens on the flight overview map
    And the default slide "Flight overview — map" is active

  Scenario: Flight overview map before deep-diving into plots
    Given the analysis station has opened on the map view
    Then the map shows the ground track populated from the location data
    And a heading-rotated aircraft marker sits at the current timeline position
    And an overview strip shows duration, max altitude, max speed, max g,
      track distance, and caution time
    And scrubbing the timeline extends the flown-track trail on the map

  Scenario: Toggle into the data plots via analysis slide
    Given the flight overview map is shown
    When the analyst clicks "Open data plots" or selects a plot slide
    Then the center panel switches to the interactive D3 plot builder
    And selecting the "Flight overview — map" slide returns to the map

  Scenario: Captured events appear on the overview map
    Given a captured significant or anomalous event
    When the analyst returns to the flight overview map
    Then the event appears as a severity-colored marker at its position on the track
    And clicking the marker or the event recalls its plot configuration

  Scenario: Build a step plot of a gear transient
    Given the analysis station is ready
    When the analyst enables the "Throttle %" and "Landing gear" parameters
    And selects the "Step (digital)" plot format
    And narrows the time snippet toward the end of the flight
    Then the plot re-renders as step traces for the selected window
    And the enabled parameter chips are highlighted

  Scenario: Define the time snippet by start time and duration offset
    Given the analysis station is ready
    When the analyst enters a start time of "14:31:00"
    And chooses Duration mode with an offset of 30 seconds
    Then the snippet summary shows "14:31:00–14:31:30"
    And the plot re-renders to that window
    And switching the unit to minutes preserves the same window definition

  Scenario: Define the time snippet by explicit end time
    Given a snippet start time of "14:31:00"
    When the analyst switches to End time mode
    And enters an end time of "14:31:50"
    Then the snippet summary shows "14:31:00–14:31:50"
    And the end time may not precede the start time

  Scenario: Adjust the snippet with timeline markers
    Given a defined time snippet
    When the analyst drags the start or end marker on the timeline
    Then the snippet window and time entries update live while dragging
    And "Full flight" resets the snippet to the whole recording

  Scenario: Capture a significant or anomalous event
    Given a configured plot showing a transient of interest
    When the analyst clicks "Capture significant event"
    And selects severity "Anomaly" and enters a summary
    And saves the event
    Then the event appears in the Significant / anomalous panel
    And it records the time window, parameter count, and plot format

  Scenario: Correlate a subsystem drop-out with instrumentation telemetry
    Given the "Subsystem drop-outs" analysis slide
    Then two stacked panels share the same time axis and scrub cursor
    And the top panel shows master caution and pump/hydraulic discretes as step traces
    And the bottom panel shows the corresponding oil pressure, fuel flow, and RPM telemetry
    And a drop-out in the top panel aligns with the telemetry response below it

  Scenario: Build a multi-panel analysis
    Given a plot slide is open
    When the analyst clicks "+ Add panel"
    Then a new panel is stacked below with its own parameters and format
    And the parameter and format chips edit whichever panel is active
    And a panel can be removed as long as at least one remains
    And capturing a significant event saves all panels for recall

  Scenario: Manage analysis slides
    Given the analysis station is ready
    When the analyst clicks "+ New slide"
    Then a new slide is created from the current plot configuration
    And selecting a slide restores its parameters, format, and time window

  Scenario: Scrub the timeline and read aircraft state
    Given the demo flight contains pump dropouts that assert master caution
    When the analyst scrubs the timeline into a dropout window
    Then the state panel shows the affected pump OFF and Caution ACTIVE

  Scenario: Return to the events dashboard
    Given the analysis station is open
    When the analyst clicks "← Events"
    Then the events dashboard is shown again with the Analyze action
