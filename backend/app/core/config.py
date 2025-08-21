from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CV Adapter"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    openai_temperature: float = 0.2
    openai_max_output_tokens: int = 800

    # Premium model used when the user is authenticated (same API key)
    premium_openai_model: str = "gpt-5-mini"

    # Google OAuth (OIDC)
    google_client_id: str | None = None
    google_client_secret: str | None = None

    # Cookie/session
    session_secret: str = "change-me"
    cookie_name: str = "cv_adapter_session"
    cookie_secure: bool = False  # set True in production
    cookie_domain: str | None = None

    model_config = SettingsConfigDict(
        env_prefix="CV_ADAPTER_",
        case_sensitive=False,
    )


settings = Settings()  # Load from environment if provided 