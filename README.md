# Flight Test Data Management System

This project is a framework for tracking flight test events and data files.

## Project Structure

- `backend/`: FastAPI application with SQLite database.
- `frontend/`: Svelte application (Vite-based) for the dashboard.

## Getting Started

### Backend

1. Navigate to the workspace root.
2. Create and activate a virtual environment (if not already done):
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   cd ..
   ```
3. Run the server as a module from the workspace root:
   ```bash
   python3 -m uvicorn backend.main:app --reload
   ```
   The API will be available at `http://localhost:8000`.
   API Documentation (Swagger UI) at `http://localhost:8000/docs`.

### Frontend

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
   The dashboard will be available at `http://localhost:5173`.

## Development Plan

See [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md) for the roadmap.
