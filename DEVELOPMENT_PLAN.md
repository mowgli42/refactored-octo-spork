# Flight Test Data Management System - Development Plan

## Phase 1: Foundation (Current Status)
- **Goal**: Establish the core architecture and tracking capabilities.
- **Tech Stack**: Svelte (Frontend), FastAPI (Backend), SQLite (Database).
- **Features**:
  - [x] Basic Project Structure
  - [x] Database Schema for Flight Events and Data Files
  - [x] Backend API to create/read events and update status
  - [x] Frontend Dashboard to view and add events

## Phase 2: File Management & Parsing
- **Goal**: Implement actual file handling and parsing logic.
- **Features**:
  - File Upload: Allow uploading files to specific events.
  - File System Scanner: Automatically detect files in a watched directory.
  - Parser Engine: Abstract base class for file parsers (CSV, Binary, etc.).
  - Async Tasks: Use background tasks (e.g., Celery or FastAPI BackgroundTasks) for long-running parsing.

## Phase 3: Data Analysis & Visualization
- **Goal**: Visualize the parsed data.
- **Features**:
  - Time-series plotting (using libraries like Plotly or D3.js in Svelte).
  - Parameter extraction and limit checking.
  - Report generation.

## Phase 4: Advanced Features
- **Goal**: Collaboration and Security.
- **Features**:
  - User Authentication & Authorization.
  - Search and Filtering (by date, pilot, aircraft).
  - Data Export APIs.

## Usage Instructions

### Prerequisites
- Python 3.12+
- Node.js 18+

### Setup

1. **Backend**:
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```
   API runs at `http://localhost:8000`. API Docs at `http://localhost:8000/docs`.

2. **Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Dashboard runs at `http://localhost:5173`.
