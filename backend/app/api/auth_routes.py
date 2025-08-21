from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware

from app.core.auth import oauth
from app.core.config import settings


router = APIRouter()


@router.get("/me")
async def me(request: Request) -> Dict[str, Any]:
    user = request.session.get("user")
    if not user:
        return {"authenticated": False}
    return {
        "authenticated": True,
        "email": user.get("email"),
        "name": user.get("name"),
        "picture": user.get("picture"),
    }


@router.get("/login/google")
async def login_google(request: Request):
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")
    redirect_uri = request.url_for("auth_google_callback")
    return await oauth.google.authorize_redirect(request, str(redirect_uri))


@router.get("/auth/google/callback")
async def auth_google_callback(request: Request):
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")
    token = await oauth.google.authorize_access_token(request)
    userinfo = token.get("userinfo")
    if not userinfo:
        # Fallback: fetch from userinfo endpoint
        resp = await oauth.google.get("userinfo", token=token)
        userinfo = resp.json()
    if not userinfo:
        raise HTTPException(status_code=401, detail="Failed to retrieve user info")

    # Store minimal user info in the session (no DB)
    request.session["user"] = {
        "sub": userinfo.get("sub"),
        "email": userinfo.get("email"),
        "name": userinfo.get("name"),
        "picture": userinfo.get("picture"),
    }

    # Redirect back to root
    response = RedirectResponse(url="/")
    return response


@router.post("/logout")
async def logout(request: Request):
    request.session.pop("user", None)
    return JSONResponse({"ok": True}) 