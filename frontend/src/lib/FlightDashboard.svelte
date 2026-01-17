<script>
  import { onMount } from 'svelte';

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

  const API_URL = 'http://localhost:8000';

  onMount(async () => {
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
    selectedEventId = eventId;
    fileForm = { filename: '', source_url: '', filetype: 'flight_log' };
  }

  async function addFileToEvent() {
    if (!selectedEventId || !fileForm.source_url) return;

    try {
      // Auto-generate filename if empty
      if (!fileForm.filename) {
        fileForm.filename = fileForm.source_url.split('/').pop() || 'unknown_file';
      }

      const response = await fetch(`${API_URL}/events/${selectedEventId}/files/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(fileForm)
      });

      if (response.ok) {
        alert('File registered and processing started!');
        selectedEventId = null;
        await fetchEvents(); // Refresh status
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
      default: return 'bg-gray-100 text-gray-800';
    }
  }
</script>

<div class="container">
  <h1>Flight Test Events Dashboard</h1>

  <div class="add-event">
    <input 
      type="text" 
      bind:value={newEventName} 
      placeholder="New Event Name"
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
              <td>
                <button class="small" on:click={() => openFileForm(event.id)}>Add File</button>
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
          <label for="source-url">Source URL / Path:</label>
          <input id="source-url" type="text" bind:value={fileForm.source_url} placeholder="https://... or /path/to/file.csv" />
        </div>
        
        <div class="form-group">
          <label for="filename">Filename (Optional):</label>
          <input id="filename" type="text" bind:value={fileForm.filename} placeholder="flight_data.csv" />
        </div>

        <div class="form-group">
          <label for="filetype">File Type:</label>
          <select id="filetype" bind:value={fileForm.filetype}>
            <option value="flight_log">Flight Log</option>
            <option value="telemetry">Telemetry</option>
            <option value="video">Video</option>
          </select>
        </div>

        <div class="modal-actions">
          <button on:click={addFileToEvent}>Register & Process</button>
          <button class="secondary" on:click={() => selectedEventId = null}>Cancel</button>
        </div>
      </div>
    </div>
  {/if}
</div>

<style>
  .container {
    max-width: 1000px;
    margin: 0 auto;
    padding: 2rem;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen-Sans, Ubuntu, Cantarell, "Helvetica Neue", sans-serif;
  }

  h1 {
    color: #333;
    border-bottom: 2px solid #eee;
    padding-bottom: 1rem;
  }

  .add-event {
    margin: 2rem 0;
    display: flex;
    gap: 1rem;
  }

  input, select {
    padding: 0.5rem;
    border: 1px solid #ccc;
    border-radius: 4px;
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
    padding: 0.5rem 1rem;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1rem;
  }

  button:hover {
    background-color: #0052a3;
  }

  button.secondary {
    background-color: #666;
  }
  
  button.secondary:hover {
    background-color: #555;
  }

  button.small {
    font-size: 0.8rem;
    padding: 0.25rem 0.5rem;
    background-color: #f0f0f0;
    color: #333;
    border: 1px solid #ccc;
  }

  button.small:hover {
    background-color: #e0e0e0;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 1rem;
  }

  th, td {
    padding: 1rem;
    text-align: left;
    border-bottom: 1px solid #eee;
  }

  th {
    background-color: #f8f9fa;
    font-weight: 600;
  }

  .status-badge {
    padding: 0.25rem 0.5rem;
    border-radius: 999px;
    font-size: 0.875rem;
    font-weight: 500;
  }

  .bg-green-100 { background-color: #d1fae5; }
  .text-green-800 { color: #065f46; }
  
  .bg-blue-100 { background-color: #dbeafe; }
  .text-blue-800 { color: #1e40af; }
  
  .bg-red-100 { background-color: #fee2e2; }
  .text-red-800 { color: #991b1b; }
  
  .bg-gray-100 { background-color: #f3f4f6; }
  .text-gray-800 { color: #1f2937; }

  .error {
    color: red;
    background: #ffe6e6;
    padding: 1rem;
    border-radius: 4px;
  }

  /* Modal Styles */
  .modal-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.5);
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .modal {
    background: white;
    padding: 2rem;
    border-radius: 8px;
    width: 400px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  }

  .modal h2 {
    margin-top: 0;
  }

  .form-group {
    margin-bottom: 1rem;
  }

  .form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
  }

  .modal-actions {
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
    margin-top: 2rem;
  }
</style>
