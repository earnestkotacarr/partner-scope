# Quick Start Guide

## Running Partner Scope Web Application

### Prerequisites

1. **Python 3.8+** and **Node.js 18+** installed
2. API keys configured (optional for testing with mock data)

### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Build the React Frontend

```bash
cd frontend
npm install
npm run build
cd ..
```

This will create a `frontend/dist` directory with the production build.

### Step 3: Start the Server

```bash
python server.py
```

The server will start at **http://localhost:8000**

### Step 4: Access the Application

Open your browser and navigate to:
- **Application**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Development Mode

### Running Frontend Dev Server (Hot Reload)

In one terminal:
```bash
cd frontend
npm run dev
```

This starts the React dev server at http://localhost:3000 with hot reload.

### Running Backend Server

In another terminal:
```bash
python server.py
```

The frontend dev server will proxy API requests to the backend at http://localhost:8000.

## Testing the Application

The application currently uses **mock data** for demonstration purposes. You can:

1. Fill out the startup information form
2. Click "Find Partners"
3. See mock partner matches appear on the right side

The mock data simulates the output of the partner matching pipeline.

## Next Steps - Implementing Real Functionality

To make the application work with real data:

1. **Configure API Keys**: Copy `.env.template` to `.env` and add your API keys
2. **Implement Providers**: Complete the TODO items in `src/providers/`
3. **Implement Core Logic**: Complete the TODO items in `src/core/`
4. **Update Server**: Replace mock data in `server.py` with actual pipeline execution

See `PROJECT_OVERVIEW.md` for detailed implementation guide.

## Project Structure

```
partner-scope/
├── frontend/              # React application
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── App.jsx       # Main app component
│   │   └── index.css     # Tailwind styles
│   ├── dist/             # Production build (created by npm run build)
│   └── package.json      # Frontend dependencies
│
├── src/                   # Python backend
│   ├── providers/        # Data source integrations
│   ├── core/            # Core matching logic
│   └── pipeline.py      # Main pipeline
│
├── server.py            # FastAPI web server
└── requirements.txt     # Python dependencies
```

## Common Issues

### "Frontend not built" message

Run `cd frontend && npm run build` to build the React application.

### Port already in use

Change the port in `server.py` (default is 8000) or kill the process using that port.

### API requests failing

Make sure the backend server is running at http://localhost:8000.

### Tailwind styles not working

Rebuild the frontend: `cd frontend && npm run build`
