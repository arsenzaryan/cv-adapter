# CV Adapter (Monolith)

FastAPI backend + React (Vite) frontend, served together from one container. No database.

## Structure

- `backend/` — FastAPI app and API endpoints
  - `app/main.py` — serves API and built frontend
  - `app/api/routes.py` — `/api` routes (`/healthz`, `/adapt`)
  - `app/core/llm.py` — OpenAI integration for adaptation
  - `app/models/schemas.py` — request/response models
  - `requirements.txt` — backend dependencies
- `frontend/` — Vite React TypeScript SPA
  - Build outputs are copied into `backend/app/static/`
- `Dockerfile` — builds frontend then runs backend serving everything

## Configuration

Environment variables (can be exported locally or passed to docker):

- `OPENAI_API_KEY` — required to enable LLM adaptation
- `CV_ADAPTER_OPENAI_MODEL` — optional, default `gpt-4o-mini`
- `CV_ADAPTER_OPENAI_TEMPERATURE` — optional, default `0.2`
- `CV_ADAPTER_OPENAI_MAX_OUTPUT_TOKENS` — optional, default `800`

## Run locally (dev)

Backend (Python 3.11+):

```bash
python -m venv .venv && source .venv/bin/activate
export OPENAI_API_KEY=sk-...   # required for /api/adapt
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` for the frontend (which will call the backend at `http://localhost:8000`). For CORS-free testing, you can also build the frontend and let FastAPI serve it:

```bash
cd frontend && npm run build && cd -
uvicorn backend.app.main:app --reload --port 8000
```

Then open `http://localhost:8000`.

## Build and run with Docker (single container)

```bash
docker build -t cv-adapter .
docker run --rm -e OPENAI_API_KEY=$OPENAI_API_KEY -p 8000:8000 cv-adapter
```

Open `http://localhost:8000`.

## Deploy to Railway

This project is configured for easy deployment on Railway:

1. **Connect your repository** to Railway
2. **Set environment variables** in Railway dashboard:
   - `OPENAI_API_KEY` — your OpenAI API key (required)
   - Optionally set:
     - `CV_ADAPTER_OPENAI_MODEL` (default: `gpt-4o-mini`)
     - `CV_ADAPTER_OPENAI_TEMPERATURE` (default: `0.2`)
     - `CV_ADAPTER_OPENAI_MAX_OUTPUT_TOKENS` (default: `800`)
3. **Deploy** — Railway will automatically use the `Dockerfile` and `railway.toml` configuration

The application will be available at your Railway-provided URL. Railway automatically handles:
- Port configuration (using `$PORT` environment variable)
- Health checks via `/api/healthz`
- Container restart policies
- SSL certificates

### Manual Railway deployment

If you prefer to deploy manually:

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway link  # or railway init to create new project
railway up
```

## Next steps

- Improve prompt templates and add evaluation harness
- Add file upload + parsing (PDF/DOCX → text)
- Authentication and persistence (when needed) 