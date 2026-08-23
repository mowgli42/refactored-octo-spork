/**
 * DASHlink-inspired procedural flight sample for Vercel demos.
 * Parameter names/families mirror NASA DASHlink Sample Flight Data (~186 real params).
 * See docs/DATASETS.md — real .mat flights are ~800MB; this approximates types + correlations.
 */

export function generateDemoFlightSample(numPoints = 280) {
  const start = new Date('2026-07-15T14:30:00Z').getTime();
  const dtMs = 500; // 2 Hz aligned demo rate
  const rows = [];

  let alt = 15000;
  let lat = 34.05;
  let lon = -118.25;
  let fuel = 4200;

  for (let i = 0; i < numPoints; i++) {
    const t = (i / numPoints) * Math.PI * 8;
    const frac = i / (numPoints - 1);

    // --- Performance / nav (DASHlink: BARO CORRECT ALTITUDE, COMPUTED AIRSPEED, …) ---
    alt = Math.max(800, Math.min(32000, alt + Math.sin(t * 0.15) * 10 + (Math.random() - 0.5) * 14));
    // late approach descent
    if (frac > 0.78) alt = Math.max(50, alt - 35);
    const airspeed = Math.max(120, Math.min(380, 280 + 30 * Math.sin(t * 0.35) + (Math.random() - 0.5) * 10 - (frac > 0.8 ? 80 : 0)));
    const vs = 600 * Math.sin(t * 1.0) + (Math.random() - 0.5) * 200 - (frac > 0.8 ? 400 : 0);

    // --- Attitude ---
    const pitch = Math.max(-12, Math.min(14, 1.6 * Math.sin(t * 0.6) + (Math.random() - 0.5) - (frac > 0.82 ? 2 : 0)));
    const roll = Math.max(-35, Math.min(35, 8 * Math.sin(t * 1.0) + (Math.random() - 0.5) * 2));
    const heading = (45 + frac * 380 + (Math.random() - 0.5)) % 360;
    const aoa = Math.max(0, Math.min(14, 3 + 2 * Math.sin(t * 0.5) + (Math.random() - 0.5) + (frac > 0.85 ? 2 : 0)));
    const g = Math.max(0.5, Math.min(2.8, 1 + 0.4 * Math.sin(t * 1.5) + (Math.random() - 0.5) * 0.1));

    // Track from heading + airspeed
    const hdgRad = (heading * Math.PI) / 180;
    const distNm = (airspeed * dtMs) / 3600000;
    lat += (distNm / 60) * Math.cos(hdgRad);
    lon += ((distNm / 60) * Math.sin(hdgRad)) / Math.max(0.2, Math.cos((lat * Math.PI) / 180));

    // --- Propulsion (CORE SPEED AVG ≈ throttle proxy in DASHlink) ---
    const throttle = Math.max(12, Math.min(98, 55 + 22 * Math.sin(t * 0.2) + (Math.random() - 0.5) * 4 - (frac > 0.82 ? 25 : 0)));
    const coreSpeed = Math.max(20, Math.min(100, throttle * 0.92 + (Math.random() - 0.5) * 3)); // %
    const rpm = 1800 + (throttle / 100) * 900 + (Math.random() - 0.5) * 20;
    const fuelFlow = 180 + (throttle / 100) * 400 + (Math.random() - 0.5) * 12;
    const oilP = Math.max(28, Math.min(75, 45 + 0.12 * (rpm - 1800) + (Math.random() - 0.5) * 2));
    const hydP = 3000 + 70 * Math.sin(t * 0.25) + (Math.random() - 0.5) * 50;
    const tat = 15 - alt / 1000 * 2 + (Math.random() - 0.5);
    fuel = Math.max(400, fuel - (fuelFlow * (dtMs / 1000) / 3600));

    // --- Control surfaces (DASHlink: aileron, elevator, rudder, flaps) ---
    const aileronL = roll * 0.35 + (Math.random() - 0.5) * 1.5;
    const aileronR = -aileronL + (Math.random() - 0.5);
    const elevator = pitch * 0.4 + (Math.random() - 0.5);
    const rudder = Math.sin(t * 0.4) * 3 + (Math.random() - 0.5);
    // flaps deploy late on approach
    let flaps = 0;
    if (frac > 0.72 && frac < 0.8) flaps = 15;
    else if (frac >= 0.8 && frac < 0.88) flaps = 25;
    else if (frac >= 0.88) flaps = 35;

    // --- Approach aids (final segment) ---
    const glideslopeDev = frac > 0.75 ? (Math.random() - 0.5) * 0.4 + (frac - 0.85) * 0.2 : 0;
    const localizerDev = frac > 0.75 ? (Math.random() - 0.5) * 0.3 : 0;

    // --- Environment ---
    const windSpeed = 12 + 8 * Math.sin(t * 0.1) + (Math.random() - 0.5) * 2;
    const windDir = (220 + frac * 30 + (Math.random() - 0.5) * 5) % 360;

    // --- Discrete / warnings (DASHlink-style) ---
    let gear = 0;
    if (frac > 0.8 && frac < 0.86) gear = 1;
    else if (frac >= 0.86) gear = 2;

    const fuelPump = frac > 0.32 && frac < 0.36 ? 0 : 1;
    const oilPump = frac > 0.52 && frac < 0.55 ? 0 : 1;
    const hydOk = frac > 0.6 && frac < 0.64 ? 0 : 1;
    const hydLowGreen = hydOk === 0 ? 1 : 0;
    const hydLowYellow = frac > 0.61 && frac < 0.63 ? 1 : 0;
    const apuFire = 0;
    const masterCaution = fuelPump === 0 || oilPump === 0 || hydOk === 0 ? 1 : 0;

    rows.push({
      timestamp: new Date(start + i * dtMs).toISOString(),
      // performance
      altitude_ft: +alt.toFixed(1),
      airspeed_kt: +airspeed.toFixed(1),
      vertical_speed_fpm: +vs.toFixed(1),
      latitude: +lat.toFixed(6),
      longitude: +lon.toFixed(6),
      // attitude
      pitch_deg: +pitch.toFixed(2),
      roll_deg: +roll.toFixed(2),
      heading_deg: +heading.toFixed(1),
      aoa_deg: +aoa.toFixed(2),
      g_force: +g.toFixed(2),
      // propulsion
      throttle_pct: +throttle.toFixed(1),
      core_speed_pct: +coreSpeed.toFixed(1),
      engine_rpm: Math.round(rpm),
      fuel_flow_pph: +fuelFlow.toFixed(1),
      oil_pressure_psi: +oilP.toFixed(1),
      hydraulic_pressure_psi: Math.round(hydP),
      fuel_qty_lb: Math.round(fuel),
      tat_c: +tat.toFixed(1),
      // controls
      aileron_lh_deg: +aileronL.toFixed(2),
      aileron_rh_deg: +aileronR.toFixed(2),
      elevator_deg: +elevator.toFixed(2),
      rudder_deg: +rudder.toFixed(2),
      flap_deg: flaps,
      // approach
      glideslope_dev_pct: +glideslopeDev.toFixed(3),
      localizer_dev_pct: +localizerDev.toFixed(3),
      // environment
      wind_speed_kt: +windSpeed.toFixed(1),
      wind_dir_deg: +windDir.toFixed(1),
      // discretes / warnings
      landing_gear: gear,
      fuel_pump_on: fuelPump,
      oil_pump_on: oilPump,
      hyd_system_ok: hydOk,
      hyd_low_green: hydLowGreen,
      hyd_low_yellow: hydLowYellow,
      apu_fire_warning: apuFire,
      master_caution: masterCaution
    });
  }
  return rows;
}

export const demoEvent = {
  id: 1,
  name: 'Demo Test Flight - Tail 652 (DASHlink-style)',
  date: '2026-07-15T14:30:00Z',
  import_status: 'Complete',
  parse_status: 'Complete',
  analysis_status: 'Ready',
  files: [
    { id: 1, filename: 'sample_flight_test_data.parquet' },
    { id: 2, filename: 'dashlink_inspired_params.json' }
  ]
};

/** Parameter catalog for UI grouping — aligned to docs/DATASETS.md */
export const PARAM_CATALOG = [
  {
    id: 'perf',
    label: 'Performance / Nav',
    params: [
      { key: 'altitude_ft', label: 'Altitude (ft)' },
      { key: 'airspeed_kt', label: 'Airspeed (kt)' },
      { key: 'vertical_speed_fpm', label: 'VS (fpm)' }
    ]
  },
  {
    id: 'att',
    label: 'Attitude',
    params: [
      { key: 'pitch_deg', label: 'Pitch (°)' },
      { key: 'roll_deg', label: 'Roll (°)' },
      { key: 'aoa_deg', label: 'AoA (°)' },
      { key: 'g_force', label: 'Vertical accel (g)' },
      { key: 'heading_deg', label: 'True heading (°)' }
    ]
  },
  {
    id: 'prop',
    label: 'Propulsion',
    params: [
      { key: 'throttle_pct', label: 'Throttle %' },
      { key: 'core_speed_pct', label: 'Core speed %' },
      { key: 'engine_rpm', label: 'RPM' },
      { key: 'fuel_flow_pph', label: 'Fuel flow' },
      { key: 'oil_pressure_psi', label: 'Oil psi' },
      { key: 'tat_c', label: 'TAT (°C)' }
    ]
  },
  {
    id: 'ctrl',
    label: 'Controls',
    params: [
      { key: 'aileron_lh_deg', label: 'Aileron LH' },
      { key: 'aileron_rh_deg', label: 'Aileron RH' },
      { key: 'elevator_deg', label: 'Elevator' },
      { key: 'rudder_deg', label: 'Rudder' },
      { key: 'flap_deg', label: 'Flaps (°)' }
    ]
  },
  {
    id: 'appr',
    label: 'Approach',
    params: [
      { key: 'glideslope_dev_pct', label: 'Glideslope dev' },
      { key: 'localizer_dev_pct', label: 'Localizer dev' }
    ]
  },
  {
    id: 'env',
    label: 'Environment',
    params: [
      { key: 'wind_speed_kt', label: 'Wind speed' },
      { key: 'wind_dir_deg', label: 'Wind dir' }
    ]
  },
  {
    id: 'disc',
    label: 'Warnings / discretes',
    params: [
      { key: 'landing_gear', label: 'Landing gear' },
      { key: 'fuel_pump_on', label: 'Fuel pump' },
      { key: 'oil_pump_on', label: 'Oil pump' },
      { key: 'hyd_system_ok', label: 'Hydraulics OK' },
      { key: 'hyd_low_green', label: 'Hyd low green' },
      { key: 'hyd_low_yellow', label: 'Hyd low yellow' },
      { key: 'master_caution', label: 'Master caution' }
    ]
  }
];
