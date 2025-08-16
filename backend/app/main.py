from pathlib import Path
from typing import Optional

from fastapi import FastAPI, APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import router as api_router


STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(title="CV Adapter API", version="0.1.0")

# API routes under /api
app.include_router(api_router, prefix="/api")

# Serve static frontend assets under /static
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")


# Health check endpoints for Railway
@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "cv-adapter"}

def _read_index_html() -> Optional[str]:
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return index_path.read_text(encoding="utf-8")
    return None


@app.get("/", response_class=HTMLResponse)
async def serve_root() -> HTMLResponse:
    index_html = _read_index_html()
    if index_html is None:
        return HTMLResponse(
            content=(
                "<html><body><h1>CV Adapter</h1>"
                "<p>Frontend is not built yet. Run \"npm run build\" in frontend/ or use Docker build.</p>"
                "</body></html>"
            ),
            status_code=200,
        )
    return HTMLResponse(content=index_html)


@app.get("/{full_path:path}", response_class=HTMLResponse)
async def serve_spa(full_path: str, request: Request) -> HTMLResponse:
    if full_path.startswith("api"):
        from fastapi import HTTPException
        raise HTTPException(status_code=404)

    index_html = _read_index_html()
    if index_html is None:
        return HTMLResponse(
            content=(
                "<html><body><h1>CV Adapter</h1>"
                "<p>Frontend is not built yet. Run \"npm run build\" in frontend/ or use Docker build.</p>"
                "</body></html>"
            ),
            status_code=200,
        )
    return HTMLResponse(content=index_html) 