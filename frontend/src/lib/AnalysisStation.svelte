<script>
  import { onMount, onDestroy, createEventDispatcher, tick } from 'svelte';
  import * as d3 from 'd3';
  import { generateDemoFlightSample } from './demoData.js';
  import FlightTrackMap from './FlightTrackMap.svelte';

  /** @type {{ id: number, name: string, date: string, files?: any[] }} */
  export let event = null;
  /** @type {any[]} */
  export let data = [];

  const dispatch = createEventDispatcher();

  const PARAM_GROUPS = [
    {
      id: 'perf',
      label: 'Performance',
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
        { key: 'g_force', label: 'G' }
      ]
    },
    {
      id: 'prop',
      label: 'Propulsion',
      params: [
        { key: 'throttle_pct', label: 'Throttle %' },
        { key: 'engine_rpm', label: 'RPM' },
        { key: 'fuel_flow_pph', label: 'Fuel flow' },
        { key: 'oil_pressure_psi', label: 'Oil psi' }
      ]
    },
    {
      id: 'disc',
      label: 'Subsystems',
      params: [
        { key: 'landing_gear', label: 'Landing gear' },
        { key: 'fuel_pump_on', label: 'Fuel pump' },
        { key: 'oil_pump_on', label: 'Oil pump' },
        { key: 'hyd_system_ok', label: 'Hydraulics' },
        { key: 'master_caution', label: 'Master caution' }
      ]
    }
  ];

  const ALL_PARAMS = PARAM_GROUPS.flatMap((g) => g.params);
  const COLORS = [
    '#4da3ff', '#ff7a45', '#5ddea0', '#f0c14a', '#a78bfa',
    '#fb923c', '#38bdf8', '#be185d', '#3dd6c6', '#ff5c6c'
  ];
  const PLOT_FORMATS = [
    { id: 'line', label: 'Multi-line' },
    { id: 'step', label: 'Step (digital)' },
    { id: 'area', label: 'Area' }
  ];

  const FILES = [
    { name: 'sample_flight_test_data.parquet', role: 'Primary telemetry' },
    { name: 'engine_bus.csv', role: 'Propulsion bus' },
    { name: 'subsystem_discretes.json', role: 'Digital discretes' }
  ];

  let phase = 'loading';
  let loadStep = 0;
  let loadMessages = [];
  let parsed = [];
  let currentIdx = 0;
  let playing = false;
  let playTimer = null;
  let panelEls = [];
  let timelineEl;

  // Analysis slides: the map overview (o-my-debrief layout) plus saved plot
  // configurations. Each plot slide is a stack of time-aligned panels so a
  // subsystem drop-out (discretes) can sit directly above the corresponding
  // instrumentation telemetry. The station opens on the map.
  let slides = [
    { id: 'map', name: 'Flight overview — map', type: 'map' },
    {
      id: 's1',
      name: 'Overview — performance',
      type: 'plot',
      t0: 0,
      t1: 1,
      panels: [
        {
          id: 'p1',
          params: ['altitude_ft', 'airspeed_kt', 'vertical_speed_fpm'],
          format: 'line'
        }
      ]
    },
    {
      id: 's2',
      name: 'Subsystem drop-outs',
      type: 'plot',
      t0: 0,
      t1: 1,
      panels: [
        {
          id: 'p2',
          params: ['master_caution', 'fuel_pump_on', 'oil_pump_on', 'hyd_system_ok'],
          format: 'step'
        },
        {
          id: 'p3',
          params: ['oil_pressure_psi', 'fuel_flow_pph', 'engine_rpm'],
          format: 'line'
        }
      ]
    }
  ];
  let activeSlideId = 'map';

  // Current plot builder state (bound to active slide): stacked panels sharing
  // one time snippet; the param/format controls edit the active panel.
  let panels = clonePanels(slides[1].panels);
  let activePanelId = panels[0].id;
  let rangeStart = 0; // fraction 0..1
  let rangeEnd = 1;

  function clonePanels(ps) {
    return ps.map((p) => ({ ...p, params: [...p.params] }));
  }
  const MIN_GAP = 0.02; // minimum snippet width as fraction of flight

  // Time snippet definition mode: end time entry or duration offset from start
  let snippetMode = 'duration'; // duration | end
  let durationUnit = 'sec'; // sec | min
  let draggingHandle = null; // 'start' | 'end' | null

  // Significant / anomalous events created by analyst
  let sigEvents = [];
  let selectedSigId = null;
  let showCapture = false;
  let captureSummary = '';
  let captureSeverity = 'anomaly'; // note | anomaly | critical

  // Right panel tab under slide selector
  let statusTab = 'state'; // state | files

  $: snapshot = parsed[currentIdx] || null;
  $: progress = parsed.length > 1 ? currentIdx / (parsed.length - 1) : 0;
  $: activeSlide = slides.find((s) => s.id === activeSlideId) || slides[0];
  $: activePanel = panels.find((p) => p.id === activePanelId) || panels[0];
  $: totalSeries = panels.reduce((n, p) => n + p.params.length, 0);
  $: flightStartMs = parsed[0]?._date?.getTime() ?? 0;
  $: flightSpanMs = Math.max(1, (parsed[parsed.length - 1]?._date?.getTime() ?? 0) - flightStartMs);
  $: startLabel = parsed.length ? fracToHMS(rangeStart) : '';
  $: endLabel = parsed.length ? fracToHMS(rangeEnd) : '';
  $: snippetSecs = ((rangeEnd - rangeStart) * flightSpanMs) / 1000;
  $: durationDisplay = durationUnit === 'min' ? +(snippetSecs / 60).toFixed(1) : Math.round(snippetSecs);
  $: isMapView = activeSlide?.type === 'map';

  // Flight overview stats for the map slide
  $: overview = parsed.length
    ? {
        duration: `${Math.round(flightSpanMs / 1000)}s`,
        maxAlt: Math.round(Math.max(...parsed.map((r) => r.altitude_ft))),
        maxSpd: Math.round(Math.max(...parsed.map((r) => r.airspeed_kt))),
        maxG: Math.max(...parsed.map((r) => r.g_force)).toFixed(2),
        trackNm: trackDistanceNm(parsed).toFixed(1),
        cautionSecs: Math.round(
          (parsed.filter((r) => r.master_caution).length / parsed.length) * (flightSpanMs / 1000)
        )
      }
    : null;

  function trackDistanceNm(rows) {
    let nm = 0;
    for (let i = 1; i < rows.length; i++) {
      const dLat = (rows[i].latitude - rows[i - 1].latitude) * 60;
      const dLon =
        (rows[i].longitude - rows[i - 1].longitude) *
        60 *
        Math.cos((rows[i].latitude * Math.PI) / 180);
      nm += Math.sqrt(dLat * dLat + dLon * dLon);
    }
    return nm;
  }
  $: windowData = (() => {
    if (!parsed.length) return [];
    const a = Math.floor(rangeStart * (parsed.length - 1));
    const b = Math.ceil(rangeEnd * (parsed.length - 1));
    return parsed.slice(Math.max(0, a), Math.min(parsed.length, b + 1));
  })();

  onMount(async () => {
    await runLoadingSequence();
  });

  onDestroy(() => {
    if (playTimer) clearInterval(playTimer);
    window.removeEventListener('pointermove', onHandleMove);
    window.removeEventListener('pointerup', endHandleDrag);
  });

  async function runLoadingSequence() {
    phase = 'loading';
    const steps = [
      `Selected event: ${event?.name || 'Demo Test Flight - Tail 652'}`,
      'Resolving associated data files…',
      `Loading ${FILES[0].name}`,
      `Loading ${FILES[1].name}`,
      `Loading ${FILES[2].name}`,
      'Building time index…',
      'Preparing analysis workspace…',
      'Analysis station ready'
    ];
    loadMessages = [];
    for (let i = 0; i < steps.length; i++) {
      loadStep = i;
      loadMessages = [...loadMessages, steps[i]];
      await sleep(260 + (i >= 2 && i <= 4 ? 160 : 0));
    }
    if (!data?.length) data = generateDemoFlightSample(240);
    parsed = data.map((d) => ({
      ...d,
      _date: d3.isoParse(d.timestamp) || new Date(d.timestamp)
    }));
    currentIdx = 0;
    phase = 'ready';
    await tick();
    drawPlots();
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
      drawPlots();
    }, 100);
  }

  function scrubTo(frac) {
    currentIdx = Math.round(frac * (parsed.length - 1));
    drawPlots();
  }

  function onTimelineClick(e) {
    const rect = timelineEl.getBoundingClientRect();
    scrubTo(Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width)));
  }

  async function selectSlide(id) {
    activeSlideId = id;
    const s = slides.find((x) => x.id === id);
    if (!s || s.type === 'map') return;
    panels = clonePanels(s.panels);
    activePanelId = panels[0].id;
    rangeStart = s.t0;
    rangeEnd = s.t1;
    await tick(); // plot containers mount when leaving the map view
    drawPlots();
  }

  function openPlots() {
    const firstPlot = slides.find((s) => s.type === 'plot');
    if (firstPlot) selectSlide(firstPlot.id);
  }

  function newSlide() {
    const id = 's' + Date.now();
    const s = {
      id,
      name: `Slide ${slides.filter((x) => x.type === 'plot').length + 1}`,
      type: 'plot',
      panels: clonePanels(panels),
      t0: rangeStart,
      t1: rangeEnd
    };
    slides = [...slides, s];
    selectSlide(id);
  }

  function saveSlideConfig() {
    // the map overview slide holds no plot configuration
    if (slides.find((s) => s.id === activeSlideId)?.type === 'map') return;
    slides = slides.map((s) =>
      s.id === activeSlideId
        ? {
            ...s,
            panels: clonePanels(panels),
            t0: rangeStart,
            t1: rangeEnd
          }
        : s
    );
  }

  function selectPanel(id) {
    activePanelId = id;
  }

  async function addPanel() {
    const id = 'p' + Date.now();
    panels = [...panels, { id, params: ['master_caution'], format: 'step' }];
    activePanelId = id;
    saveSlideConfig();
    await tick();
    drawPlots();
  }

  async function removePanel(id) {
    if (panels.length === 1) return;
    panels = panels.filter((p) => p.id !== id);
    if (activePanelId === id) activePanelId = panels[0].id;
    saveSlideConfig();
    await tick();
    drawPlots();
  }

  function toggleParam(key) {
    const p = activePanel;
    if (!p) return;
    if (p.params.includes(key)) {
      if (p.params.length === 1) return;
      p.params = p.params.filter((k) => k !== key);
    } else {
      p.params = [...p.params, key];
    }
    panels = panels;
    saveSlideConfig();
    drawPlots();
  }

  function setFormat(fmt) {
    if (!activePanel) return;
    activePanel.format = fmt;
    panels = panels;
    saveSlideConfig();
    drawPlots();
  }

  function setRange(which, val) {
    const v = Math.max(0, Math.min(1, +val));
    if (which === 'start') {
      rangeStart = Math.min(v, rangeEnd - MIN_GAP);
    } else {
      rangeEnd = Math.max(v, rangeStart + MIN_GAP);
    }
    saveSlideConfig();
    drawPlots();
  }

  function fracToHMS(frac) {
    return new Date(flightStartMs + frac * flightSpanMs).toISOString().slice(11, 19);
  }

  /** Parse "HH:MM:SS" (or "HH:MM") on the flight's UTC day → fraction of flight, or null. */
  function hmsToFrac(str) {
    const m = /^(\d{1,2}):(\d{2})(?::(\d{2}))?$/.exec(String(str).trim());
    if (!m || !parsed.length) return null;
    const d = new Date(flightStartMs);
    d.setUTCHours(+m[1], +m[2], +(m[3] || 0), 0);
    return Math.max(0, Math.min(1, (d.getTime() - flightStartMs) / flightSpanMs));
  }

  function onStartEntry(e) {
    const f = hmsToFrac(e.currentTarget.value);
    if (f == null) {
      e.currentTarget.value = startLabel;
      return;
    }
    if (snippetMode === 'duration') {
      // keep the duration offset, slide the whole window
      const width = Math.max(MIN_GAP, rangeEnd - rangeStart);
      rangeStart = Math.min(f, 1 - MIN_GAP);
      rangeEnd = Math.min(1, rangeStart + width);
    } else {
      rangeStart = Math.min(f, rangeEnd - MIN_GAP);
    }
    saveSlideConfig();
    drawPlots();
  }

  function onEndEntry(e) {
    const f = hmsToFrac(e.currentTarget.value);
    if (f == null) {
      e.currentTarget.value = endLabel;
      return;
    }
    rangeEnd = Math.max(f, rangeStart + MIN_GAP);
    saveSlideConfig();
    drawPlots();
  }

  function onDurationEntry(e) {
    const v = +e.currentTarget.value;
    if (!isFinite(v) || v <= 0) {
      e.currentTarget.value = durationDisplay;
      return;
    }
    const secs = durationUnit === 'min' ? v * 60 : v;
    const width = Math.max(MIN_GAP, (secs * 1000) / flightSpanMs);
    rangeEnd = Math.min(1, rangeStart + width);
    saveSlideConfig();
    drawPlots();
  }

  function resetSnippet() {
    rangeStart = 0;
    rangeEnd = 1;
    saveSlideConfig();
    drawPlots();
  }

  function startHandleDrag(which, e) {
    e.stopPropagation();
    e.preventDefault();
    draggingHandle = which;
    window.addEventListener('pointermove', onHandleMove);
    window.addEventListener('pointerup', endHandleDrag);
  }

  function onHandleMove(e) {
    if (!draggingHandle || !timelineEl) return;
    const rect = timelineEl.getBoundingClientRect();
    setRange(draggingHandle, (e.clientX - rect.left) / rect.width);
  }

  function endHandleDrag() {
    draggingHandle = null;
    window.removeEventListener('pointermove', onHandleMove);
    window.removeEventListener('pointerup', endHandleDrag);
  }

  function openCapture() {
    captureSummary = '';
    captureSeverity = 'anomaly';
    showCapture = true;
  }

  function confirmCapture() {
    if (!captureSummary.trim()) return;
    const id = 'e' + Date.now();
    const a = Math.floor(rangeStart * (parsed.length - 1));
    const b = Math.ceil(rangeEnd * (parsed.length - 1));
    const entry = {
      id,
      severity: captureSeverity,
      summary: captureSummary.trim(),
      panels: clonePanels(panels),
      t0: rangeStart,
      t1: rangeEnd,
      t0Label: parsed[a]?._date?.toISOString().slice(11, 19) || '',
      t1Label: parsed[b]?._date?.toISOString().slice(11, 19) || '',
      createdAt: new Date().toISOString()
    };
    sigEvents = [entry, ...sigEvents];
    selectedSigId = id;
    showCapture = false;
  }

  async function selectSig(ev) {
    selectedSigId = ev.id;
    // recalling a captured event opens the plots view
    if (isMapView) {
      const firstPlot = slides.find((s) => s.type === 'plot');
      if (firstPlot) activeSlideId = firstPlot.id;
    }
    panels = clonePanels(ev.panels);
    activePanelId = panels[0].id;
    rangeStart = ev.t0;
    rangeEnd = ev.t1;
    // also stamp onto active slide
    saveSlideConfig();
    await tick();
    drawPlots();
  }

  function deleteSig(id) {
    sigEvents = sigEvents.filter((e) => e.id !== id);
    if (selectedSigId === id) selectedSigId = null;
  }

  function gearLabel(v) {
    if (v === 2) return 'DOWN';
    if (v === 1) return 'TRANS';
    return 'UP';
  }
  function onOff(v) {
    return v ? 'ON' : 'OFF';
  }

  function drawPlots() {
    panels.forEach((panel, i) => {
      const el = panelEls[i];
      if (el) drawPanel(el, panel, i === panels.length - 1);
    });
  }

  function drawPanel(el, panel, showTimeAxis) {
    if (!el || !windowData.length) return;
    d3.select(el).selectAll('*').remove();
    const w = el.clientWidth || 700;
    const h = Math.max(140, el.clientHeight || 200);
    const margin = { top: 24, right: 16, bottom: showTimeAxis ? 32 : 8, left: 52 };
    const innerW = w - margin.left - margin.right;
    const innerH = h - margin.top - margin.bottom;

    const svg = d3
      .select(el)
      .append('svg')
      .attr('width', w)
      .attr('height', h);
    const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

    // shared time domain across all panels: the current snippet window
    const x = d3
      .scaleTime()
      .domain(d3.extent(windowData, (d) => d._date))
      .range([0, innerW]);

    g.append('g')
      .attr('transform', `translate(0,${innerH})`)
      .call(
        showTimeAxis
          ? d3.axisBottom(x).ticks(6).tickFormat(d3.timeFormat('%H:%M:%S'))
          : d3.axisBottom(x).ticks(6).tickFormat('')
      )
      .attr('color', '#8fa3c1');

    panel.params.forEach((key, i) => {
      const vals = windowData.map((d) => +d[key]).filter((v) => !isNaN(v));
      if (!vals.length) return;
      const y = d3.scaleLinear().domain(d3.extent(vals)).nice().range([innerH, 0]);
      const color = COLORS[i % COLORS.length];

      if (i === 0) {
        g.append('g')
          .call(d3.axisLeft(y).ticks(4).tickFormat(d3.format('~g')))
          .attr('color', '#8fa3c1');
        g.append('g')
          .attr('opacity', 0.12)
          .call(d3.axisLeft(y).tickSize(-innerW).tickFormat(''));
      }

      const curve =
        panel.format === 'step' ? d3.curveStepAfter : d3.curveMonotoneX;

      if (panel.format === 'area') {
        const area = d3
          .area()
          .x((d) => x(d._date))
          .y0(innerH)
          .y1((d) => y(+d[key]))
          .curve(curve);
        g.append('path')
          .datum(windowData)
          .attr('fill', color)
          .attr('opacity', 0.25)
          .attr('d', area);
      }

      const line = d3
        .line()
        .x((d) => x(d._date))
        .y((d) => y(+d[key]))
        .curve(curve);
      g.append('path')
        .datum(windowData)
        .attr('fill', 'none')
        .attr('stroke', color)
        .attr('stroke-width', 2)
        .attr('d', line);
    });

    // shared scrub cursor across all panels, if inside window
    if (snapshot && snapshot._date >= x.domain()[0] && snapshot._date <= x.domain()[1]) {
      g.append('line')
        .attr('x1', x(snapshot._date))
        .attr('x2', x(snapshot._date))
        .attr('y1', 0)
        .attr('y2', innerH)
        .attr('stroke', '#3dd6c6')
        .attr('stroke-dasharray', '4,3')
        .attr('stroke-width', 1.2);
    }

    // legend
    panel.params.forEach((key, i) => {
      const label = ALL_PARAMS.find((p) => p.key === key)?.label || key;
      const lx = i * 118;
      svg
        .append('rect')
        .attr('x', margin.left + lx)
        .attr('y', 6)
        .attr('width', 10)
        .attr('height', 10)
        .attr('rx', 2)
        .attr('fill', COLORS[i % COLORS.length]);
      svg
        .append('text')
        .attr('x', margin.left + lx + 14)
        .attr('y', 15)
        .attr('fill', '#8fa3c1')
        .attr('font-size', 11)
        .text(label);
    });
  }

  $: if (phase === 'ready' && panelEls.length) {
    // reactive redraw when window / panels change externally
    drawPlots();
  }
</script>

{#if phase === 'loading'}
  <div class="load-screen">
    <div class="load-card panel">
      <div class="load-kicker">FLIGHT TEST ANALYSIS</div>
      <h1>{event?.name || 'Demo Test Flight — Tail 652'}</h1>
      <p class="load-sub mono">{event?.date ? new Date(event.date).toUTCString() : ''}</p>
      <div class="files-label">Associated data products</div>
      {#each FILES as f, i}
        <div class="file-row" class:active={loadStep >= i + 2}>
          <span class="dot" class:on={loadStep >= i + 2}></span>
          <span class="fname mono">{f.name}</span>
          <span class="frole">{f.role}</span>
        </div>
      {/each}
      <ul class="log mono">
        {#each loadMessages as m}<li>{m}</li>{/each}
      </ul>
      <div class="bar"><div class="bar-fill" style="width: {((loadStep + 1) / 8) * 100}%"></div></div>
    </div>
  </div>
{:else}
  <div class="station">
    <header class="station-header">
      <button type="button" class="ghost" on:click={back}>← Events</button>
      <div class="title-block">
        <div class="kicker">Open Arsenal · Flight Test</div>
        <h1>{event?.name || 'Tail 652'}</h1>
      </div>
      <div class="mono time">{snapshot?.timestamp?.replace('T', ' ').replace('Z', '') || '—'}</div>
      <div class="header-actions">
        <button type="button" class="ghost" on:click={togglePlay}>{playing ? 'Pause' : 'Play'}</button>
        <button type="button" class="accent" on:click={openCapture}>Capture significant event</button>
      </div>
    </header>

    <div class="timeline-wrap">
      <div
        class="timeline"
        bind:this={timelineEl}
        on:click={onTimelineClick}
        role="slider"
        tabindex="0"
      >
        <div class="timeline-track">
          <div class="timeline-fill" style="width: {progress * 100}%"></div>
          <div class="timeline-thumb" style="left: {progress * 100}%"></div>
          <!-- window highlight -->
          <div
            class="timeline-window"
            style="left: {rangeStart * 100}%; width: {(rangeEnd - rangeStart) * 100}%"
          ></div>
          <!-- draggable snippet start / end handles -->
          <button
            type="button"
            class="timeline-handle start"
            class:dragging={draggingHandle === 'start'}
            style="left: {rangeStart * 100}%"
            title="Snippet start — drag to set ({startLabel})"
            aria-label="Snippet start"
            on:pointerdown={(e) => startHandleDrag('start', e)}
            on:click|stopPropagation
          >▶</button>
          <button
            type="button"
            class="timeline-handle end"
            class:dragging={draggingHandle === 'end'}
            style="left: {rangeEnd * 100}%"
            title="Snippet end — drag to set ({endLabel})"
            aria-label="Snippet end"
            on:pointerdown={(e) => startHandleDrag('end', e)}
            on:click|stopPropagation
          >◀</button>
        </div>
        <div class="timeline-labels mono">
          <span>{parsed[0]?._date?.toISOString().slice(11, 19) || ''}</span>
          <span>{parsed[parsed.length - 1]?._date?.toISOString().slice(11, 19) || ''}</span>
        </div>
      </div>
    </div>

    <main class="station-main">
      <!-- LEFT: significant / anomalous events -->
      <aside class="panel side">
        <h2>Significant / anomalous</h2>
        <p class="hint">Build a plot in the center, then capture it with a summary.</p>
        {#if !sigEvents.length}
          <p class="empty">No events yet. Configure the D3 view and click <em>Capture significant event</em>.</p>
        {:else}
          <ul class="sig-list">
            {#each sigEvents as ev}
              <li
                class:active={selectedSigId === ev.id}
                class={ev.severity}
              >
                <button type="button" class="sig-btn" on:click={() => selectSig(ev)}>
                  <span class="sev">{ev.severity}</span>
                  <span class="sum">{ev.summary}</span>
                  <span class="meta mono"
                    >{ev.t0Label}–{ev.t1Label} · {ev.panels.length} panel{ev.panels.length > 1 ? 's' : ''} · {ev.panels.reduce((n, p) => n + p.params.length, 0)} series</span
                  >
                </button>
                <button type="button" class="del" title="Remove" on:click={() => deleteSig(ev.id)}>×</button>
              </li>
            {/each}
          </ul>
        {/if}
      </aside>

      <!-- CENTER: flight overview map (default) or interactive D3 plot builder -->
      <section class="center panel">
        {#if isMapView}
          <div class="overview-bar">
            {#if overview}
              <div class="stat"><span class="ov-label">Duration</span><span class="ov-value mono">{overview.duration}</span></div>
              <div class="stat"><span class="ov-label">Max alt</span><span class="ov-value mono">{overview.maxAlt} ft</span></div>
              <div class="stat"><span class="ov-label">Max speed</span><span class="ov-value mono">{overview.maxSpd} kt</span></div>
              <div class="stat"><span class="ov-label">Max g</span><span class="ov-value mono">{overview.maxG}</span></div>
              <div class="stat"><span class="ov-label">Track</span><span class="ov-value mono">{overview.trackNm} nm</span></div>
              <div class="stat"><span class="ov-label">Caution</span><span class="ov-value mono" class:danger={overview.cautionSecs > 0}>{overview.cautionSecs}s</span></div>
            {/if}
            <button type="button" class="chip open-plots" on:click={openPlots}>Open data plots →</button>
          </div>
          <div class="map-wrap">
            <FlightTrackMap
              track={parsed}
              {currentIdx}
              {sigEvents}
              on:selectEvent={(e) => selectSig(e.detail)}
            />
          </div>
        {:else}
        <div class="builder-bar">
          <div class="editing-row">
            <span class="ctl-label">Editing</span>
            {#each panels as p, i (p.id)}
              <button
                type="button"
                class="chip"
                class:on={p.id === activePanelId}
                on:click={() => selectPanel(p.id)}>Panel {i + 1}</button
              >
            {/each}
            <button type="button" class="chip add" on:click={addPanel}>+ Add panel</button>
          </div>
          <div class="param-groups">
            {#each PARAM_GROUPS as group}
              <div class="pg">
                <span class="pg-label">{group.label}</span>
                <div class="chips">
                  {#each group.params as p}
                    <button
                      type="button"
                      class="chip"
                      class:on={activePanel?.params.includes(p.key)}
                      on:click={() => toggleParam(p.key)}
                    >
                      {p.label}
                    </button>
                  {/each}
                </div>
              </div>
            {/each}
          </div>
          <div class="builder-controls">
            <div class="fmt">
              <span class="ctl-label">Format</span>
              {#each PLOT_FORMATS as f}
                <button
                  type="button"
                  class="chip"
                  class:on={activePanel?.format === f.id}
                  on:click={() => setFormat(f.id)}>{f.label}</button
                >
              {/each}
            </div>
            <div class="snippet">
              <span class="ctl-label">Time snippet</span>
              <label class="mono snippet-field"
                >Start
                <input
                  class="time-in mono"
                  type="text"
                  inputmode="numeric"
                  placeholder="HH:MM:SS"
                  value={startLabel}
                  on:change={onStartEntry}
                />
              </label>
              <div class="mode-toggle" role="group" aria-label="Snippet end definition">
                <button
                  type="button"
                  class="chip"
                  class:on={snippetMode === 'duration'}
                  on:click={() => (snippetMode = 'duration')}>Duration</button
                >
                <button
                  type="button"
                  class="chip"
                  class:on={snippetMode === 'end'}
                  on:click={() => (snippetMode = 'end')}>End time</button
                >
              </div>
              {#if snippetMode === 'duration'}
                <label class="mono snippet-field"
                  >For
                  <input
                    class="dur-in mono"
                    type="number"
                    min="1"
                    step="any"
                    value={durationDisplay}
                    on:change={onDurationEntry}
                  />
                </label>
                <select
                  class="unit mono"
                  aria-label="Duration unit"
                  bind:value={durationUnit}
                >
                  <option value="sec">sec</option>
                  <option value="min">min</option>
                </select>
              {:else}
                <label class="mono snippet-field"
                  >End
                  <input
                    class="time-in mono"
                    type="text"
                    inputmode="numeric"
                    placeholder="HH:MM:SS"
                    value={endLabel}
                    on:change={onEndEntry}
                  />
                </label>
              {/if}
              <button type="button" class="chip" on:click={resetSnippet}>Full flight</button>
              <span class="snippet-summary mono">{startLabel}–{endLabel} · {Math.round(snippetSecs)}s</span>
            </div>
          </div>
        </div>
        <div class="panels-stack">
          {#each panels as panel, i (panel.id)}
            <div class="ppanel" class:on={panel.id === activePanelId}>
              <div class="ppanel-head">
                <button
                  type="button"
                  class="ppanel-title mono"
                  on:click={() => selectPanel(panel.id)}
                  title="Edit this panel"
                >
                  Panel {i + 1} · {panel.params.length} series · {panel.format}
                </button>
                {#if panels.length > 1}
                  <button
                    type="button"
                    class="del"
                    title="Remove panel"
                    on:click={() => removePanel(panel.id)}>×</button
                  >
                {/if}
              </div>
              <div class="ppanel-plot" bind:this={panelEls[i]}></div>
            </div>
          {/each}
        </div>
        {/if}
      </section>

      <!-- RIGHT: analysis slide selector + status -->
      <aside class="panel side status">
        <h2>Analysis slides</h2>
        <div class="slide-list">
          {#each slides as s}
            <button
              type="button"
              class="slide"
              class:on={s.id === activeSlideId}
              on:click={() => selectSlide(s.id)}
            >
              <span class="slide-name">{s.name}</span>
              <span class="mono muted"
                >{s.type === 'map'
                  ? 'ground track · overview'
                  : `${s.panels.length} panel${s.panels.length > 1 ? 's' : ''} · ${s.panels.reduce((n, p) => n + p.params.length, 0)} series`}</span
              >
            </button>
          {/each}
          <button type="button" class="slide add" on:click={newSlide}>+ New slide</button>
        </div>

        <div class="tabs">
          <button
            type="button"
            class:on={statusTab === 'state'}
            on:click={() => (statusTab = 'state')}>State</button
          >
          <button
            type="button"
            class:on={statusTab === 'files'}
            on:click={() => (statusTab = 'files')}>Files</button
          >
        </div>

        {#if statusTab === 'state' && snapshot}
          <div class="metric"><span class="label">Altitude</span><span class="value mono">{snapshot.altitude_ft?.toFixed?.(0)} ft</span></div>
          <div class="metric"><span class="label">Airspeed</span><span class="value mono">{snapshot.airspeed_kt?.toFixed?.(0)} kt</span></div>
          <div class="metric"><span class="label">Throttle</span><span class="value mono">{snapshot.throttle_pct?.toFixed?.(0)}%</span></div>
          <div class="metric"><span class="label">RPM</span><span class="value mono">{snapshot.engine_rpm}</span></div>
          <div class="metric"><span class="label">Gear</span><span class="value mono">{gearLabel(snapshot.landing_gear)}</span></div>
          <div class="metric"><span class="label">Fuel pump</span><span class="value mono" class:danger={!snapshot.fuel_pump_on}>{onOff(snapshot.fuel_pump_on)}</span></div>
          <div class="metric"><span class="label">Oil pump</span><span class="value mono" class:danger={!snapshot.oil_pump_on}>{onOff(snapshot.oil_pump_on)}</span></div>
          <div class="metric"><span class="label">Hydraulics</span><span class="value mono" class:danger={!snapshot.hyd_system_ok}>{snapshot.hyd_system_ok ? 'OK' : 'FAULT'}</span></div>
          <div class="metric"><span class="label">Caution</span><span class="value mono" class:danger={snapshot.master_caution}>{snapshot.master_caution ? 'ACTIVE' : 'CLEAR'}</span></div>
        {:else if statusTab === 'files'}
          {#each FILES as f}
            <div class="file-mini mono">{f.name}<span class="muted">{f.role}</span></div>
          {/each}
        {/if}
      </aside>
    </main>
  </div>

  {#if showCapture}
    <div class="modal-bg" on:click|self={() => (showCapture = false)}>
      <div class="modal panel">
        <h3>Capture significant / anomalous event</h3>
        <p class="hint">
          Saves current view: <strong>{panels.length} panel{panels.length > 1 ? 's' : ''}</strong> ·
          <strong>{totalSeries} series</strong>
          ({panels.map((p) => p.params.length + ' ' + p.format).join(' + ')}) · time window
          <span class="mono">{startLabel}–{endLabel} ({Math.round(snippetSecs)}s)</span>
        </p>
        <label class="field">
          Severity
          <select bind:value={captureSeverity}>
            <option value="note">Note</option>
            <option value="anomaly">Anomaly</option>
            <option value="critical">Critical</option>
          </select>
        </label>
        <label class="field">
          Summary
          <textarea
            rows="4"
            bind:value={captureSummary}
            placeholder="Brief description of what is significant in this window…"
          ></textarea>
        </label>
        <div class="modal-actions">
          <button type="button" class="ghost" on:click={() => (showCapture = false)}>Cancel</button>
          <button type="button" class="accent" on:click={confirmCapture}>Save event</button>
        </div>
      </div>
    </div>
  {/if}
{/if}

<style>
  .load-screen {
    position: fixed; inset: 0; display: flex; align-items: center; justify-content: center;
    background: radial-gradient(800px 400px at 50% 30%, #16324f 0%, transparent 60%), #0b1220;
    z-index: 40; padding: 1.5rem;
  }
  .load-card { width: min(520px, 100%); border-radius: 6px; padding: 1.75rem 1.5rem; }
  .load-kicker { font-size: 10px; letter-spacing: 0.2em; color: var(--muted); }
  .load-card h1 { margin: 0.35rem 0 0.15rem; font-size: 1.35rem; }
  .load-sub { margin: 0 0 1.25rem; color: var(--accent); font-size: 0.8rem; }
  .files-label { font-size: 10px; letter-spacing: 0.12em; text-transform: uppercase; color: var(--muted); margin-bottom: 0.5rem; }
  .file-row { display: grid; grid-template-columns: 14px 1fr auto; gap: 0.5rem; align-items: center; padding: 0.35rem 0; opacity: 0.4; font-size: 0.85rem; }
  .file-row.active { opacity: 1; }
  .dot { width: 8px; height: 8px; border-radius: 50%; background: var(--line); }
  .dot.on { background: var(--verify); box-shadow: 0 0 8px rgba(93,222,160,0.5); }
  .fname { color: var(--text); }
  .frole { color: var(--muted); font-size: 0.75rem; }
  .log { margin: 1rem 0; padding: 0.75rem; list-style: none; background: var(--bg-deep); border: 1px solid var(--line); border-radius: 4px; max-height: 140px; overflow: auto; font-size: 0.75rem; color: var(--muted); }
  .log li:last-child { color: var(--accent); }
  .bar { height: 4px; background: var(--bg-deep); border-radius: 2px; overflow: hidden; }
  .bar-fill { height: 100%; background: linear-gradient(90deg, var(--accent), var(--collect)); transition: width 0.25s ease; }

  .station { position: fixed; inset: 0; display: flex; flex-direction: column; z-index: 30; }
  .station-header {
    display: flex; flex-wrap: wrap; align-items: center; gap: 0.75rem 1rem;
    padding: 0.65rem 1rem; border-bottom: 1px solid var(--line);
    background: color-mix(in srgb, var(--bg-panel) 90%, transparent);
  }
  .title-block .kicker { font-size: 10px; letter-spacing: 0.18em; text-transform: uppercase; color: var(--muted); }
  .title-block h1 { margin: 0; font-size: 1.1rem; }
  .time { color: var(--accent); font-size: 0.9rem; }
  .header-actions { margin-left: auto; display: flex; gap: 0.5rem; }
  button.ghost, button.accent, button.chip, button.slide, button.sig-btn, button.del {
    font-family: inherit; cursor: pointer;
  }
  button.ghost {
    background: var(--bg-elevated); color: var(--text); border: 1px solid var(--line);
    border-radius: 3px; padding: 0.4rem 0.75rem; font-size: 0.85rem;
  }
  button.ghost:hover { border-color: var(--accent); }
  button.accent {
    background: color-mix(in srgb, var(--accent) 18%, transparent); color: var(--accent);
    border: 1px solid var(--accent); border-radius: 3px; padding: 0.4rem 0.75rem; font-size: 0.85rem; font-weight: 600;
  }

  .timeline-wrap { padding: 0.65rem 1rem 0.25rem; }
  .timeline { cursor: pointer; }
  .timeline-track { position: relative; height: 12px; background: var(--bg-deep); border: 1px solid var(--line); border-radius: 4px; }
  .timeline-fill { position: absolute; inset: 0 auto 0 0; background: color-mix(in srgb, var(--accent) 35%, transparent); border-radius: 4px; }
  .timeline-window {
    position: absolute; top: 0; bottom: 0;
    background: color-mix(in srgb, var(--collect) 22%, transparent);
    border-left: 1px solid var(--collect); border-right: 1px solid var(--collect);
    pointer-events: none;
  }
  .timeline-thumb {
    position: absolute; top: 50%; width: 12px; height: 12px; margin-left: -6px; margin-top: -6px;
    border-radius: 50%; background: var(--accent); box-shadow: 0 0 0 2px var(--bg-deep); z-index: 2;
  }
  .timeline-handle {
    position: absolute; top: -8px; height: 26px; width: 16px; margin-left: -8px;
    display: flex; align-items: center; justify-content: center; padding: 0;
    background: transparent; border: none; color: var(--collect);
    font-size: 9px; line-height: 1; cursor: ew-resize; z-index: 3;
    text-shadow: 0 0 4px rgba(0, 0, 0, 0.8);
  }
  .timeline-handle:hover, .timeline-handle.dragging { color: var(--accent); transform: scale(1.35); }
  .timeline-labels { display: flex; justify-content: space-between; font-size: 0.7rem; color: var(--muted); margin-top: 0.25rem; }

  .station-main {
    flex: 1; min-height: 0; display: grid;
    grid-template-columns: minmax(200px, 240px) 1fr minmax(210px, 250px);
    gap: 0.75rem; padding: 0.75rem 1rem 1rem; overflow: hidden;
  }
  @media (max-width: 1000px) { .station-main { grid-template-columns: 1fr; overflow: auto; } }
  .side { border-radius: 4px; padding: 0.75rem; overflow: auto; min-height: 0; }
  .side h2 { margin: 0 0 0.5rem; font-size: 0.7rem; letter-spacing: 0.14em; text-transform: uppercase; color: var(--accent); }
  .hint { margin: 0 0 0.75rem; font-size: 0.75rem; color: var(--muted); line-height: 1.35; }
  .empty { font-size: 0.8rem; color: var(--muted); }

  .sig-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 0.4rem; }
  .sig-list li { display: flex; gap: 0.25rem; align-items: stretch; }
  .sig-list li.active .sig-btn { border-color: var(--accent); }
  .sig-btn {
    flex: 1; text-align: left; background: var(--bg-deep); border: 1px solid var(--line);
    border-radius: 4px; padding: 0.45rem 0.5rem; color: var(--text);
  }
  .sig-btn:hover { border-color: var(--muted); }
  .sev {
    display: inline-block; font-size: 0.65rem; font-weight: 700; letter-spacing: 0.06em;
    text-transform: uppercase; margin-bottom: 0.2rem;
  }
  .anomaly .sev { color: var(--warn); }
  .critical .sev { color: var(--danger); }
  .note .sev { color: var(--collect); }
  .sum { display: block; font-size: 0.82rem; }
  .meta { display: block; font-size: 0.68rem; color: var(--muted); margin-top: 0.2rem; }
  .del {
    background: transparent; border: 1px solid var(--line); color: var(--muted);
    border-radius: 4px; width: 28px; font-size: 1rem;
  }
  .del:hover { color: var(--danger); border-color: var(--danger); }

  .center { border-radius: 4px; padding: 0.55rem 0.65rem 0.65rem; display: flex; flex-direction: column; min-height: 0; min-width: 0; }
  .overview-bar {
    flex-shrink: 0; display: flex; flex-wrap: wrap; align-items: center;
    gap: 0.4rem 1.1rem; margin-bottom: 0.5rem; padding: 0.35rem 0.5rem;
    background: var(--bg-deep); border: 1px solid var(--line); border-radius: 4px;
  }
  .stat { display: flex; flex-direction: column; gap: 0.05rem; }
  .ov-label { font-size: 0.6rem; letter-spacing: 0.1em; text-transform: uppercase; color: var(--muted); }
  .ov-value { font-size: 0.85rem; font-weight: 600; }
  .ov-value.danger { color: var(--danger); }
  .open-plots { margin-left: auto; }
  .map-wrap { flex: 1; min-height: 0; display: flex; }
  .builder-bar { flex-shrink: 0; margin-bottom: 0.5rem; }
  .param-groups { display: flex; flex-direction: column; gap: 0.35rem; margin-bottom: 0.45rem; }
  .pg { display: flex; flex-wrap: wrap; align-items: center; gap: 0.35rem 0.5rem; }
  .pg-label { font-size: 0.65rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted); width: 72px; }
  .chips { display: flex; flex-wrap: wrap; gap: 0.3rem; }
  .chip {
    background: var(--bg-deep); border: 1px solid var(--line); color: var(--muted);
    border-radius: 999px; padding: 0.2rem 0.55rem; font-size: 0.72rem;
  }
  .chip.on { border-color: var(--accent); color: var(--accent); background: color-mix(in srgb, var(--accent) 12%, transparent); }
  .builder-controls { display: flex; flex-wrap: wrap; gap: 0.75rem 1.25rem; align-items: center; }
  .ctl-label { font-size: 0.65rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted); margin-right: 0.35rem; }
  .fmt, .snippet { display: flex; flex-wrap: wrap; align-items: center; gap: 0.35rem; }
  .snippet-field { display: flex; align-items: center; gap: 0.35rem; font-size: 0.72rem; color: var(--muted); }
  .time-in, .dur-in, .unit {
    background: var(--bg-deep); border: 1px solid var(--line); color: var(--text);
    border-radius: 3px; padding: 0.22rem 0.4rem; font-size: 0.75rem;
  }
  .time-in { width: 84px; }
  .time-in:focus, .dur-in:focus, .unit:focus { outline: none; border-color: var(--accent); }
  .dur-in { width: 60px; }
  .unit { padding-right: 0.2rem; }
  .mode-toggle { display: flex; gap: 0.25rem; }
  .snippet-summary { font-size: 0.7rem; color: var(--collect); }
  .editing-row { display: flex; flex-wrap: wrap; align-items: center; gap: 0.3rem; margin-bottom: 0.4rem; }
  .editing-row .chip.add { border-style: dashed; }
  .panels-stack { flex: 1; min-height: 0; display: flex; flex-direction: column; gap: 0.45rem; overflow: auto; }
  .ppanel {
    flex: 1; min-height: 150px; display: flex; flex-direction: column;
    background: var(--bg-deep); border: 1px solid var(--line); border-radius: 4px;
  }
  .ppanel.on { border-color: var(--accent); }
  .ppanel-head {
    display: flex; align-items: center; gap: 0.25rem;
    padding: 0.15rem 0.3rem; border-bottom: 1px solid color-mix(in srgb, var(--line) 55%, transparent);
  }
  .ppanel-title {
    flex: 1; text-align: left; background: transparent; border: none; cursor: pointer;
    color: var(--muted); font-size: 0.68rem; padding: 0.15rem 0.25rem;
  }
  .ppanel.on .ppanel-title { color: var(--accent); }
  .ppanel-plot { flex: 1; min-height: 120px; }

  .slide-list { display: flex; flex-direction: column; gap: 0.35rem; margin-bottom: 0.75rem; }
  .slide {
    text-align: left; background: var(--bg-deep); border: 1px solid var(--line); border-radius: 4px;
    padding: 0.45rem 0.55rem; color: var(--text); display: flex; flex-direction: column; gap: 0.15rem;
  }
  .slide.on { border-color: var(--accent); background: color-mix(in srgb, var(--accent) 10%, var(--bg-deep)); }
  .slide.add { color: var(--muted); border-style: dashed; }
  .slide-name { font-size: 0.85rem; font-weight: 600; }
  .muted { color: var(--muted); font-size: 0.7rem; }
  .tabs { display: flex; gap: 0.25rem; margin-bottom: 0.6rem; }
  .tabs button {
    flex: 1; background: var(--bg-deep); border: 1px solid var(--line); color: var(--muted);
    border-radius: 3px; padding: 0.3rem; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.06em;
  }
  .tabs button.on { border-color: var(--accent); color: var(--accent); }
  .metric {
    display: flex; justify-content: space-between; gap: 0.5rem; padding: 0.3rem 0;
    border-bottom: 1px solid color-mix(in srgb, var(--line) 55%, transparent); font-size: 0.82rem;
  }
  .metric .label { color: var(--muted); }
  .metric .value { font-weight: 600; }
  .metric .value.danger { color: var(--danger); }
  .file-mini { font-size: 0.75rem; padding: 0.35rem 0; border-bottom: 1px solid var(--line); display: flex; flex-direction: column; gap: 0.1rem; }

  .modal-bg {
    position: fixed; inset: 0; background: rgba(0,0,0,0.55); z-index: 50;
    display: flex; align-items: center; justify-content: center; padding: 1rem;
  }
  .modal { width: min(440px, 100%); border-radius: 6px; padding: 1.25rem; }
  .modal h3 { margin: 0 0 0.5rem; font-size: 1rem; color: var(--accent); }
  .field { display: flex; flex-direction: column; gap: 0.35rem; margin: 0.75rem 0; font-size: 0.8rem; color: var(--muted); }
  .field select, .field textarea {
    background: var(--bg-deep); border: 1px solid var(--line); color: var(--text);
    border-radius: 4px; padding: 0.5rem; font-family: inherit; font-size: 0.9rem;
  }
  .modal-actions { display: flex; justify-content: flex-end; gap: 0.5rem; margin-top: 0.5rem; }
  .mono { font-family: var(--font-mono); }
</style>
