<script>
  import { onMount, onDestroy, createEventDispatcher } from 'svelte';
  import * as d3 from 'd3';
  import { generateDemoFlightSample } from './demoData.js';

  /** @type {{ id: number, name: string, date: string, files?: any[] }} */
  export let event = null;
  /** @type {any[]} */
  export let data = [];

  const dispatch = createEventDispatcher();

  let phase = 'loading'; // loading | ready
  let loadStep = 0;
  let loadMessages = [];
  let parsed = [];
  let currentIdx = 0;
  let playing = false;
  let playTimer = null;
  let mapEl;
  let chartsEl;
  let timelineEl;

  const FILES = [
    { name: 'sample_flight_test_data.parquet', role: 'Primary telemetry', status: 'ready' },
    { name: 'engine_bus.csv', role: 'Propulsion bus', status: 'ready' },
    { name: 'subsystem_discretes.json', role: 'Digital discretes', status: 'ready' }
  ];

  $: snapshot = parsed[currentIdx] || null;
  $: progress = parsed.length ? currentIdx / (parsed.length - 1) : 0;

  onMount(async () => {
    await runLoadingSequence();
  });

  onDestroy(() => {
    if (playTimer) clearInterval(playTimer);
  });

  async function runLoadingSequence() {
    phase = 'loading';
    const steps = [
      `Selected event: ${event?.name || 'Demo Test Flight - Tail 652'}`,
      'Resolving associated data files…',
      `Loading ${FILES[0].name}`,
      `Loading ${FILES[1].name}`,
      `Loading ${FILES[2].name}`,
      'Building time index & interpolators…',
      'Preparing map track and panel layout…',
      'Analysis station ready'
    ];
    loadMessages = [];
    for (let i = 0; i < steps.length; i++) {
      loadStep = i;
      loadMessages = [...loadMessages, steps[i]];
      await sleep(280 + (i === 2 || i === 3 || i === 4 ? 180 : 0));
    }

    if (!data?.length) {
      data = generateDemoFlightSample(240);
    }
    parsed = data.map((d) => ({
      ...d,
      _date: d3.isoParse(d.timestamp) || new Date(d.timestamp)
    }));
    currentIdx = 0;
    phase = 'ready';
    // allow DOM to mount
    await sleep(40);
    drawMap();
    drawCharts();
    drawTimeline();
  }

  function sleep(ms) {
    return new Promise((r) => setTimeout(r, ms));
  }

  function back() {
    playing = false;
    if (playTimer) clearInterval(playTimer);
    dispatch('back');
  }

  function togglePlay() {
    playing = !playing;
    if (playTimer) clearInterval(playTimer);
    if (!playing) return;
    playTimer = setInterval(() => {
      if (currentIdx >= parsed.length - 1) {
        playing = false;
        clearInterval(playTimer);
        return;
      }
      currentIdx += 1;
      drawMap();
    }, 120);
  }

  function scrubTo(frac) {
    currentIdx = Math.round(frac * (parsed.length - 1));
    drawMap();
  }

  function onTimelineClick(e) {
    const rect = timelineEl.getBoundingClientRect();
    const frac = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
    scrubTo(frac);
  }

  function gearLabel(v) {
    if (v === 2) return 'DOWN';
    if (v === 1) return 'TRANS';
    return 'UP';
  }

  function onOff(v) {
    return v ? 'ON' : 'OFF';
  }

  // ---- MAP ----
  function drawMap() {
    if (!mapEl || !parsed.length) return;
    const w = mapEl.clientWidth || 600;
    const h = mapEl.clientHeight || 280;
    d3.select(mapEl).selectAll('*').remove();
    const svg = d3.select(mapEl).append('svg').attr('width', w).attr('height', h);
    const pad = 16;
    const x = d3
      .scaleLinear()
      .domain(d3.extent(parsed, (d) => d.longitude))
      .range([pad, w - pad]);
    const y = d3
      .scaleLinear()
      .domain(d3.extent(parsed, (d) => d.latitude))
      .range([h - pad, pad]);
    const color = d3
      .scaleSequential(d3.interpolateTurbo)
      .domain(d3.extent(parsed, (d) => d.altitude_ft));

    const line = d3
      .line()
      .x((d) => x(d.longitude))
      .y((d) => y(d.latitude))
      .curve(d3.curveCatmullRom);

    for (let i = 1; i < parsed.length; i++) {
      svg
        .append('path')
        .datum([parsed[i - 1], parsed[i]])
        .attr('fill', 'none')
        .attr('stroke', color(parsed[i].altitude_ft))
        .attr('stroke-width', 2.2)
        .attr('d', line);
    }

    // aircraft at scrub
    const cur = parsed[currentIdx];
    if (cur) {
      svg
        .append('circle')
        .attr('cx', x(cur.longitude))
        .attr('cy', y(cur.latitude))
        .attr('r', 6)
        .attr('fill', '#3dd6c6')
        .attr('stroke', '#0b1220')
        .attr('stroke-width', 2);
    }
    svg
      .append('circle')
      .attr('cx', x(parsed[0].longitude))
      .attr('cy', y(parsed[0].latitude))
      .attr('r', 3.5)
      .attr('fill', '#5ddea0');
    svg
      .append('circle')
      .attr('cx', x(parsed[parsed.length - 1].longitude))
      .attr('cy', y(parsed[parsed.length - 1].latitude))
      .attr('r', 3.5)
      .attr('fill', '#ff5c6c');
  }

  // ---- CHARTS (key initial graphs) ----
  function drawCharts() {
    if (!chartsEl || !parsed.length) return;
    d3.select(chartsEl).selectAll('*').remove();
    const w = chartsEl.clientWidth || 900;
    const panelH = 72;
    const gap = 8;
    const groups = [
      {
        title: 'Performance',
        series: [
          { k: 'altitude_ft', c: '#4da3ff' },
          { k: 'airspeed_kt', c: '#ff7a45' },
          { k: 'vertical_speed_fpm', c: '#5ddea0' }
        ]
      },
      {
        title: 'Propulsion',
        series: [
          { k: 'throttle_pct', c: '#f0c14a' },
          { k: 'engine_rpm', c: '#be185d' },
          { k: 'fuel_flow_pph', c: '#3dd6c6' }
        ]
      },
      {
        title: 'Attitude',
        series: [
          { k: 'pitch_deg', c: '#a78bfa' },
          { k: 'roll_deg', c: '#fb923c' },
          { k: 'aoa_deg', c: '#38bdf8' }
        ]
      }
    ];
    const totalH = groups.length * (panelH + gap) + 20;
    const svg = d3.select(chartsEl).append('svg').attr('width', w).attr('height', totalH);
    const margin = { left: 8, right: 8 };
    const innerW = w - margin.left - margin.right;
    const x = d3
      .scaleTime()
      .domain(d3.extent(parsed, (d) => d._date))
      .range([0, innerW]);

    groups.forEach((g, gi) => {
      const y0 = gi * (panelH + gap);
      const pg = svg.append('g').attr('transform', `translate(${margin.left},${y0})`);
      pg.append('rect')
        .attr('width', innerW)
        .attr('height', panelH)
        .attr('rx', 4)
        .attr('fill', '#121c2e')
        .attr('stroke', '#2a3b5c');
      pg.append('text')
        .attr('x', 8)
        .attr('y', 14)
        .attr('fill', '#8fa3c1')
        .attr('font-size', 10)
        .attr('font-weight', 600)
        .attr('letter-spacing', '0.08em')
        .text(g.title.toUpperCase());

      g.series.forEach((s) => {
        const vals = parsed.map((d) => +d[s.k]).filter((v) => !isNaN(v));
        const ys = d3
          .scaleLinear()
          .domain(d3.extent(vals))
          .range([panelH - 6, 20]);
        const line = d3
          .line()
          .x((d) => x(d._date))
          .y((d) => ys(+d[s.k]))
          .curve(d3.curveMonotoneX);
        pg.append('path')
          .datum(parsed)
          .attr('fill', 'none')
          .attr('stroke', s.c)
          .attr('stroke-width', 1.6)
          .attr('d', line);
      });

      // scrub line
      if (snapshot) {
        pg.append('line')
          .attr('x1', x(snapshot._date))
          .attr('x2', x(snapshot._date))
          .attr('y1', 16)
          .attr('y2', panelH - 4)
          .attr('stroke', '#3dd6c6')
          .attr('stroke-dasharray', '3,2')
          .attr('stroke-width', 1);
      }
    });
  }

  function drawTimeline() {
    // scrubber is HTML; nothing to draw
  }

  $: if (phase === 'ready' && snapshot) {
    // redraw scrub indicators
    if (chartsEl) drawCharts();
  }
</script>

{#if phase === 'loading'}
  <div class="load-screen">
    <div class="load-card panel">
      <div class="load-kicker">FLIGHT TEST ANALYSIS</div>
      <h1>{event?.name || 'Demo Test Flight — Tail 652'}</h1>
      <p class="load-sub mono">{event?.date ? new Date(event.date).toUTCString() : ''}</p>

      <div class="files">
        <div class="files-label">Associated data products</div>
        {#each FILES as f, i}
          <div class="file-row" class:active={loadStep >= i + 2}>
            <span class="dot" class:on={loadStep >= i + 2}></span>
            <span class="fname mono">{f.name}</span>
            <span class="frole">{f.role}</span>
          </div>
        {/each}
      </div>

      <ul class="log mono">
        {#each loadMessages as m}
          <li>{m}</li>
        {/each}
      </ul>

      <div class="bar">
        <div class="bar-fill" style="width: {((loadStep + 1) / 8) * 100}%"></div>
      </div>
    </div>
  </div>
{:else}
  <div class="station">
    <header class="station-header">
      <button class="ghost" on:click={back}>← Events</button>
      <div class="title-block">
        <div class="kicker">Open Arsenal · Flight Test</div>
        <h1>{event?.name || 'Tail 652'}</h1>
      </div>
      <div class="mono time">{snapshot?.timestamp?.replace('T', ' ').replace('Z', ' Z') || '—'}</div>
      <div class="header-actions">
        <button class="ghost" on:click={togglePlay}>{playing ? 'Pause' : 'Play'}</button>
      </div>
    </header>

    <!-- Timeline scrub -->
    <div class="timeline-wrap">
      <div
        class="timeline"
        bind:this={timelineEl}
        on:click={onTimelineClick}
        role="slider"
        aria-valuenow={currentIdx}
        tabindex="0"
      >
        <div class="timeline-track">
          <div class="timeline-fill" style="width: {progress * 100}%"></div>
          <div class="timeline-thumb" style="left: {progress * 100}%"></div>
        </div>
        <div class="timeline-labels mono">
          <span>{parsed[0]?._date?.toISOString().slice(11, 19) || ''}</span>
          <span>{parsed[parsed.length - 1]?._date?.toISOString().slice(11, 19) || ''}</span>
        </div>
      </div>
    </div>

    <main class="station-main">
      <!-- Left: key events / markers -->
      <aside class="panel side">
        <h2>Key events</h2>
        <ul class="events">
          <li>
            <span class="tag collect">T0</span>
            <div>
              <div>Mission start</div>
              <div class="mono muted">{parsed[0]?.timestamp?.slice(11, 19)}</div>
            </div>
          </li>
          <li>
            <span class="tag warn">SYS</span>
            <div>
              <div>Fuel pump anomaly</div>
              <div class="mono muted">~32% mission</div>
            </div>
          </li>
          <li>
            <span class="tag warn">SYS</span>
            <div>
              <div>Oil pump momentary off</div>
              <div class="mono muted">~53% mission</div>
            </div>
          </li>
          <li>
            <span class="tag danger">HYD</span>
            <div>
              <div>Hydraulic pressure dip</div>
              <div class="mono muted">~62% mission</div>
            </div>
          </li>
          <li>
            <span class="tag verify">GEAR</span>
            <div>
              <div>Landing gear extension</div>
              <div class="mono muted">~82–88% mission</div>
            </div>
          </li>
        </ul>
      </aside>

      <!-- Center: map + charts -->
      <section class="center">
        <div class="panel map-panel">
          <div class="panel-title">Track · color by altitude</div>
          <div class="map" bind:this={mapEl}></div>
        </div>
        <div class="panel charts-panel">
          <div class="panel-title">Time-aligned parameters</div>
          <div class="charts" bind:this={chartsEl}></div>
        </div>
      </section>

      <!-- Right: status at scrub -->
      <aside class="panel side status">
        <h2>State at time</h2>
        {#if snapshot}
          <div class="metric">
            <span class="label">Altitude</span>
            <span class="value mono">{snapshot.altitude_ft?.toFixed?.(0) ?? snapshot.altitude_ft} ft</span>
          </div>
          <div class="metric">
            <span class="label">Airspeed</span>
            <span class="value mono">{snapshot.airspeed_kt?.toFixed?.(0) ?? snapshot.airspeed_kt} kt</span>
          </div>
          <div class="metric">
            <span class="label">Throttle</span>
            <span class="value mono">{snapshot.throttle_pct?.toFixed?.(0) ?? snapshot.throttle_pct}%</span>
          </div>
          <div class="metric">
            <span class="label">Engine RPM</span>
            <span class="value mono">{snapshot.engine_rpm}</span>
          </div>
          <div class="metric">
            <span class="label">Pitch / Roll</span>
            <span class="value mono"
              >{snapshot.pitch_deg?.toFixed?.(1)}° / {snapshot.roll_deg?.toFixed?.(1)}°</span
            >
          </div>
          <hr />
          <div class="metric">
            <span class="label">Landing gear</span>
            <span class="value mono" class:warn={snapshot.landing_gear === 2}
              >{gearLabel(snapshot.landing_gear)}</span
            >
          </div>
          <div class="metric">
            <span class="label">Fuel pump</span>
            <span class="value mono" class:danger={!snapshot.fuel_pump_on}
              >{onOff(snapshot.fuel_pump_on)}</span
            >
          </div>
          <div class="metric">
            <span class="label">Oil pump</span>
            <span class="value mono" class:danger={!snapshot.oil_pump_on}
              >{onOff(snapshot.oil_pump_on)}</span
            >
          </div>
          <div class="metric">
            <span class="label">Hydraulics</span>
            <span class="value mono" class:danger={!snapshot.hyd_system_ok}
              >{snapshot.hyd_system_ok ? 'OK' : 'FAULT'}</span
            >
          </div>
          <div class="metric">
            <span class="label">Master caution</span>
            <span class="value mono" class:danger={snapshot.master_caution}
              >{snapshot.master_caution ? 'ACTIVE' : 'CLEAR'}</span
            >
          </div>
          <div class="pos mono muted">
            {snapshot.latitude?.toFixed?.(4)}, {snapshot.longitude?.toFixed?.(4)}
          </div>
        {/if}
      </aside>
    </main>
  </div>
{/if}

<style>
  .load-screen {
    position: fixed;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    background: radial-gradient(800px 400px at 50% 30%, #16324f 0%, transparent 60%), #0b1220;
    z-index: 40;
    padding: 1.5rem;
  }
  .load-card {
    width: min(520px, 100%);
    border-radius: 6px;
    padding: 1.75rem 1.5rem;
  }
  .load-kicker {
    font-size: 10px;
    letter-spacing: 0.2em;
    color: var(--muted);
  }
  .load-card h1 {
    margin: 0.35rem 0 0.15rem;
    font-size: 1.35rem;
    font-weight: 600;
  }
  .load-sub {
    margin: 0 0 1.25rem;
    color: var(--accent);
    font-size: 0.8rem;
  }
  .files-label {
    font-size: 10px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.5rem;
  }
  .file-row {
    display: grid;
    grid-template-columns: 14px 1fr auto;
    gap: 0.5rem;
    align-items: center;
    padding: 0.35rem 0;
    opacity: 0.4;
    font-size: 0.85rem;
  }
  .file-row.active {
    opacity: 1;
  }
  .dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--line);
  }
  .dot.on {
    background: var(--verify);
    box-shadow: 0 0 8px rgba(93, 222, 160, 0.5);
  }
  .fname {
    color: var(--text);
  }
  .frole {
    color: var(--muted);
    font-size: 0.75rem;
  }
  .log {
    margin: 1rem 0;
    padding: 0.75rem;
    list-style: none;
    background: var(--bg-deep);
    border: 1px solid var(--line);
    border-radius: 4px;
    max-height: 140px;
    overflow: auto;
    font-size: 0.75rem;
    color: var(--muted);
  }
  .log li {
    padding: 0.15rem 0;
  }
  .log li:last-child {
    color: var(--accent);
  }
  .bar {
    height: 4px;
    background: var(--bg-deep);
    border-radius: 2px;
    overflow: hidden;
  }
  .bar-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--accent), var(--collect));
    transition: width 0.25s ease;
  }

  .station {
    position: fixed;
    inset: 0;
    display: flex;
    flex-direction: column;
    z-index: 30;
    background: transparent;
  }
  .station-header {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 0.75rem 1rem;
    padding: 0.65rem 1rem;
    border-bottom: 1px solid var(--line);
    background: color-mix(in srgb, var(--bg-panel) 90%, transparent);
  }
  .title-block .kicker {
    font-size: 10px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--muted);
  }
  .title-block h1 {
    margin: 0;
    font-size: 1.1rem;
    font-weight: 600;
  }
  .time {
    color: var(--accent);
    font-size: 0.9rem;
  }
  .header-actions {
    margin-left: auto;
    display: flex;
    gap: 0.5rem;
  }
  button.ghost {
    background: var(--bg-elevated);
    color: var(--text);
    border: 1px solid var(--line);
    border-radius: 3px;
    padding: 0.4rem 0.75rem;
    font-size: 0.85rem;
    cursor: pointer;
  }
  button.ghost:hover {
    border-color: var(--accent);
  }

  .timeline-wrap {
    padding: 0.65rem 1rem 0.25rem;
  }
  .timeline {
    cursor: pointer;
  }
  .timeline-track {
    position: relative;
    height: 10px;
    background: var(--bg-deep);
    border: 1px solid var(--line);
    border-radius: 4px;
  }
  .timeline-fill {
    position: absolute;
    inset: 0 auto 0 0;
    background: color-mix(in srgb, var(--accent) 45%, transparent);
    border-radius: 4px;
  }
  .timeline-thumb {
    position: absolute;
    top: 50%;
    width: 12px;
    height: 12px;
    margin-left: -6px;
    margin-top: -6px;
    border-radius: 50%;
    background: var(--accent);
    box-shadow: 0 0 0 2px var(--bg-deep);
  }
  .timeline-labels {
    display: flex;
    justify-content: space-between;
    font-size: 0.7rem;
    color: var(--muted);
    margin-top: 0.25rem;
  }

  .station-main {
    flex: 1;
    min-height: 0;
    display: grid;
    grid-template-columns: minmax(180px, 220px) 1fr minmax(200px, 240px);
    gap: 0.75rem;
    padding: 0.75rem 1rem 1rem;
    overflow: hidden;
  }
  @media (max-width: 960px) {
    .station-main {
      grid-template-columns: 1fr;
      overflow: auto;
    }
  }
  .side {
    border-radius: 4px;
    padding: 0.75rem;
    overflow: auto;
    min-height: 0;
  }
  .side h2 {
    margin: 0 0 0.75rem;
    font-size: 0.7rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--accent);
  }
  .events {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 0.55rem;
  }
  .events li {
    display: flex;
    gap: 0.5rem;
    font-size: 0.8rem;
  }
  .tag {
    flex-shrink: 0;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    padding: 0.15rem 0.35rem;
    border-radius: 3px;
    height: fit-content;
  }
  .tag.collect {
    background: rgba(77, 163, 255, 0.15);
    color: var(--collect);
  }
  .tag.warn {
    background: rgba(240, 193, 74, 0.15);
    color: var(--warn);
  }
  .tag.danger {
    background: rgba(255, 92, 108, 0.15);
    color: var(--danger);
  }
  .tag.verify {
    background: rgba(93, 222, 160, 0.15);
    color: var(--verify);
  }
  .muted {
    color: var(--muted);
    font-size: 0.7rem;
  }

  .center {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    min-height: 0;
    min-width: 0;
  }
  .map-panel,
  .charts-panel {
    border-radius: 4px;
    padding: 0.5rem 0.6rem 0.6rem;
    min-height: 0;
  }
  .map-panel {
    flex: 0 0 42%;
  }
  .charts-panel {
    flex: 1;
    overflow: auto;
  }
  .panel-title {
    font-size: 0.65rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.35rem;
  }
  .map {
    width: 100%;
    height: calc(100% - 1rem);
    min-height: 160px;
  }
  .charts {
    width: 100%;
  }

  .status .metric {
    display: flex;
    justify-content: space-between;
    gap: 0.5rem;
    padding: 0.35rem 0;
    border-bottom: 1px solid color-mix(in srgb, var(--line) 60%, transparent);
    font-size: 0.85rem;
  }
  .status .label {
    color: var(--muted);
  }
  .status .value {
    font-weight: 600;
  }
  .status .value.warn {
    color: var(--warn);
  }
  .status .value.danger {
    color: var(--danger);
  }
  .status hr {
    border: none;
    border-top: 1px solid var(--line);
    margin: 0.5rem 0;
  }
  .pos {
    margin-top: 0.75rem;
    font-size: 0.7rem;
  }
</style>
