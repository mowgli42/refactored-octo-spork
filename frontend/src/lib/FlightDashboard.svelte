<script>
  import { onMount } from 'svelte';
  import FlightAnalysisWorkspace from './FlightAnalysisWorkspace.svelte';
  import { generateDemoFlightSample, demoEvent } from './demoData.js';
  import { API_BASE } from './api.js';

  let events = [];
  let loading = true;
  let error = null;
  let showAnalysis = false;
  let analysisData = [];

  const isDemoMode = import.meta.env.VITE_DEMO_MODE === 'true' || true; // force demo for Vercel slice

  onMount(() => {
    if (isDemoMode) {
      events = [demoEvent];
      analysisData = generateDemoFlightSample(220);
      loading = false;
    } else {
      // Full mode would fetch from API — not used on Vercel demo
      loading = false;
      error = 'Backend not configured. Use local full stack or enable VITE_DEMO_MODE.';
    }
  });

  function openAnalysis() {
    if (!analysisData.length) {
      analysisData = generateDemoFlightSample(220);
    }
    showAnalysis = true;
  }

  function closeAnalysis() {
    showAnalysis = false;
  }

  function getStatusColor(status) {
    if (!status) return 'bg-gray-100';
    switch (String(status).toLowerCase()) {
      case 'complete':
      case 'ready':
        return 'bg-green-100';
      case 'processing':
        return 'bg-blue-100';
      case 'error':
        return 'bg-red-100';
      default:
        return 'bg-gray-100';
    }
  }
</script>

<div class="container">
  <div class="header">
    <div>
      <h1>Flight Test Analysis {isDemoMode ? '— Demo' : ''}</h1>
      <p class="subtitle">
        Time-aligned multi-panel workspace · Map track · Performance · Attitude · Propulsion · Subsystem states
      </p>
    </div>
    <button class="primary" on:click={openAnalysis}>
      Open Analysis Workspace
    </button>
  </div>

  {#if isDemoMode}
    <div class="demo-banner">
      <strong>Demo mode</strong> — Fixed sample flight (Tail 652). Data import and uploads are disabled.
      Use the analysis workspace to explore altitude, speed, throttle, gear, pumps, and hydraulics time-aligned.
    </div>
  {/if}

  {#if loading}
    <p>Loading…</p>
  {:else if error}
    <p class="error">{error}</p>
  {:else}
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Date</th>
            <th>Import</th>
            <th>Parse</th>
            <th>Analysis</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {#each events as event}
            <tr>
              <td>{event.id}</td>
              <td>{event.name}</td>
              <td>{new Date(event.date).toLocaleString()}</td>
              <td><span class="badge {getStatusColor(event.import_status)}">{event.import_status}</span></td>
              <td><span class="badge {getStatusColor(event.parse_status)}">{event.parse_status}</span></td>
              <td><span class="badge {getStatusColor(event.analysis_status)}">{event.analysis_status}</span></td>
              <td>
                <button class="small primary" on:click={openAnalysis}>Analyze</button>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>

    <div class="hints">
      <h3>What you can inspect in this demo</h3>
      <ul>
        <li><strong>Map</strong> — aircraft track colored by altitude</li>
        <li><strong>Performance</strong> — altitude, airspeed, vertical speed</li>
        <li><strong>Attitude</strong> — pitch, roll, angle of attack</li>
        <li><strong>Propulsion</strong> — throttle %, engine RPM, fuel flow</li>
        <li><strong>Subsystems</strong> — landing gear, fuel/oil pumps, hydraulics, master caution (digital traces)</li>
        <li>Brush the bottom time axis to zoom a region; hover for a shared vertical cursor</li>
      </ul>
    </div>
  {/if}

  {#if showAnalysis}
    <div class="modal-backdrop" on:click|self={closeAnalysis}>
      <div class="modal large" on:click|stopPropagation>
        <div class="modal-header">
          <h2>Flight Test Analysis Workspace — Tail 652</h2>
          <button class="secondary" on:click={closeAnalysis}>Close</button>
        </div>
        <FlightAnalysisWorkspace data={analysisData} />
        <p class="modal-foot">
          Brush bottom axis to zoom · Hover for time cursor · Discrete panel uses step traces for subsystem states
        </p>
      </div>
    </div>
  {/if}
</div>

<style>
  .container {
    max-width: 1100px;
    margin: 0 auto;
    padding: 1.5rem;
    font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
    color: #0f172a;
  }
  .header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 1rem;
    margin-bottom: 1rem;
  }
  h1 {
    margin: 0 0 0.25rem;
    font-size: 1.5rem;
  }
  .subtitle {
    margin: 0;
    color: #64748b;
    font-size: 0.9rem;
  }
  .demo-banner {
    background: #f0fdf4;
    border: 1px solid #86efac;
    border-radius: 8px;
    padding: 0.85rem 1rem;
    margin-bottom: 1.25rem;
    font-size: 0.9rem;
  }
  button {
    border: none;
    border-radius: 6px;
    padding: 0.5rem 1rem;
    font-weight: 500;
    cursor: pointer;
  }
  button.primary {
    background: #059669;
    color: white;
  }
  button.primary:hover {
    background: #047857;
  }
  button.secondary {
    background: #e2e8f0;
    color: #334155;
  }
  button.small {
    padding: 0.3rem 0.7rem;
    font-size: 0.85rem;
  }
  .table-wrap {
    overflow-x: auto;
    background: white;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgb(0 0 0 / 0.06);
  }
  table {
    width: 100%;
    border-collapse: collapse;
  }
  th,
  td {
    padding: 0.75rem 1rem;
    text-align: left;
    border-bottom: 1px solid #f1f5f9;
  }
  th {
    background: #f8fafc;
    font-size: 0.8rem;
    color: #475569;
  }
  .badge {
    display: inline-block;
    padding: 0.15rem 0.5rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
  }
  .bg-green-100 {
    background: #dcfce7;
    color: #166534;
  }
  .bg-blue-100 {
    background: #dbeafe;
    color: #1e40af;
  }
  .bg-red-100 {
    background: #fee2e2;
    color: #991b1b;
  }
  .bg-gray-100 {
    background: #f1f5f9;
    color: #475569;
  }
  .hints {
    margin-top: 1.5rem;
    padding: 1rem;
    background: #f8fafc;
    border-radius: 8px;
    font-size: 0.9rem;
  }
  .hints h3 {
    margin: 0 0 0.5rem;
    font-size: 1rem;
  }
  .hints ul {
    margin: 0;
    padding-left: 1.2rem;
  }
  .error {
    color: #b91c1c;
    background: #fef2f2;
    padding: 1rem;
    border-radius: 6px;
  }
  .modal-backdrop {
    position: fixed;
    inset: 0;
    background: rgb(15 23 42 / 0.55);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 50;
    padding: 1rem;
  }
  .modal.large {
    background: white;
    border-radius: 12px;
    width: min(1100px, 98vw);
    max-height: 94vh;
    overflow: auto;
    padding: 1rem 1.25rem 1.25rem;
    box-shadow: 0 25px 50px -12px rgb(0 0 0 / 0.25);
  }
  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
  }
  .modal-header h2 {
    margin: 0;
    font-size: 1.15rem;
  }
  .modal-foot {
    margin: 0.75rem 0 0;
    font-size: 0.8rem;
    color: #64748b;
    text-align: center;
  }
</style>
