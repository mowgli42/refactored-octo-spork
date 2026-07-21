# Flight Test Data Management System

**Now with Parquet ingestion + interactive D3.js flight data plotting!**

This project is a framework for tracking flight test events and data files, with strong support for efficient aircraft telemetry analysis.

## Key Features (Updated)

- Track flight test events with status workflow (Import / Parse / Analysis)
- Register data files by local path or URL (now supports **.parquet**, .csv, .h5 natively)
- Backend processing: realistic mock telemetry or real Parquet/CSV flight test data → cached as high-performance Parquet
- **New**: `/files/{id}/data` API endpoint serves downsampled JSON ready for visualization
- **New**: Interactive D3.js time-series plots in Svelte frontend (altitude, airspeed, pitch, roll, vertical speed, AoA, G-force etc.)
  - Toggle parameters via legend
  - Hover tooltips with values
  - Mouse wheel zoom & pan
  - Clean aviation-themed styling

## Project Structure

- `backend/`: FastAPI + SQLAlchemy + pandas/pyarrow (Parquet first-class)
- `frontend/`: Svelte 5 + Vite + D3 v7

## Getting Started

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..
python3 -m uvicorn backend.main:app --reload
```

API at http://localhost:8000 , docs at /docs

### Frontend

```bash
cd frontend
npm install   # now includes d3
npm run dev
```

Dashboard at http://localhost:5173

## How to Use Parquet + D3 Plotting

1. Add a new Event (e.g. "Flight Test 47 - F-35 Demo")
2. Click "Add File" → paste **full local path** to your `.parquet` flight test file (or use the generated mock by leaving path as-is)
3. Processing runs in background → status becomes Complete / Ready
4. Click the green **"📈 Open D3 Flight Data Plot"** button (or "Plot Data" on a processed row)
5. Explore interactive charts of aircraft parameters over time

Tip: For real data, ensure the Parquet has a `timestamp` column (or datetime index) and numeric telemetry columns. The system auto-detects and down-samples for smooth D3 rendering.

## Development Plan

See [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md) — Phase 3 (Visualization) is now substantially complete with D3 + Parquet.

## Next Ideas
- Full file upload (multipart) instead of path-only
- Per-event file listing + multi-file comparison plots
- Export plot as SVG/PNG or generate PDF reports
- Integration with larger Dashlink-style datasets
