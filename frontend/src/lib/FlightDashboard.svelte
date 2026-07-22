<script>
  import { onMount } from 'svelte';
  import FlightDataPlot from './FlightDataPlot.svelte';
  import { API_BASE } from './api.js';

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

  // Sample demo data (small subset)
  const demoSampleData = [
    {"timestamp":"2026-07-15T14:30:00","altitude_ft":15002.48,"airspeed_kt":279.74,"vertical_speed_fpm":175.86,"pitch_deg":-0.4,"roll_deg":0.88,"heading_deg":44.86,"aoa_deg":3.74,"g_force":1.05},
    {"timestamp":"2026-07-15T14:30:01","altitude_ft":15019.02,"airspeed_kt":284.88,"vertical_speed_fpm":378.77,"pitch_deg":-0.38,"roll_deg":-1.45,"heading_deg":45.21,"aoa_deg":3.58,"g_force":1.07}
    // ... more rows can be added or loaded from sample-data JSON
  ];

  onMount(async () => {
    if (isDemoMode) {
      events = [
        { id: 1, name: 'Demo Test Flight - Tail 652', date: '2026-07-15T14:30:00Z', import_status: 'Complete', parse_status: 'Complete', analysis_status: 'Ready', files: [{ id: 1 }] }
      ];
      loading = false;
    } else {
      await fetchEvents();
    }
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
      alert('Demo mode: Sample events are pre-loaded.');
      return;
    }
    if (!newEventName) return;
    // original fetch code...
    try {
      const response = await fetch(`${API_URL}/events/`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
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
      alert('Demo mode: File registration simulated. Open the plot for sample data.');
      return;
    }
    selectedEventId = eventId;
    fileForm = { filename: '', source_url: '', filetype: 'flight_log' };
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

  function openPlotForFile(fId) {
    if (isDemoMode) {
      plotInitialData = demoSampleData;
    }
    plotFileId = fId;
    showPlotModal = true;
  }
</script>

<div class="container">
  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
    <h1>Flight Test Events Dashboard {isDemoMode ? '(Demo Mode)' : ''}</h1>
    <button on:click={openPlotDemo} style="background: #059669; font-size: 0.9rem; padding: 0.5rem 1rem;">
      📈 Open D3 Flight Data Plot
    </button>
  </div>

  <p style="color: #666; margin-bottom: 1.5rem; font-size: 0.95rem;">
    Track flight test events • Register Parquet/CSV telemetry files • Process into efficient cache • Visualize with interactive D3.js plots
  </p>

  {#if isDemoMode}
    <div style="background:#f0fdf4; border:1px solid #86efac; padding:1rem; border-radius:6px; margin-bottom:1rem;">
      <strong>Demo Mode Active</strong> — Fixed sample flight data loaded. Uploads are disabled.
    </div>
  {/if}

  <!-- Rest of the template unchanged -->
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
    <!-- table unchanged -->
    <div class="table-container">
      <table>
        <!-- ... -->
      </table>
    </div>
  {/if}

  {#if selectedEventId}
    <!-- modal unchanged, but demo guard in addFileToEvent -->
  {/if}

  {#if showPlotModal}
    <div class="modal-backdrop" on:click|self={closePlotModal}>
      <div class="modal large" on:click|stopPropagation>
        <div style="display:flex; justify-content: space-between; align-items:center; margin-bottom:1rem;">
          <h2 style="margin:0;">Interactive Flight Test Data Plot (D3.js) {isDemoMode ? '(Demo Data)' : ''}</h2>
          <button class="secondary" on:click={closePlotModal}>Close</button>
        </div>
        
        <FlightDataPlot 
          apiBase={API_URL} 
          fileId={plotFileId} 
          initialData={plotInitialData} 
        />
        
        <div style="margin-top: 1rem; font-size: 0.85rem; color: #666; text-align: center;">
          Zoom with mouse wheel • Hover for tooltip • Click legend to toggle parameters
        </div>
      </div>
    </div>
  {/if}
</div>

<style>
  /* unchanged */
</style>
