from __future__ import annotations

import os
from typing import Optional

from openai import OpenAI

from app.core.config import settings


def _get_openai_client() -> OpenAI:
    api_key = settings.openai_api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set. Provide env var or CV_ADAPTER_OPENAI_API_KEY.")
    return OpenAI(api_key=api_key)


def adapt_resume(resume_text: str, job_description: str, strategy: str | None = None) -> str:
    client = _get_openai_client()

    system_prompt = (
        "You are an expert resume editor. You adapt a candidate's resume to a given job "
        "description while preserving truthful experience. Optimize for clarity, impact, and ATS keyword alignment. "
        "Return clean plain text that can be pasted into a resume. Avoid hallucinating facts. Do not fabricate statements."
    )

    user_prompt = (
        f"Strategy: {strategy or 'default'}\n\n"
        f"Job Description:\n{job_description}\n\n"
        f"Candidate Resume:\n{resume_text}\n\n"
        "Tasks:\n"
        "1) Highlight relevant experience and skills that match the job description.\n"
        "2) Adjust wording to include role-appropriate keywords without fabricating.\n"
        "3) Tighten bullets for measurable impact (action + scope + result).\n"
        "4) Keep the output as a resume sectioned text (Summary, Experience, Skills, Education)."
    )

    response = client.chat.completions.create(
        model=settings.openai_model,
        temperature=settings.openai_temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=settings.openai_max_output_tokens,
    )

    content = response.choices[0].message.content if response.choices else None
    if not content:
        raise RuntimeError("OpenAI returned no content")
    return content.strip() 