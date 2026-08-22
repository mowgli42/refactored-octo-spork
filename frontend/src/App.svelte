<script>
  import FlightDashboard from './lib/FlightDashboard.svelte';
  import AnalysisStation from './lib/AnalysisStation.svelte';

  let view = 'dashboard'; // dashboard | analysis
  let selectedEvent = null;
  let analysisData = [];

  function onAnalyze(e) {
    selectedEvent = e.detail.event;
    analysisData = e.detail.data || [];
    view = 'analysis';
  }

  function onBack() {
    view = 'dashboard';
    selectedEvent = null;
  }
</script>

{#if view === 'analysis' && selectedEvent}
  <AnalysisStation event={selectedEvent} data={analysisData} on:back={onBack} />
{:else}
  <FlightDashboard on:analyze={onAnalyze} />
{/if}
