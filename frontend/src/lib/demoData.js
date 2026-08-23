/**
 * Procedural demo flight-test sample for Vercel (no backend / no import).
 * Generates coherent continuous + discrete parameters matching the expanded sample schema.
 */

export function generateDemoFlightSample(numPoints = 200) {
  const start = new Date('2026-07-15T14:30:00Z').getTime();
  const dtMs = 500; // 2 Hz
  const rows = [];

  let alt = 15000;
  let lat = 34.05;
  let lon = -118.25;
  let fuel = 4200;

  for (let i = 0; i < numPoints; i++) {
    const t = (i / numPoints) * Math.PI * 8;
    const frac = i / (numPoints - 1);

    // Performance
    alt = Math.max(9000, Math.min(30000, alt + (Math.sin(t * 0.15) * 8 + (Math.random() - 0.5) * 12)));
    const airspeed = Math.max(200, Math.min(360, 280 + 30 * Math.sin(t * 0.35) + (Math.random() - 0.5) * 10));
    const vs = 600 * Math.sin(t * 1.0) + (Math.random() - 0.5) * 200;

    // Attitude
    const pitch = Math.max(-10, Math.min(12, 1.6 * Math.sin(t * 0.6) + (Math.random() - 0.5)));
    const roll = Math.max(-30, Math.min(30, 8 * Math.sin(t * 1.0) + (Math.random() - 0.5) * 2));
    const heading = (45 + frac * 360 + (Math.random() - 0.5)) % 360;
    const aoa = Math.max(0, Math.min(12, 3 + 2 * Math.sin(t * 0.5) + (Math.random() - 0.5)));
    const g = Math.max(0.6, Math.min(2.6, 1 + 0.4 * Math.sin(t * 1.5) + (Math.random() - 0.5) * 0.1));

    // Position — ground track integrated from heading and airspeed so the
    // map overview shows a real flight path (full heading sweep ≈ circuit)
    const hdgRad = (heading * Math.PI) / 180;
    const distNm = (airspeed * dtMs) / 3600000;
    lat += (distNm / 60) * Math.cos(hdgRad);
    lon += ((distNm / 60) * Math.sin(hdgRad)) / Math.cos((lat * Math.PI) / 180);

    // Propulsion
    const throttle = Math.max(18, Math.min(95, 55 + 22 * Math.sin(t * 0.2) + (Math.random() - 0.5) * 4));
    const rpm = 1800 + (throttle / 100) * 900 + (Math.random() - 0.5) * 20;
    const fuelFlow = 180 + (throttle / 100) * 400 + (Math.random() - 0.5) * 12;
    const oilP = Math.max(28, Math.min(75, 45 + 0.12 * (rpm - 1800) + (Math.random() - 0.5) * 2));
    const hydP = 3000 + 70 * Math.sin(t * 0.25) + (Math.random() - 0.5) * 50;
    fuel = Math.max(500, fuel - (fuelFlow * (dtMs / 1000) / 3600));

    // Discrete states with realistic events
    let gear = 0;
    if (frac > 0.8 && frac < 0.86) gear = 1;
    else if (frac >= 0.86) gear = 2;

    const fuelPump = frac > 0.32 && frac < 0.36 ? 0 : 1;
    const oilPump = frac > 0.52 && frac < 0.55 ? 0 : 1;
    const hydOk = frac > 0.6 && frac < 0.64 ? 0 : 1;
    const masterCaution = fuelPump === 0 || oilPump === 0 || hydOk === 0 ? 1 : 0;

    rows.push({
      timestamp: new Date(start + i * dtMs).toISOString(),
      altitude_ft: +alt.toFixed(1),
      airspeed_kt: +airspeed.toFixed(1),
      vertical_speed_fpm: +vs.toFixed(1),
      latitude: +lat.toFixed(6),
      longitude: +lon.toFixed(6),
      pitch_deg: +pitch.toFixed(2),
      roll_deg: +roll.toFixed(2),
      heading_deg: +heading.toFixed(1),
      aoa_deg: +aoa.toFixed(2),
      g_force: +g.toFixed(2),
      throttle_pct: +throttle.toFixed(1),
      engine_rpm: Math.round(rpm),
      fuel_flow_pph: +fuelFlow.toFixed(1),
      oil_pressure_psi: +oilP.toFixed(1),
      hydraulic_pressure_psi: Math.round(hydP),
      fuel_qty_lb: Math.round(fuel),
      landing_gear: gear,
      fuel_pump_on: fuelPump,
      oil_pump_on: oilPump,
      hyd_system_ok: hydOk,
      master_caution: masterCaution
    });
  }
  return rows;
}

export const demoEvent = {
  id: 1,
  name: 'Demo Test Flight - Tail 652',
  date: '2026-07-15T14:30:00Z',
  import_status: 'Complete',
  parse_status: 'Complete',
  analysis_status: 'Ready',
  files: [{ id: 1, filename: 'sample_flight_test_data.parquet' }]
};
