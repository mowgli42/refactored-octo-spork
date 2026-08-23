<script>
  // Ported from o-my-debrief MissionMap.svelte: CARTO dark tiles, dashed planned
  // route, flown-track polyline that follows playback, heading-rotated platform
  // marker, and severity-colored significant-event markers.
  import { onMount, onDestroy, createEventDispatcher } from 'svelte';
  import L from 'leaflet';
  import 'leaflet/dist/leaflet.css';

  /** @type {any[]} parsed telemetry rows (latitude, longitude, heading_deg, _date) */
  export let track = [];
  export let currentIdx = 0;
  /** @type {any[]} analyst-captured significant/anomalous events */
  export let sigEvents = [];

  const dispatch = createEventDispatcher();
  const SEV_COLORS = { note: '#4da3ff', anomaly: '#f0c14a', critical: '#ff5c6c' };

  let mapEl;
  let map = null;
  let routeLayer = null;
  let flownLayer = null;
  let eventLayer = null;
  let platformMarker = null;
  let fitted = false;
  let ready = false;

  onMount(() => {
    map = L.map(mapEl, { zoomControl: true, attributionControl: true }).setView(
      [34.05, -118.25],
      11
    );
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; OSM &copy; CARTO',
      maxZoom: 18
    }).addTo(map);
    routeLayer = L.layerGroup().addTo(map);
    flownLayer = L.layerGroup().addTo(map);
    eventLayer = L.layerGroup().addTo(map);
    ready = true;
  });

  onDestroy(() => {
    map?.remove();
    map = null;
  });

  $: latlngs = track.map((r) => [r.latitude, r.longitude]);
  $: if (ready && latlngs.length) drawRoute(latlngs);
  $: if (ready && latlngs.length) drawFlown(latlngs, currentIdx);
  $: if (ready) drawSigEvents(sigEvents, latlngs);
  $: if (ready && track.length) drawPlatform(track[Math.min(currentIdx, track.length - 1)]);

  function drawRoute(pts) {
    routeLayer.clearLayers();
    L.polyline(pts, { color: '#3dd6c6', weight: 2, opacity: 0.45, dashArray: '6 4' }).addTo(
      routeLayer
    );
    L.circleMarker(pts[0], {
      radius: 5,
      color: '#5ddea0',
      fillColor: '#0b1220',
      fillOpacity: 1,
      weight: 2
    })
      .bindTooltip('Start', { direction: 'top' })
      .addTo(routeLayer);
    L.circleMarker(pts[pts.length - 1], {
      radius: 5,
      color: '#8fa3c1',
      fillColor: '#0b1220',
      fillOpacity: 1,
      weight: 2
    })
      .bindTooltip('End', { direction: 'top' })
      .addTo(routeLayer);
    if (!fitted) {
      map.fitBounds(L.latLngBounds(pts).pad(0.2));
      fitted = true;
    }
  }

  function drawFlown(pts, idx) {
    flownLayer.clearLayers();
    const flown = pts.slice(0, Math.max(2, idx + 1));
    if (flown.length >= 2) {
      L.polyline(flown, { color: '#f0c14a', weight: 3, opacity: 0.9 }).addTo(flownLayer);
    }
  }

  function drawSigEvents(evts, pts) {
    eventLayer.clearLayers();
    if (!pts.length) return;
    for (const ev of evts) {
      const i = Math.min(pts.length - 1, Math.round(ev.t0 * (pts.length - 1)));
      const color = SEV_COLORS[ev.severity] || '#8fa3c1';
      const mk = L.marker(pts[i], {
        icon: L.divIcon({
          className: 'sig-marker',
          html: `<div style="font-size:18px;line-height:1;color:${color};text-shadow:0 0 6px rgba(0,0,0,.9)">▼</div>`,
          iconSize: [18, 18],
          iconAnchor: [9, 9]
        })
      }).bindTooltip(`${ev.severity.toUpperCase()} — ${ev.summary}`, { direction: 'top' });
      mk.on('click', () => dispatch('selectEvent', ev));
      mk.addTo(eventLayer);
    }
  }

  function drawPlatform(row) {
    if (platformMarker) {
      map.removeLayer(platformMarker);
      platformMarker = null;
    }
    if (!row) return;
    const rot = row.heading_deg != null ? `transform:rotate(${row.heading_deg}deg)` : '';
    platformMarker = L.marker([row.latitude, row.longitude], {
      icon: L.divIcon({
        className: 'platform-marker',
        html: `<div style="width:16px;height:16px;${rot}"><div style="width:0;height:0;border-left:8px solid transparent;border-right:8px solid transparent;border-bottom:16px solid #3dd6c6;filter:drop-shadow(0 0 6px rgba(61,214,198,.9))"></div></div>`,
        iconSize: [16, 16],
        iconAnchor: [8, 8]
      })
    }).addTo(map);
  }
</script>

<div class="map-el" bind:this={mapEl}></div>

<style>
  .map-el {
    flex: 1;
    min-height: 300px;
    border: 1px solid var(--line);
    border-radius: 4px;
    overflow: hidden;
  }
  :global(.leaflet-container) {
    background: #0b1220;
    font-family: inherit;
  }
</style>
