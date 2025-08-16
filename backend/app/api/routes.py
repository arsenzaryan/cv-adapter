from fastapi import APIRouter
from fastapi import UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse

from app.core.llm import adapt_resume
from app.core.pdf import extract_first_two_pages_text, parse_text_to_sections, render_cv_pdf_from_sections
from app.models.schemas import AdaptRequest, AdaptResponse, HealthResponse


router = APIRouter()


@router.get("/healthz", response_model=HealthResponse)
def healthcheck() -> HealthResponse:
    return HealthResponse(status="ok")


@router.post("/adapt", response_model=AdaptResponse)
def adapt(request: AdaptRequest) -> AdaptResponse:
    adapted = adapt_resume(
        resume_text=request.resume_text,
        job_description=request.job_description,
        strategy=request.strategy,
    )
    return AdaptResponse(adapted_resume=adapted)


@router.post("/adapt-upload", response_model=AdaptResponse)
async def adapt_upload(
    file: UploadFile = File(..., description="PDF resume file"),
    job_description: str = Form(..., description="Target job description text"),
    strategy: str | None = Form(default=None, description="Optional strategy hint"),
) -> AdaptResponse:
    if file.content_type not in ("application/pdf", "application/x-pdf", "application/acrobat", "applications/pdf", "text/pdf", "text/x-pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    file_bytes = await file.read()
    try:
        resume_text = extract_first_two_pages_text(file_bytes)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to read PDF: {exc}")

    if not resume_text.strip():
        raise HTTPException(status_code=400, detail="No extractable text found in the first two pages of the PDF")

    adapted = adapt_resume(
        resume_text=resume_text,
        job_description=job_description,
        strategy=strategy,
    )
    return AdaptResponse(adapted_resume=adapted)


@router.post("/pdf")
async def generate_pdf(
    text: str = Form(..., description="Adapted resume text to render to PDF"),
    filename: str | None = Form(default=None, description="Optional file name (without extension)"),
    title: str | None = Form(default=None, description="Optional document title"),
):
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text is required")
    sections = parse_text_to_sections(text)
    pdf_bytes = render_cv_pdf_from_sections(sections, title=title or "Curriculum Vitae")
    out_name = (filename or "adapted-cv").strip() or "adapted-cv"
    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={out_name}.pdf",
        },
    ) 