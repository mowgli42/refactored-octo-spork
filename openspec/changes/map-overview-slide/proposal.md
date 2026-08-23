# Proposal: Flight Overview Map Slide (o-my-debrief layout)

## Why

The station previously dropped the analyst straight into the D3 plot builder.
Debrief flow (o-my-debrief) starts with a geographic overview of the event —
where the aircraft flew, where things happened — before deep-diving into
specific data plots. The plot builder should be a slide/toggle, not the landing
view.

## Scope (this change)

- Port o-my-debrief's `MissionMap.svelte` as `FlightTrackMap.svelte` (Leaflet +
  dark CARTO tiles): dashed ground track, flown-track trail following playback,
  heading-rotated aircraft marker, start/end markers
- Analysis slides gain types: a default "Flight overview — map" slide plus plot
  slides; the station opens on the map and "Open data plots →" (or the slide
  selector) toggles into the D3 builder
- Overview stats strip on the map slide: duration, max altitude, max speed,
  max g, track distance, caution time
- Captured significant/anomalous events render as severity-colored markers on
  the track; clicking a marker recalls the captured plot configuration
- Location data upgraded from a random walk to a ground track integrated from
  heading and airspeed (both `demoData.js` and the Python generator), so the
  map shows a real flight circuit

## Out of Scope

- Offline / self-hosted map tiles
- Track coloring by altitude or speed
- Multiple aircraft / formation events
