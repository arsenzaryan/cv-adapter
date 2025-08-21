from __future__ import annotations

import os
from typing import Optional, Tuple

from openai import OpenAI
from starlette.requests import Request

from app.core.config import settings


def _select_credentials(request: Optional[Request]) -> Tuple[str, str]:
    # Always use the same API key; switch model if authenticated
    api_key = settings.openai_api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set. Provide env var or CV_ADAPTER_OPENAI_API_KEY.")
    is_authenticated = bool(getattr(request, "session", None) and request.session.get("user"))
    if is_authenticated:
        model = settings.premium_openai_model or "gpt-5-mini"
    else:
        model = settings.openai_model
    return api_key, model


def _get_openai_client(request: Optional[Request]) -> tuple[OpenAI, str]:
    api_key, model = _select_credentials(request)
    return OpenAI(api_key=api_key), model


def _extract_text_from_response(response) -> Optional[str]:
    # Try direct property
    text = getattr(response, "output_text", None)
    if isinstance(text, str) and text.strip():
        return text.strip()

    # Try Responses API typed objects
    output = getattr(response, "output", None)
    if output and isinstance(output, list):
        chunks: list[str] = []
        for item in output:
            content = getattr(item, "content", None)
            if content and isinstance(content, list):
                for part in content:
                    text_obj = getattr(part, "text", None)
                    if text_obj is None and isinstance(part, dict):
                        text_obj = part.get("text")
                    if text_obj is not None:
                        value = getattr(text_obj, "value", None)
                        if value is None and isinstance(text_obj, dict):
                            value = text_obj.get("value")
                        if isinstance(value, str) and value:
                            chunks.append(value)
        if chunks:
            joined = "".join(chunks).strip()
            if joined:
                return joined

    # Fallback for Chat Completions shape
    choices = getattr(response, "choices", None)
    if choices:
        first = choices[0] if len(choices) else None
        message = getattr(first, "message", None)
        content = getattr(message, "content", None)
        if isinstance(content, str) and content.strip():
            return content.strip()

    return None


def adapt_resume(resume_text: str, job_description: str, strategy: str | None = None, request: Optional[Request] = None) -> str:
    client, model = _get_openai_client(request)

    system_prompt = (
        "You are an expert resume editor. You adapt a candidate's resume to a given job "
        "description while preserving truthful experience. Optimize for clarity, impact, and ATS keyword alignment. "
        "Return clean plain text that can be pasted into a resume. You can use '*'s as basic markdown formatting for important information, but keep it minimal. "
        "Avoid hallucinating facts. Do not fabricate statements."
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

    is_gpt5 = model.lower().startswith("gpt-5")

    if is_gpt5:
        # Prefer Responses API for gpt-5 models
        input_text = f"System: {system_prompt}\n\nUser: {user_prompt}"
        response = client.responses.create(
            model=model,
            input=input_text,
            max_output_tokens=settings.openai_max_output_tokens,
        )
        content = _extract_text_from_response(response)
        if not content:
            # Fallback to Chat Completions without unsupported params
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            content = _extract_text_from_response(response)
    else:
        # Use Chat Completions for other models
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=settings.openai_max_output_tokens,
            temperature=settings.openai_temperature,
        )
        content = _extract_text_from_response(response)

    if not content:
        raise RuntimeError("OpenAI returned no content")
    return content.strip() 