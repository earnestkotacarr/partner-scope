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

## Debug Mode (Testing with Fake Data)

Debug mode allows you to run the complete evaluation pipeline without making any API calls, using auto-generated fake data to test each stage. Both frontend and backend support debug mode.

### Frontend Debug Mode

Frontend debug mode allows you to navigate directly to any page with pre-populated fake data, making UI development and testing much faster.

**Method 1: Browser Console**
```javascript
// Enable debug mode (page will reload)
window.debug.enable()

// Navigate directly to any page
window.debug.goTo('/evaluate')   // Go to evaluation page
window.debug.goTo('/results')    // Go to results page
window.debug.goTo('/review')     // Go to template review

// Check current status
window.debug.status()

// Get generated fake data
window.debug.getData()

// Show all available commands
window.debug.help()
```

**Method 2: Debug Panel UI**
- After enabling debug mode, an orange "DEBUG" button appears in the bottom-left corner
- Click to expand the debug panel
- Navigate to any page with one click
- Adjust the number of fake candidates (5/10/15/20)

**Method 3: Environment Variable (Build Time)**
```bash
# Enable debug mode during development
VITE_DEBUG_MODE=true npm run dev
```

### Backend Debug Mode

**Option 1: Environment Variable**
```bash
# Enable debug mode
DEBUG_MODE=1 python server.py

# Or set more options
DEBUG_MODE=1 DEBUG_VERBOSE=1 python server.py
```

**Option 2: API Call**
```bash
# Enable debug mode
curl -X POST http://localhost:8000/api/debug/enable \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'

# Check debug status
curl http://localhost:8000/api/debug/status
```

### Debug API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/debug/status` | GET | Get current debug mode status |
| `/api/debug/enable` | POST | Enable/disable debug mode |
| `/api/debug/evaluation` | POST | Run complete fake evaluation pipeline |
| `/api/debug/candidates` | GET | Generate fake candidate company data |
| `/api/debug/strategy` | GET | Generate fake evaluation strategy |
| `/api/debug/result` | GET | Generate complete fake evaluation result |

### Example: Run Debug Evaluation

```bash
# Run complete fake evaluation
curl -X POST http://localhost:8000/api/debug/evaluation \
  -H "Content-Type: application/json" \
  -d '{"num_candidates": 10, "startup_name": "TestStartup", "industry": "Software"}'

# Get 10 fake candidates
curl "http://localhost:8000/api/debug/candidates?count=10"

# Get fake evaluation strategy
curl "http://localhost:8000/api/debug/strategy?num_candidates=10"
```

### Using Debug Mode in Python Code

```python
from src.debug import DebugConfig, FakeDataGenerator

# Enable debug mode
DebugConfig.enable()

# Generate fake data
generator = FakeDataGenerator()
candidates = generator.generate_candidates(count=10)
strategy = generator.generate_strategy(num_candidates=10)
result = generator.generate_evaluation_result(candidates, strategy)

# Run debug evaluation
from src.evaluation.orchestrator import EvaluationOrchestrator

orchestrator = EvaluationOrchestrator(debug_mode=True)
result = await orchestrator.run_debug_evaluation(num_candidates=10)
```

### Debug Mode Configuration Options

| Option | Environment Variable | Default | Description |
|--------|---------------------|---------|-------------|
| `skip_planner_llm` | `DEBUG_SKIP_PLANNER` | True | Skip Planner Agent LLM calls |
| `skip_specialized_llm` | `DEBUG_SKIP_SPECIALIZED` | True | Skip Specialized Agent LLM calls |
| `skip_supervisor_llm` | `DEBUG_SKIP_SUPERVISOR` | True | Skip Supervisor Agent LLM calls |
| `skip_web_search` | `DEBUG_SKIP_WEB_SEARCH` | True | Skip Web Search API calls |
| `simulate_delay` | - | False | Simulate API delays |
| `verbose` | `DEBUG_VERBOSE` | True | Verbose logging output |

---

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
│   │   │   └── DebugPanel.jsx  # Debug mode floating panel
│   │   ├── context/      # React context providers
│   │   ├── debug/        # Frontend debug utilities
│   │   │   ├── config.js   # Debug configuration
│   │   │   ├── fakeData.js # Fake data generator
│   │   │   ├── init.js     # Console utilities (window.debug)
│   │   │   └── index.js    # Module exports
│   │   ├── hooks/        # Custom React hooks
│   │   │   └── useDebugMode.js  # Debug mode hook
│   │   ├── pages/        # Page components
│   │   ├── App.jsx       # Main app component
│   │   └── index.css     # Tailwind styles
│   ├── dist/             # Production build (created by npm run build)
│   └── package.json      # Frontend dependencies
│
├── src/                   # Python backend
│   ├── debug/            # Backend debug utilities
│   │   ├── config.py     # DebugConfig class
│   │   └── fake_data.py  # FakeDataGenerator class
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
