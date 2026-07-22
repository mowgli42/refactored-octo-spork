#!/usr/bin/env node
/**
 * Capture dashboard screenshots (API :8000, Vite :5173 must be running).
 * Usage: node scripts/capture-screenshots.mjs
 */
import { chromium } from 'playwright';
import { mkdir } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '..');
const outDir = path.join(root, 'screenshots');

const API = process.env.API_URL || 'http://127.0.0.1:8020';
const UI = process.env.UI_URL || 'http://127.0.0.1:5175';

async function seedDemoData() {
  const eventResp = await fetch(`${API}/events/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      name: 'Mach 1.5 Test',
      description: 'Screenshot demo flight event',
    }),
  });
  const event = await eventResp.json();
  const parquetPath = path.join(root, 'sample-data/sample_flight_test_data.parquet');
  await fetch(`${API}/events/${event.id}/files/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      filename: 'sample_flight_test_data.parquet',
      source_url: parquetPath,
      filetype: 'flight_log',
    }),
  });
  for (let i = 0; i < 30; i++) {
    const r = await fetch(`${API}/events/${event.id}`);
    const data = await r.json();
    if (data.parse_status === 'Complete') return event.id;
    await new Promise((r) => setTimeout(r, 200));
  }
  return event.id;
}

async function main() {
  await mkdir(outDir, { recursive: true });
  await seedDemoData();

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });

  await page.goto(UI, { waitUntil: 'networkidle' });
  await page.waitForTimeout(1500);
  await page.screenshot({ path: path.join(outDir, 'dashboard.png'), fullPage: true });

  const addFileBtn = page.getByRole('button', { name: /^Add File$/i }).first();
  if (await addFileBtn.count()) {
    await addFileBtn.click();
    await page.waitForTimeout(500);
    await page.screenshot({ path: path.join(outDir, 'add-file-modal.png') });
    await page.getByRole('button', { name: /cancel/i }).click();
    await page.waitForTimeout(300);
  }

  const plotBtn = page.getByRole('button', { name: /^Plot Data$/i }).first();
  if (await plotBtn.count()) {
    await plotBtn.click();
    await page.waitForTimeout(2000);
    await page.screenshot({ path: path.join(outDir, 'd3-plot.png') });
    await page.screenshot({ path: path.join(outDir, 'dashboard-with-plot.png'), fullPage: true });
  }

  await browser.close();
  console.log('Screenshots written to', outDir);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
