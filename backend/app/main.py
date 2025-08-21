from pathlib import Path
from typing import Optional

from fastapi import FastAPI, APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.api.routes import router as api_router
from app.api.auth_routes import router as auth_router
from app.core.config import settings


STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(title="CV Adapter API", version="0.1.0")

# Sessions (cookie-based, no DB)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret,
    session_cookie=settings.cookie_name,
    https_only=settings.cookie_secure,
    same_site="lax",
    domain=settings.cookie_domain,
)

# API routes under /api
app.include_router(api_router, prefix="/api")
app.include_router(auth_router, prefix="/api/auth")

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