<script>
  import { onMount, createEventDispatcher } from 'svelte';
  import { generateDemoFlightSample, demoEvent } from './demoData.js';

  const dispatch = createEventDispatcher();

  let events = [];
  let loading = true;
  let error = null;
  let analysisData = [];

  const isDemoMode = import.meta.env.VITE_DEMO_MODE === 'true' || true;

  onMount(() => {
    if (isDemoMode) {
      events = [demoEvent];
      analysisData = generateDemoFlightSample(240);
      loading = false;
    } else {
      loading = false;
      error = 'Backend not configured. Use local full stack or enable VITE_DEMO_MODE.';
    }
  });

  function openAnalysis(event) {
    if (!analysisData.length) analysisData = generateDemoFlightSample(240);
    dispatch('analyze', { event, data: analysisData });
  }

  function getStatusColor(status) {
    if (!status) return 'muted';
    switch (String(status).toLowerCase()) {
      case 'complete':
      case 'ready':
        return 'ok';
      case 'processing':
        return 'info';
      case 'error':
        return 'bad';
      default:
        return 'muted';
    }
  }
</script>

<div class="dash">
  <header class="dash-header">
    <div>
      <div class="kicker">Open Arsenal · Flight Test</div>
      <h1>Events {isDemoMode ? '— Demo' : ''}</h1>
      <p class="sub">Select an event to open the immersive analysis station</p>
    </div>
  </header>

  {#if isDemoMode}
    <div class="banner">
      <strong>Demo mode</strong> — Fixed sample flight (Tail 652). Import disabled. Click Analyze for full-screen debrief.
    </div>
  {/if}

  {#if loading}
    <p class="muted">Loading…</p>
  {:else if error}
    <p class="error">{error}</p>
  {:else}
    <div class="table-wrap panel">
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
              <td class="mono">{event.id}</td>
              <td>{event.name}</td>
              <td class="mono">{new Date(event.date).toLocaleString()}</td>
              <td><span class="badge {getStatusColor(event.import_status)}">{event.import_status}</span></td>
              <td><span class="badge {getStatusColor(event.parse_status)}">{event.parse_status}</span></td>
              <td><span class="badge {getStatusColor(event.analysis_status)}">{event.analysis_status}</span></td>
              <td>
                <button class="analyze" on:click={() => openAnalysis(event)}>Analyze</button>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}
</div>

<style>
  .dash {
    max-width: 1000px;
    margin: 0 auto;
    padding: 1.5rem 1.25rem;
    height: 100%;
    overflow: auto;
  }
  .kicker {
    font-size: 10px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--muted);
  }
  h1 {
    margin: 0.2rem 0;
    font-size: 1.45rem;
  }
  .sub {
    margin: 0;
    color: var(--muted);
    font-size: 0.9rem;
  }
  .banner {
    margin: 1rem 0;
    padding: 0.75rem 1rem;
    border: 1px solid color-mix(in srgb, var(--verify) 40%, var(--line));
    background: color-mix(in srgb, var(--verify) 10%, var(--bg-panel));
    border-radius: 4px;
    font-size: 0.88rem;
  }
  .table-wrap {
    border-radius: 4px;
    overflow: auto;
  }
  table {
    width: 100%;
    border-collapse: collapse;
  }
  th,
  td {
    padding: 0.7rem 0.9rem;
    text-align: left;
    border-bottom: 1px solid var(--line);
    font-size: 0.9rem;
  }
  th {
    color: var(--muted);
    font-size: 0.75rem;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    background: var(--bg-deep);
  }
  .badge {
    display: inline-block;
    padding: 0.12rem 0.45rem;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 600;
  }
  .badge.ok {
    background: rgba(93, 222, 160, 0.15);
    color: var(--verify);
  }
  .badge.info {
    background: rgba(77, 163, 255, 0.15);
    color: var(--collect);
  }
  .badge.bad {
    background: rgba(255, 92, 108, 0.15);
    color: var(--danger);
  }
  .badge.muted {
    background: var(--bg-elevated);
    color: var(--muted);
  }
  button.analyze {
    background: color-mix(in srgb, var(--accent) 18%, transparent);
    color: var(--accent);
    border: 1px solid var(--accent);
    border-radius: 3px;
    padding: 0.35rem 0.75rem;
    font-size: 0.85rem;
    font-weight: 600;
    cursor: pointer;
  }
  button.analyze:hover {
    background: color-mix(in srgb, var(--accent) 28%, transparent);
  }
  .error {
    color: var(--danger);
  }
  .muted {
    color: var(--muted);
  }
  .mono {
    font-family: var(--font-mono);
  }
</style>
