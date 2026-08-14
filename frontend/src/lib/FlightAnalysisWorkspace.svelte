<script>
  import { onMount, onDestroy } from 'svelte';
  import * as d3 from 'd3';

  /** @type {any[]} */
  export let data = [];

  let rootEl;
  let width = 960;
  const margin = { top: 8, right: 16, bottom: 28, left: 52 };
  const panelH = 88;
  const mapH = 140;
  const discreteH = 110;
  const gap = 10;

  const panels = [
    {
      id: 'perf',
      title: 'Performance',
      series: [
        { key: 'altitude_ft', label: 'Altitude (ft)', color: '#1e40af' },
        { key: 'airspeed_kt', label: 'Airspeed (kt)', color: '#dc2626' },
        { key: 'vertical_speed_fpm', label: 'VS (fpm)', color: '#059669' }
      ]
    },
    {
      id: 'att',
      title: 'Attitude',
      series: [
        { key: 'pitch_deg', label: 'Pitch (°)', color: '#7c3aed' },
        { key: 'roll_deg', label: 'Roll (°)', color: '#ea580c' },
        { key: 'aoa_deg', label: 'AoA (°)', color: '#0891b2' }
      ]
    },
    {
      id: 'prop',
      title: 'Propulsion',
      series: [
        { key: 'throttle_pct', label: 'Throttle %', color: '#b45309' },
        { key: 'engine_rpm', label: 'RPM', color: '#be185d' },
        { key: 'fuel_flow_pph', label: 'Fuel flow', color: '#0f766e' }
      ]
    }
  ];

  const discreteSeries = [
    { key: 'landing_gear', label: 'Landing gear', color: '#334155', levels: 3 },
    { key: 'fuel_pump_on', label: 'Fuel pump', color: '#1d4ed8', levels: 2 },
    { key: 'oil_pump_on', label: 'Oil pump', color: '#b45309', levels: 2 },
    { key: 'hyd_system_ok', label: 'Hydraulics OK', color: '#059669', levels: 2 },
    { key: 'master_caution', label: 'Master caution', color: '#dc2626', levels: 2 }
  ];

  let parsed = [];
  let xScale;
  let brushDomain = null;
  let cursorTime = null;

  onMount(() => {
    if (data?.length) render();
    const ro = new ResizeObserver(() => {
      if (rootEl) {
        width = Math.max(640, rootEl.clientWidth - 8);
        render();
      }
    });
    if (rootEl) ro.observe(rootEl);
    return () => ro.disconnect();
  });

  $: if (data?.length && rootEl) {
    parsed = data.map((d) => ({
      ...d,
      _date: d3.isoParse(d.timestamp) || new Date(d.timestamp)
    }));
    render();
  }

  function render() {
    if (!rootEl || !parsed.length) return;
    d3.select(rootEl).selectAll('svg.workspace').remove();

    const innerW = width - margin.left - margin.right;
    const totalH =
      mapH + gap + panels.length * (panelH + gap) + discreteH + gap + 36;

    const svg = d3
      .select(rootEl)
      .append('svg')
      .attr('class', 'workspace')
      .attr('width', width)
      .attr('height', totalH);

    const fullX = d3.extent(parsed, (d) => d._date);
    const domain = brushDomain || fullX;
    xScale = d3.scaleTime().domain(domain).range([0, innerW]);

    const filtered = parsed.filter(
      (d) => d._date >= domain[0] && d._date <= domain[1]
    );

    let y = margin.top;

    // ---- MAP ----
    drawMap(svg, filtered, innerW, y);
    y += mapH + gap;

    // ---- CONTINUOUS PANELS ----
    panels.forEach((p) => {
      drawContinuousPanel(svg, p, filtered, innerW, y);
      y += panelH + gap;
    });

    // ---- DISCRETE ----
    drawDiscretePanel(svg, filtered, innerW, y);
    y += discreteH + gap;

    // ---- BRUSH ----
    const brushG = svg
      .append('g')
      .attr('transform', `translate(${margin.left},${y})`);

    const brushX = d3.scaleTime().domain(fullX).range([0, innerW]);
    brushG
      .append('g')
      .attr('transform', `translate(0,20)`)
      .call(d3.axisBottom(brushX).ticks(6).tickFormat(d3.timeFormat('%H:%M:%S')));

    const brush = d3
      .brushX()
      .extent([
        [0, 0],
        [innerW, 18]
      ])
      .on('end', (event) => {
        if (!event.selection) {
          brushDomain = null;
        } else {
          brushDomain = event.selection.map(brushX.invert);
        }
        render();
      });
    brushG.call(brush);

    // cursor line layer
    const cursorLayer = svg.append('g').attr('class', 'cursor-layer');
    svg
      .append('rect')
      .attr('x', margin.left)
      .attr('y', margin.top)
      .attr('width', innerW)
      .attr('height', totalH - margin.top - 40)
      .attr('fill', 'transparent')
      .on('mousemove', function (event) {
        const [mx] = d3.pointer(event, this);
        const t = xScale.invert(mx - margin.left);
        cursorTime = t;
        cursorLayer.selectAll('*').remove();
        cursorLayer
          .append('line')
          .attr('x1', margin.left + xScale(t))
          .attr('x2', margin.left + xScale(t))
          .attr('y1', margin.top)
          .attr('y2', totalH - 40)
          .attr('stroke', '#64748b')
          .attr('stroke-dasharray', '4,3')
          .attr('stroke-width', 1);
      })
      .on('mouseleave', () => {
        cursorLayer.selectAll('*').remove();
        cursorTime = null;
      });
  }

  function drawMap(svg, filtered, innerW, y0) {
    const g = svg
      .append('g')
      .attr('transform', `translate(${margin.left},${y0})`);

    g.append('rect')
      .attr('width', innerW)
      .attr('height', mapH)
      .attr('fill', '#f8fafc')
      .attr('stroke', '#e2e8f0')
      .attr('rx', 4);

    g.append('text')
      .attr('x', 8)
      .attr('y', 16)
      .attr('font-size', 11)
      .attr('font-weight', 600)
      .attr('fill', '#334155')
      .text('Track (lat / lon) — color by altitude');

    if (filtered.length < 2) return;

    const x = d3
      .scaleLinear()
      .domain(d3.extent(filtered, (d) => d.longitude))
      .range([12, innerW - 12]);
    const y = d3
      .scaleLinear()
      .domain(d3.extent(filtered, (d) => d.latitude))
      .range([mapH - 12, 24]);
    const color = d3
      .scaleSequential(d3.interpolateTurbo)
      .domain(d3.extent(filtered, (d) => d.altitude_ft));

    const line = d3
      .line()
      .x((d) => x(d.longitude))
      .y((d) => y(d.latitude))
      .curve(d3.curveCatmullRom);

    // colored segments
    for (let i = 1; i < filtered.length; i++) {
      g.append('path')
        .datum([filtered[i - 1], filtered[i]])
        .attr('fill', 'none')
        .attr('stroke', color(filtered[i].altitude_ft))
        .attr('stroke-width', 2.5)
        .attr('d', line);
    }

    // start / end markers
    const last = filtered[filtered.length - 1];
    g.append('circle')
      .attr('cx', x(filtered[0].longitude))
      .attr('cy', y(filtered[0].latitude))
      .attr('r', 4)
      .attr('fill', '#16a34a');
    g.append('circle')
      .attr('cx', x(last.longitude))
      .attr('cy', y(last.latitude))
      .attr('r', 5)
      .attr('fill', '#dc2626')
      .attr('stroke', '#fff')
      .attr('stroke-width', 1.5);
  }

  function drawContinuousPanel(svg, panel, filtered, innerW, y0) {
    const g = svg
      .append('g')
      .attr('transform', `translate(${margin.left},${y0})`);

    g.append('rect')
      .attr('width', innerW)
      .attr('height', panelH)
      .attr('fill', '#fff')
      .attr('stroke', '#e2e8f0')
      .attr('rx', 4);

    g.append('text')
      .attr('x', 8)
      .attr('y', 14)
      .attr('font-size', 11)
      .attr('font-weight', 600)
      .attr('fill', '#334155')
      .text(panel.title);

    // legend
    panel.series.forEach((s, i) => {
      const lx = innerW - 200 + i * 68;
      g.append('rect')
        .attr('x', lx)
        .attr('y', 4)
        .attr('width', 10)
        .attr('height', 10)
        .attr('fill', s.color)
        .attr('rx', 2);
      g.append('text')
        .attr('x', lx + 14)
        .attr('y', 13)
        .attr('font-size', 9)
        .attr('fill', '#475569')
        .text(s.label);
    });

    const plotTop = 20;
    const plotH = panelH - plotTop - 4;

    // Independent normalized overlay for mixed units (demo clarity)
    panel.series.forEach((s) => {
      const vals = filtered.map((d) => +d[s.key]).filter((v) => !isNaN(v));
      if (!vals.length) return;
      const yScale = d3
        .scaleLinear()
        .domain(d3.extent(vals))
        .nice()
        .range([plotH, 0]);

      const line = d3
        .line()
        .x((d) => xScale(d._date))
        .y((d) => yScale(+d[s.key]))
        .curve(d3.curveMonotoneX)
        .defined((d) => d[s.key] != null);

      g.append('path')
        .datum(filtered)
        .attr('fill', 'none')
        .attr('stroke', s.color)
        .attr('stroke-width', 1.8)
        .attr('transform', `translate(0,${plotTop})`)
        .attr('d', line);
    });

    // light x grid
    g.append('g')
      .attr('transform', `translate(0,${panelH - 4})`)
      .attr('opacity', 0.3)
      .call(
        d3
          .axisBottom(xScale)
          .ticks(5)
          .tickSize(-plotH)
          .tickFormat('')
      );
  }

  function drawDiscretePanel(svg, filtered, innerW, y0) {
    const g = svg
      .append('g')
      .attr('transform', `translate(${margin.left},${y0})`);

    g.append('rect')
      .attr('width', innerW)
      .attr('height', discreteH)
      .attr('fill', '#fff')
      .attr('stroke', '#e2e8f0')
      .attr('rx', 4);

    g.append('text')
      .attr('x', 8)
      .attr('y', 14)
      .attr('font-size', 11)
      .attr('font-weight', 600)
      .attr('fill', '#334155')
      .text('Subsystem states (digital)');

    const rowH = (discreteH - 22) / discreteSeries.length;

    discreteSeries.forEach((s, si) => {
      const rowY = 20 + si * rowH;
      g.append('text')
        .attr('x', 8)
        .attr('y', rowY + rowH * 0.65)
        .attr('font-size', 9)
        .attr('fill', '#64748b')
        .text(s.label);

      const yScale = d3
        .scaleLinear()
        .domain([0, s.levels - 1])
        .range([rowY + rowH - 4, rowY + 4]);

      const step = d3
        .line()
        .x((d) => xScale(d._date))
        .y((d) => yScale(+d[s.key] || 0))
        .curve(d3.curveStepAfter);

      g.append('path')
        .datum(filtered)
        .attr('fill', 'none')
        .attr('stroke', s.color)
        .attr('stroke-width', 1.6)
        .attr('d', step);
    });
  }
</script>

<div class="workspace-root" bind:this={rootEl}>
  {#if !data || data.length === 0}
    <p class="empty">No flight data loaded for analysis.</p>
  {/if}
</div>

<style>
  .workspace-root {
    width: 100%;
    overflow-x: auto;
    background: #f1f5f9;
    border-radius: 8px;
    padding: 0.5rem;
  }
  .empty {
    padding: 2rem;
    text-align: center;
    color: #64748b;
  }
  :global(.workspace) {
    display: block;
    max-width: 100%;
  }
</style>
