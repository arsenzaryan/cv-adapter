from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(default="ok")


class AdaptRequest(BaseModel):
    resume_text: str = Field(..., description="Raw resume or CV text")
    job_description: str = Field(..., description="Target job description text")
    strategy: str | None = Field(
        default=None,
        description="Optional hint about how to adapt (e.g., 'concise', 'keyword-match')",
    )


class AdaptResponse(BaseModel):
    adapted_resume: str 