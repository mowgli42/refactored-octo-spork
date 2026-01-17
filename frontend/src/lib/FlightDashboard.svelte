<script>
  import { onMount } from 'svelte';

  let events = [];
  let newEventName = '';
  let loading = true;
  let error = null;

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

  function getStatusColor(status) {
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
                <button class="small">View Details</button>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
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

  input {
    padding: 0.5rem;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 1rem;
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
</style>
