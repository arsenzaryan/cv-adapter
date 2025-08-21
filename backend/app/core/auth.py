from __future__ import annotations

from authlib.integrations.starlette_client import OAuth

from app.core.config import settings


oauth = OAuth()

# Register Google as an OpenID Connect provider
# Requires CV_ADAPTER_GOOGLE_CLIENT_ID and CV_ADAPTER_GOOGLE_CLIENT_SECRET to be set
oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_id=settings.google_client_id or "",
    client_secret=settings.google_client_secret or "",
    client_kwargs={
        "scope": "openid email profile",
    },
) 