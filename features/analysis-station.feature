Feature: Immersive Flight Test Analysis Station
  Full-screen debrief workspace entered from the events dashboard.
  Automated by scripts/capture-screenshots.mjs against the demo build.

  Background:
    Given the frontend is built with VITE_DEMO_MODE
    And the events dashboard shows "Demo Test Flight - Tail 652"

  Scenario: Enter the analysis station through the loading sequence
    When the user clicks Analyze on the demo event
    Then a loading screen lists the associated data products as they load
    And the full-screen analysis station opens with a rendered D3 plot
    And the default slide "Overview — performance" is active

  Scenario: Build a step plot of a gear transient
    Given the analysis station is ready
    When the analyst enables the "Throttle %" and "Landing gear" parameters
    And selects the "Step (digital)" plot format
    And narrows the time snippet toward the end of the flight
    Then the plot re-renders as step traces for the selected window
    And the enabled parameter chips are highlighted

  Scenario: Capture a significant or anomalous event
    Given a configured plot showing a transient of interest
    When the analyst clicks "Capture significant event"
    And selects severity "Anomaly" and enters a summary
    And saves the event
    Then the event appears in the Significant / anomalous panel
    And it records the time window, parameter count, and plot format

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
