# Change: Parquet cache and D3 visualization

## Why

Flight test telemetry datasets are large and columnar. HDF5-only caching and static tables limited exploration. Parquet + a D3 plot endpoint unlock interactive multi-parameter review.

## What changes

- Processing caches as Parquet (legacy H5 read still supported)
- GET `/files/{id}/data` with downsampling for frontend
- `FlightDataPlot.svelte` with D3 zoom, legend, tooltips
- Sample data generator and README formalization

## Non-goals

- Multipart file upload (path registration only for now)
- Vercel demo mode implementation (documented, not wired)
- User authentication
