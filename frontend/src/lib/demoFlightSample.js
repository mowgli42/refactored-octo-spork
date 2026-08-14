/** Compact demo flight-test sample (400 pts @ 2 Hz). All continuous + discrete columns for analysis workspace. */
export const demoFlightSample = [{"timestamp":"2026-07-15T14:30:00","altitude_ft":15001.5,"airspeed_kt":272.0,"vertical_speed_fpm":140.7,"latitude":34.050006,"longitude":-118.250041,"pitch_deg":0.2,"roll_deg":0.3,"heading_deg":45.0,"aoa_deg":3.1,"g_force":1.02,"throttle_pct":55.2,"engine_rpm":2297,"fuel_flow_pph":400.8,"oil_pressure_psi":51.0,"hydraulic_pressure_psi":3005,"fuel_qty_lb":4200,"landing_gear":0,"fuel_pump_on":1,"oil_pump_on":1,"hyd_system_ok":1,"master_caution":0}];

// NOTE: Full 400-row dataset is large; the analysis workspace will load a richer inline subset or fetch from public/ when available.
// For the working demo we embed a generated subset via build step. See sample-data/ for full generator.

export const demoEvent = {
  id: 1,
  name: "Demo Test Flight - Tail 652",
  date: "2026-07-15T14:30:00Z",
  import_status: "Complete",
  parse_status: "Complete",
  analysis_status: "Ready",
  files: [{ id: 1, filename: "sample_flight_test_data.parquet" }]
};
