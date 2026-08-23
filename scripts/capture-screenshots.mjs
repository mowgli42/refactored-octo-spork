#!/usr/bin/env node
/**
 * Validate the demo analysis-station workflow and capture screenshots.
 *
 * Drives the frontend-only demo (VITE_DEMO_MODE): events dashboard → Analyze →
 * loading sequence → immersive analysis station → plot builder (params, format,
 * time snippet) → capture significant event → analysis slides → back.
 *
 * Usage:
 *   cd frontend && npm run build && npm run preview -- --port 4173
 *   node scripts/capture-screenshots.mjs
 */
import { chromium } from 'playwright';
import { mkdir } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '..');
const outDir = path.join(root, 'screenshots');

const UI = process.env.UI_URL || 'http://127.0.0.1:4173';

function fail(msg) {
  console.error(`WORKFLOW FAILURE: ${msg}`);
  process.exit(1);
}

async function main() {
  await mkdir(outDir, { recursive: true });

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

  const consoleErrors = [];
  page.on('console', (m) => {
    if (m.type() === 'error') consoleErrors.push(m.text());
  });
  page.on('pageerror', (e) => consoleErrors.push(String(e)));

  // 1. Events dashboard
  await page.goto(UI, { waitUntil: 'networkidle' });
  await page.getByRole('button', { name: 'Analyze' }).waitFor({ timeout: 10000 });
  if (!(await page.locator('.banner', { hasText: 'Demo mode' }).count()))
    fail('demo banner missing on dashboard');
  if (!(await page.locator('td', { hasText: 'Demo Test Flight - Tail 652' }).count()))
    fail('demo event row missing');
  await page.screenshot({ path: path.join(outDir, 'dashboard.png'), fullPage: true });
  console.log('1/7 dashboard OK');

  // 2. Analyze → loading sequence
  await page.getByRole('button', { name: 'Analyze' }).click();
  await page.locator('.load-screen').waitFor({ timeout: 5000 });
  await page.waitForTimeout(900); // mid-sequence, file rows lighting up
  await page.screenshot({ path: path.join(outDir, 'analysis-loading.png') });
  console.log('2/7 loading sequence OK');

  // 3. Analysis station ready — opens on the flight overview map (o-my-debrief layout)
  await page.getByRole('button', { name: 'Capture significant event' }).waitFor({ timeout: 15000 });
  await page.locator('.leaflet-container').waitFor({ timeout: 10000 });
  if (!(await page.locator('.slide.on', { hasText: 'Flight overview — map' }).count()))
    fail('map overview slide not active by default');
  if ((await page.locator('.overview-bar .stat').count()) < 5)
    fail('flight overview stats missing');
  if (!(await page.locator('.leaflet-overlay-pane path').count()))
    fail('flight track polyline did not render on map');
  await page.waitForTimeout(2000); // allow map tiles to land for the screenshot
  await page.screenshot({ path: path.join(outDir, 'analysis-overview-map.png') });
  console.log('3/7 flight overview map OK');

  // 4. Toggle into the data plots via slide
  await page.getByRole('button', { name: 'Open data plots →' }).click();
  await page.locator('.plot svg').waitFor({ timeout: 5000 });
  if (!(await page.locator('.slide.on', { hasText: 'Overview — performance' }).count()))
    fail('plot slide not active after toggle');
  await page.screenshot({ path: path.join(outDir, 'analysis-station.png') });
  console.log('4/7 plot slide toggle OK');

  // 5. Plot builder: params + step format + time snippet (entry, duration, end time, drag)
  await page.getByRole('button', { name: 'Throttle %' }).click();
  await page.getByRole('button', { name: 'Landing gear' }).click();
  await page.getByRole('button', { name: 'Step (digital)' }).click();
  if (!(await page.locator('.chip.on', { hasText: 'Throttle %' }).count()))
    fail('param toggle did not stick');

  const summary = page.locator('.snippet-summary');

  // 4a. start time entry + duration offset (secs)
  const startIn = page.locator('.snippet .time-in').first();
  await startIn.fill('14:31:00');
  await startIn.press('Enter');
  const durIn = page.locator('.snippet .dur-in');
  await durIn.fill('30');
  await durIn.press('Enter');
  await page.waitForTimeout(300);
  let text = await summary.textContent();
  if (!text.includes('14:31:00–14:31:30'))
    fail(`duration snippet wrong: "${text}" (expected 14:31:00–14:31:30)`);
  console.log('5a start entry + 30 sec duration OK');

  // 4b. switch duration unit to minutes
  await page.locator('.snippet .unit').selectOption('min');
  await durIn.fill('0.75');
  await durIn.press('Enter');
  await page.waitForTimeout(300);
  text = await summary.textContent();
  if (!text.includes('14:31:00–14:31:45'))
    fail(`minute-duration snippet wrong: "${text}" (expected 14:31:00–14:31:45)`);
  console.log('5b duration in minutes OK');

  // 4c. explicit end-time entry
  await page.getByRole('button', { name: 'End time', exact: true }).click();
  const endIn = page.locator('.snippet .time-in').nth(1);
  await endIn.fill('14:31:50');
  await endIn.press('Enter');
  await page.waitForTimeout(300);
  text = await summary.textContent();
  if (!text.includes('14:31:00–14:31:50'))
    fail(`end-time snippet wrong: "${text}" (expected 14:31:00–14:31:50)`);
  console.log('5c end-time entry OK');

  // 4d. drag the end handle on the timeline
  const track = await page.locator('.timeline-track').boundingBox();
  const endHandle = await page.locator('.timeline-handle.end').boundingBox();
  if (!track || !endHandle) fail('timeline snippet handles missing');
  await page.mouse.move(endHandle.x + endHandle.width / 2, endHandle.y + endHandle.height / 2);
  await page.mouse.down();
  await page.mouse.move(track.x + track.width * 0.7, endHandle.y + endHandle.height / 2, { steps: 8 });
  await page.mouse.up();
  await page.waitForTimeout(300);
  text = await summary.textContent();
  if (text.includes('14:31:00–14:31:50'))
    fail(`dragging end handle had no effect: "${text}"`);
  console.log(`5d timeline end-handle drag OK (${text.trim()})`);

  await page.screenshot({ path: path.join(outDir, 'plot-builder-step.png') });
  console.log('5/7 plot builder (params + step format + time snippet entry/drag) OK');

  // 5. Capture a significant / anomalous event
  await page.getByRole('button', { name: 'Capture significant event' }).click();
  await page.locator('.modal').waitFor({ timeout: 5000 });
  await page.locator('.modal select').selectOption('anomaly');
  await page
    .locator('.modal textarea')
    .fill('Gear extension with throttle transient — landing gear step trace shows transition window while throttle drops.');
  await page.screenshot({ path: path.join(outDir, 'capture-event-modal.png') });
  await page.getByRole('button', { name: 'Save event' }).click();
  await page.locator('.sig-list li', { hasText: 'Gear extension' }).waitFor({ timeout: 5000 });

  // 6b. captured event shows as a marker on the map overview
  await page.getByRole('button', { name: 'Flight overview — map' }).click();
  await page.locator('.sig-marker').waitFor({ timeout: 5000 });
  await page.waitForTimeout(1500); // tiles
  await page.screenshot({ path: path.join(outDir, 'map-event-marker.png') });
  // recalling the event from the left panel returns to the plots view
  await page.locator('.sig-btn', { hasText: 'Gear extension' }).click();
  await page.locator('.plot svg').waitFor({ timeout: 5000 });
  console.log('6/7 significant event capture + map marker OK');

  // 6. New analysis slide, then back to dashboard
  await page.getByRole('button', { name: '+ New slide' }).click();
  if (!(await page.locator('.slide', { hasText: 'Slide 2' }).count()))
    fail('new analysis slide not created');
  await page.screenshot({ path: path.join(outDir, 'significant-event-captured.png') });
  await page.getByRole('button', { name: '← Events' }).click();
  await page.getByRole('button', { name: 'Analyze' }).waitFor({ timeout: 5000 });
  console.log('7/7 slides + back navigation OK');

  await browser.close();

  if (consoleErrors.length) fail(`console errors:\n${consoleErrors.join('\n')}`);
  console.log('Workflow validated. Screenshots written to', outDir);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
