<script>
  import { onMount } from 'svelte';
  import FlightDataPlot from './FlightDataPlot.svelte';
  import { API_BASE } from './api.js';
  import demoSampleData from './demoSampleData.json';

  let events = [];
  let newEventName = '';
  let loading = true;
  let error = null;
  
  // File upload state
  let selectedEventId = null;
  let fileForm = {
    filename: '',
    source_url: '',
    filetype: 'flight_log'
  };

  // Plot modal state
  let showPlotModal = false;
  let plotFileId = null;
  let plotInitialData = null;

  const API_URL = API_BASE;
  const isDemoMode = import.meta.env.VITE_DEMO_MODE === 'true';

  const demoEvents = [
    {
      id: 1,
      name: 'Demo Test Flight - Tail 652',
      date: '2026-07-15T14:30:00Z',
      import_status: 'Complete',
      parse_status: 'Complete',
      analysis_status: 'Ready',
      files: [{ id: 1 }],
    },
    {
      id: 2,
      name: 'High Alpha Maneuver - Tail 652',
      date: '2026-07-16T09:15:00Z',
      import_status: 'Complete',
      parse_status: 'Complete',
      analysis_status: 'Ready',
      files: [{ id: 2 }],
    },
  ];

  onMount(async () => {
    if (isDemoMode) {
      events = demoEvents;
      loading = false;
      return;
    }
    await fetchEvents();
  });

  async function fetchEvents() {
    try {
      const response = await fetch(`${API_URL}/events/`);
      if (!response.ok) throw new Error('Failed to fetch events');
      events = await response.json();
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  }

  async function addEvent() {
    if (isDemoMode) {
      alert('Demo mode: sample events are pre-loaded. Run locally without VITE_DEMO_MODE for full CRUD.');
      return;
    }
    if (!newEventName) return;
    
    try {
      const response = await fetch(`${API_URL}/events/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: newEventName }),
      });
      
      if (response.ok) {
        newEventName = '';
        await fetchEvents();
      }
    } catch (e) {
      console.error(e);
      alert('Error adding event');
    }
  }

  function openFileForm(eventId) {
    if (isDemoMode) {
      alert('Demo mode: file registration is disabled. Use Plot Data to view embedded sample telemetry.');
      return;
    }
    selectedEventId = eventId;
    fileForm = { filename: '', source_url: '', filetype: 'flight_log' };
  }

  async function addFileToEvent() {
    if (isDemoMode) {
      alert('Demo mode: uploads are disabled.');
      return;
    }
    if (!selectedEventId || !fileForm.source_url) return;

    try {
      if (!fileForm.filename) {
        fileForm.filename = fileForm.source_url.split('/').pop() || 'unknown_file';
      }

      const response = await fetch(`${API_URL}/events/${selectedEventId}/files/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(fileForm)
      });

      if (response.ok) {
        alert('File registered and processing started! (Parquet supported)');
        selectedEventId = null;
        await fetchEvents();
      } else {
        alert('Failed to register file');
      }
    } catch (e) {
      console.error(e);
      alert('Error adding file');
    }
  }

  function getStatusColor(status) {
    if (!status) return 'bg-gray-100 text-gray-800';
    switch (status.toLowerCase()) {
      case 'complete': return 'bg-green-100 text-green-800';
      case 'processing': return 'bg-blue-100 text-blue-800';
      case 'error': return 'bg-red-100 text-red-800';
      case 'ready': return 'bg-emerald-100 text-emerald-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  }

  function openPlotDemo() {
    plotFileId = null;
    plotInitialData = demoSampleData;
    showPlotModal = true;
  }

  function closePlotModal() {
    showPlotModal = false;
    plotFileId = null;
    plotInitialData = null;
  }

  // Example: to use with real processed file, after adding+processing a file, call openPlotForFile(fileId)
  function openPlotForFile(fId) {
    if (isDemoMode) {
      plotFileId = null;
      plotInitialData = demoSampleData;
    } else {
      plotFileId = fId;
      plotInitialData = null;
    }
    showPlotModal = true;
  }
</script>

<div class="container">
  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
    <h1>Flight Test Events Dashboard{isDemoMode ? ' (Demo Mode)' : ''}</h1>
    <button on:click={openPlotDemo} style="background: #059669; font-size: 0.9rem; padding: 0.5rem 1rem;">
      📈 Open D3 Flight Data Plot
    </button>
  </div>

  <p style="color: #666; margin-bottom: 1.5rem; font-size: 0.95rem;">
    Track flight test events • Register Parquet/CSV telemetry files • Process into efficient cache • Visualize with interactive D3.js plots
  </p>

  {#if isDemoMode}
    <div class="demo-banner">
      <strong>Demo Mode Active</strong> — Fixed sample flight data loaded. Uploads and API writes are disabled.
      <a href="https://github.com/mowgli42/refactored-octo-spork#quick-start" target="_blank" rel="noopener">Run full stack locally</a>
    </div>
  {/if}

  <div class="add-event">
    <input 
      type="text" 
      bind:value={newEventName} 
      placeholder="New Event Name (e.g. Test Flight 42 - Tail 652)"
    />
    <button on:click={addEvent}>Add Event</button>
  </div>

  {#if loading}
    <p>Loading events...</p>
  {:else if error}
    <p class="error">{error}</p>
  {:else}
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Date</th>
            <th>Import</th>
            <th>Parsing</th>
            <th>Analysis</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {#each events as event}
            <tr>
              <td>{event.id}</td>
              <td>{event.name}</td>
              <td>{new Date(event.date).toLocaleDateString()}</td>
              <td>
                <span class={`status-badge ${getStatusColor(event.import_status)}`}>
                  {event.import_status}
                </span>
              </td>
              <td>
                <span class={`status-badge ${getStatusColor(event.parse_status)}`}>
                  {event.parse_status}
                </span>
              </td>
              <td>
                <span class={`status-badge ${getStatusColor(event.analysis_status)}`}>
                  {event.analysis_status}
                </span>
              </td>
              <td style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
                <button class="small" on:click={() => openFileForm(event.id)}>Add File</button>
                {#if (event.parse_status === 'Complete' || event.analysis_status === 'Ready') && event.files?.length}
                  <button class="small" style="background:#059669; color:white; border:none;" on:click={() => openPlotForFile(event.files[0].id)}>
                    Plot Data
                  </button>
                {/if}
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}

  {#if selectedEventId}
    <div class="modal-backdrop">
      <div class="modal">
        <h2>Add File to Event #{selectedEventId}</h2>
        
        <div class="form-group">
          <label for="source-url">Source URL / Local Path (supports .parquet, .csv, .h5):</label>
          <input id="source-url" type="text" bind:value={fileForm.source_url} placeholder="/path/to/flight_data.parquet or https://..." />
          <small style="color:#666">Tip: Place a real Parquet flight test file on the backend host and paste the full local path.</small>
        </div>
        
        <div class="form-group">
          <label for="filename">Filename (Optional):</label>
          <input id="filename" type="text" bind:value={fileForm.filename} placeholder="flight_data.parquet" />
        </div>

        <div class="form-group">
          <label for="filetype">File Type:</label>
          <select id="filetype" bind:value={fileForm.filetype}>
            <option value="flight_log">Flight Log / Telemetry</option>
            <option value="telemetry">Telemetry</option>
            <option value="video">Video (placeholder)</option>
          </select>
        </div>

        <div class="modal-actions">
          <button on:click={addFileToEvent}>Register & Process (Parquet ready)</button>
          <button class="secondary" on:click={() => selectedEventId = null}>Cancel</button>
        </div>
      </div>
    </div>
  {/if}

  {#if showPlotModal}
    <div class="modal-backdrop" on:click|self={closePlotModal}>
      <div class="modal large" on:click|stopPropagation>
        <div style="display:flex; justify-content: space-between; align-items:center; margin-bottom:1rem;">
          <h2 style="margin:0;">Interactive Flight Test Data Plot (D3.js){isDemoMode ? ' (Demo Data)' : ''}</h2>
          <button class="secondary" on:click={closePlotModal}>Close</button>
        </div>
        
        <FlightDataPlot 
          apiBase={API_URL} 
          fileId={plotFileId} 
          initialData={plotInitialData} 
        />
        
        <div style="margin-top: 1rem; font-size: 0.85rem; color: #666; text-align: center;">
          Zoom with mouse wheel • Hover for tooltip • Click legend to toggle parameters • Supports real Parquet flight data
        </div>
      </div>
    </div>
  {/if}
</div>

<style>
  .container {
    max-width: 1100px;
    margin: 0 auto;
    padding: 2rem;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen-Sans, Ubuntu, Cantarell, "Helvetica Neue", sans-serif;
  }

  h1 {
    color: #1f2937;
    border-bottom: 2px solid #e5e7eb;
    padding-bottom: 0.75rem;
  }

  .add-event {
    margin: 1.5rem 0;
    display: flex;
    gap: 1rem;
  }

  input, select {
    padding: 0.5rem;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    font-size: 1rem;
    width: 100%;
    box-sizing: border-box;
  }

  .add-event input {
    flex-grow: 1;
  }

  button {
    background-color: #0066cc;
    color: white;
    border: none;
    padding: 0.55rem 1.1rem;
    border-radius: 6px;
    cursor: pointer;
    font-size: 1rem;
    font-weight: 500;
  }

  button:hover {
    background-color: #0052a3;
  }

  button.secondary {
    background-color: #6b7280;
  }
  
  button.secondary:hover {
    background-color: #4b5563;
  }

  button.small {
    font-size: 0.8rem;
    padding: 0.3rem 0.7rem;
    background-color: #f3f4f6;
    color: #374151;
    border: 1px solid #d1d5db;
  }

  button.small:hover {
    background-color: #e5e7eb;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 0.5rem;
    background: white;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  }

  th, td {
    padding: 0.85rem 1rem;
    text-align: left;
    border-bottom: 1px solid #f3f4f6;
  }

  th {
    background-color: #f8fafc;
    font-weight: 600;
    color: #334155;
  }

  .status-badge {
    padding: 0.2rem 0.6rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: capitalize;
  }

  .bg-green-100 { background-color: #d1fae5; color: #065f46; }
  .bg-blue-100 { background-color: #dbeafe; color: #1e40af; }
  .bg-red-100 { background-color: #fee2e2; color: #991b1b; }
  .bg-gray-100 { background-color: #f3f4f6; color: #374151; }
  .bg-emerald-100 { background-color: #d1fae5; color: #065f46; }

  .error {
    color: #dc2626;
    background: #fef2f2;
    padding: 1rem;
    border-radius: 6px;
  }

  /* Modal Styles */
  .modal-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(15, 23, 42, 0.6);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 100;
  }

  .modal {
    background: white;
    padding: 2rem;
    border-radius: 12px;
    width: 420px;
    max-height: 85vh;
    overflow: auto;
    box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
  }

  .modal.large {
    width: 95%;
    max-width: 980px;
  }

  .modal h2 {
    margin-top: 0;
    color: #1e2937;
  }

  .form-group {
    margin-bottom: 1.1rem;
  }

  .form-group label {
    display: block;
    margin-bottom: 0.4rem;
    font-weight: 600;
    color: #334155;
  }

  .modal-actions {
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
    margin-top: 1.5rem;
  }

  .table-container {
    overflow-x: auto;
  }

  .demo-banner {
    background: #f0fdf4;
    border: 1px solid #86efac;
    padding: 1rem;
    border-radius: 6px;
    margin-bottom: 1rem;
    color: #14532d;
  }

  .demo-banner a {
    margin-left: 0.5rem;
    color: #047857;
  }
</style>
