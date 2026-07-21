<script>
  import { onMount, onDestroy } from 'svelte';
  import * as d3 from 'd3';

  /** @type {string} */
  export let apiBase = 'http://localhost:8000';
  /** @type {number | null} */
  export let fileId = null;
  /** @type {any[] | null} */
  export let initialData = null;

  let container;
  let svg;
  let tooltip;
  let data = [];
  let columns = [];
  let loading = false;
  let error = null;
  let selectedParams = [];
  let chartWidth = 900;
  let chartHeight = 420;

  // Color scale for parameters (nice aviation-ish palette)
  const colorScale = d3.scaleOrdinal()
    .domain(['altitude_ft', 'airspeed_kt', 'vertical_speed_fpm', 'pitch_deg', 'roll_deg', 'heading_deg', 'aoa_deg', 'g_force'])
    .range(['#1e40af', '#dc2626', '#059669', '#7c3aed', '#ea580c', '#0891b2', '#be185d', '#4b5563']);

  onMount(() => {
    if (initialData && initialData.length > 0) {
      data = initialData;
      columns = Object.keys(data[0] || {});
      initChart();
    } else if (fileId) {
      fetchData();
    }
  });

  onDestroy(() => {
    if (svg) {
      d3.select(svg).selectAll('*').remove();
    }
  });

  async function fetchData() {
    if (!fileId) return;
    loading = true;
    error = null;
    try {
      const res = await fetch(`${apiBase}/files/${fileId}/data?limit=2500`);
      if (!res.ok) throw new Error(await res.text());
      const json = await res.json();
      data = json.data || [];
      columns = json.columns || [];
      if (data.length === 0) throw new Error('No data returned');
      // Auto-select interesting flight test params
      const preferred = ['altitude_ft', 'airspeed_kt', 'pitch_deg', 'vertical_speed_fpm', 'roll_deg'];
      selectedParams = preferred.filter(p => columns.includes(p));
      if (selectedParams.length === 0) {
        selectedParams = columns.filter(c => c !== 'timestamp' && typeof data[0][c] === 'number').slice(0, 4);
      }
      initChart();
    } catch (e) {
      error = e.message || 'Failed to load flight data';
      console.error(e);
    } finally {
      loading = false;
    }
  }

  function initChart() {
    if (!container || data.length === 0) return;

    const margin = { top: 20, right: 120, bottom: 50, left: 70 };
    const width = chartWidth - margin.left - margin.right;
    const height = chartHeight - margin.top - margin.bottom;

    // Clear previous
    d3.select(container).selectAll('svg').remove();
    d3.select(container).selectAll('.tooltip').remove();

    svg = d3.select(container)
      .append('svg')
      .attr('width', chartWidth)
      .attr('height', chartHeight)
      .attr('viewBox', `0 0 ${chartWidth} ${chartHeight}`)
      .attr('preserveAspectRatio', 'xMidYMid meet');

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Parse timestamps
    const parseTime = d3.isoParse;
    data.forEach(d => {
      d._date = parseTime(d.timestamp) || new Date(d.timestamp);
    });

    const xExtent = d3.extent(data, d => d._date);
    const xScale = d3.scaleTime()
      .domain(xExtent)
      .range([0, width]);

    // Y scales per param or shared? For demo use individual or common normalized
    // Simple: shared y for demo (or per series later)
    const allValues = [];
    selectedParams.forEach(param => {
      data.forEach(d => { if (typeof d[param] === 'number') allValues.push(d[param]); });
    });
    const yExtent = d3.extent(allValues.length ? allValues : [0, 100]);
    const yScale = d3.scaleLinear()
      .domain([yExtent[0] * 0.95, yExtent[1] * 1.05])
      .range([height, 0]);

    // Axes
    const xAxis = d3.axisBottom(xScale).ticks(6).tickFormat(d3.timeFormat('%H:%M:%S'));
    const yAxis = d3.axisLeft(yScale).ticks(6);

    g.append('g')
      .attr('class', 'x-axis')
      .attr('transform', `translate(0,${height})`)
      .call(xAxis);

    g.append('g')
      .attr('class', 'y-axis')
      .call(yAxis);

    // Grid
    g.append('g')
      .attr('class', 'grid')
      .attr('opacity', 0.15)
      .call(d3.axisLeft(yScale).tickSize(-width).tickFormat(''));

    // Line generator
    const line = d3.line()
      .x(d => xScale(d._date))
      .y(d => yScale(d[param]))
      .curve(d3.curveMonotoneX);

    // Draw lines for selected params
    const linesGroup = g.append('g').attr('class', 'lines');

    function updateLines() {
      linesGroup.selectAll('path').remove();
      selectedParams.forEach((param, i) => {
        const linePath = linesGroup.append('path')
          .datum(data)
          .attr('fill', 'none')
          .attr('stroke', colorScale(param))
          .attr('stroke-width', 2.5)
          .attr('stroke-linejoin', 'round')
          .attr('stroke-linecap', 'round')
          .attr('d', d3.line()
            .x(d => xScale(d._date))
            .y(d => yScale(+d[param]))
            .curve(d3.curveMonotoneX)
          );
      });
    }

    updateLines();

    // Legend
    const legend = svg.append('g')
      .attr('transform', `translate(${width + margin.left + 10}, ${margin.top + 10})`);

    selectedParams.forEach((param, i) => {
      const yPos = i * 22;
      const item = legend.append('g').attr('transform', `translate(0, ${yPos})`);
      
      item.append('rect')
        .attr('width', 14)
        .attr('height', 14)
        .attr('fill', colorScale(param))
        .attr('rx', 2)
        .style('cursor', 'pointer')
        .on('click', () => toggleParam(param));
      
      item.append('text')
        .attr('x', 20)
        .attr('y', 11)
        .text(param.replace(/_/g, ' '))
        .style('font-size', '12px')
        .style('fill', '#333')
        .style('cursor', 'pointer')
        .on('click', () => toggleParam(param));
    });

    function toggleParam(param) {
      if (selectedParams.includes(param)) {
        selectedParams = selectedParams.filter(p => p !== param);
      } else {
        selectedParams = [...selectedParams, param];
      }
      // Re-render lines (simple way: re-init for now)
      initChart();
    }

    // Tooltip
    tooltip = d3.select(container)
      .append('div')
      .attr('class', 'tooltip')
      .style('position', 'absolute')
      .style('background', 'rgba(255,255,255,0.95)')
      .style('border', '1px solid #ccc')
      .style('border-radius', '4px')
      .style('padding', '8px 12px')
      .style('font-size', '12px')
      .style('pointer-events', 'none')
      .style('opacity', 0)
      .style('box-shadow', '0 2px 8px rgba(0,0,0,0.15)');

    const focus = g.append('g')
      .attr('class', 'focus')
      .style('display', 'none');

    focus.append('line')
      .attr('class', 'focus-line')
      .attr('y1', 0)
      .attr('y2', height)
      .attr('stroke', '#666')
      .attr('stroke-width', 1)
      .attr('stroke-dasharray', '3,3');

    const focusCircle = focus.append('circle')
      .attr('r', 4)
      .attr('fill', '#fff')
      .attr('stroke', '#333')
      .attr('stroke-width', 1.5);

    // Mouse interaction for tooltip
    const overlay = g.append('rect')
      .attr('width', width)
      .attr('height', height)
      .attr('fill', 'none')
      .attr('pointer-events', 'all');

    overlay
      .on('mouseover', () => focus.style('display', null))
      .on('mouseout', () => {
        focus.style('display', 'none');
        tooltip.style('opacity', 0);
      })
      .on('mousemove', function(event) {
        const [mx] = d3.pointer(event, this);
        const x0 = xScale.invert(mx);
        
        // Find closest point
        let closest = data[0];
        let minDist = Infinity;
        data.forEach(d => {
          const dist = Math.abs(d._date - x0);
          if (dist < minDist) {
            minDist = dist;
            closest = d;
          }
        });

        const xPos = xScale(closest._date);
        focus.attr('transform', `translate(${xPos},0)`);
        focusCircle.attr('cy', yScale(+closest[selectedParams[0]] || 0));

        // Tooltip content
        let html = `<strong>${closest.timestamp}</strong><br/>`;
        selectedParams.forEach(p => {
          if (closest[p] != null) {
            const val = typeof closest[p] === 'number' ? closest[p].toFixed(2) : closest[p];
            html += `${p.replace(/_/g,' ')}: <strong>${val}</strong><br/>`;
          }
        });
        tooltip.html(html)
          .style('left', `${event.pageX + 15}px`)
          .style('top', `${event.pageY - 10}px`)
          .style('opacity', 1);
      });

    // Simple zoom (wheel)
    const zoom = d3.zoom()
      .scaleExtent([0.5, 50])
      .on('zoom', (event) => {
        const newX = event.transform.rescaleX(xScale);
        g.select('.x-axis').call(xAxis.scale(newX));
        // Update lines with new scale (re-draw for simplicity)
        linesGroup.selectAll('path').attr('d', d3.line()
          .x(d => newX(d._date))
          .y(d => yScale(+d[selectedParams[0]] || 0)) // simplistic for multi
        );
      });

    svg.call(zoom);

    // X label
    g.append('text')
      .attr('x', width / 2)
      .attr('y', height + 40)
      .attr('text-anchor', 'middle')
      .style('font-size', '12px')
      .text('Time (UTC)');

    // Y label
    g.append('text')
      .attr('transform', 'rotate(-90)')
      .attr('x', -height / 2)
      .attr('y', -50)
      .attr('text-anchor', 'middle')
      .style('font-size', '12px')
      .text('Parameter Value');
  }

  function refreshPlot() {
    if (data.length > 0) initChart();
  }
</script>

<div bind:this={container} class="plot-container" style="position: relative; width: 100%; max-width: {chartWidth}px; margin: 1rem auto;">
  {#if loading}
    <div class="loading">Loading flight test data for D3 visualization...</div>
  {:else if error}
    <div class="error">{error}</div>
  {:else if data.length === 0}
    <div class="empty">No data loaded. Provide a fileId or initialData prop.</div>
  {/if}
</div>

<style>
  .plot-container {
    background: #fff;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 1rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  }
  .loading, .empty, .error {
    padding: 2rem;
    text-align: center;
    color: #666;
    font-style: italic;
  }
  .error { color: #dc2626; }
</style>
