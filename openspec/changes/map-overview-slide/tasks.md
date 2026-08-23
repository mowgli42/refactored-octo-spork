# Tasks – Flight Overview Map Slide

## Implemented

- [x] `FlightTrackMap.svelte` ported from o-my-debrief `MissionMap.svelte`
- [x] Leaflet dependency added; CARTO dark tiles matching the station theme
- [x] Typed slides: map overview (default) + plot slides; "Open data plots →"
- [x] Overview stats strip (duration, max alt/speed/g, track nm, caution secs)
- [x] Sig-event markers on the track (severity colors, tooltip, click-to-recall)
- [x] Timeline scrub / play drives the flown trail and aircraft marker
- [x] Ground track integrated from heading + airspeed in `demoData.js` and
      `sample-data/generate_sample_flight_data.py`; sample files regenerated

## Verified

- [x] Production build succeeds; backend pytest still 3 passed
- [x] Python generator produces a ~4 nm circuit (was a stationary random walk)
- [x] Workflow script extended to 7 steps incl. map-first entry, plot slide
      toggle, and map event marker — all pass headless with zero console errors
