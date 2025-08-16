from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CV Adapter"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    openai_temperature: float = 0.2
    openai_max_output_tokens: int = 800

    model_config = SettingsConfigDict(
        env_prefix="CV_ADAPTER_",
        case_sensitive=False,
    )


settings = Settings()  # Load from environment if provided 