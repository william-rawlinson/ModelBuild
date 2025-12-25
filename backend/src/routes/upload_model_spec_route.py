from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from io import BytesIO
import hashlib
import logging

from docx import Document  # python-docx

router = APIRouter()
logger = logging.getLogger(__name__)


class ModelSpecMeta(BaseModel):
    filename: str
    size_bytes: int
    sha256: str
    paragraphs: int


class UploadModelSpecResponse(BaseModel):
    text: str
    meta: ModelSpecMeta
    warnings: list[str]


def _sha256_bytes(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()


def extract_plain_text_from_docx(content: bytes) -> tuple[str, int]:
    """
    v1: simplest possible extraction.
    - Paragraphs only
    - No tables, no formatting, no cleaning
    """
    doc = Document(BytesIO(content))
    texts = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    return "\n".join(texts), len(texts)


@router.post("/spec", response_model=UploadModelSpecResponse)
async def upload_model_spec(file: UploadFile = File(...)):
    filename = file.filename or ""

    if not filename.lower().endswith(".docx"):
        raise HTTPException(status_code=400, detail="Only .docx files are supported.")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file.")

    max_bytes = 10 * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(status_code=400, detail="File too large (max 10MB).")

    sha256 = _sha256_bytes(content)
    warnings: list[str] = []

    try:
        text, paragraph_count = extract_plain_text_from_docx(content)
    except Exception as e:
        logger.exception("Failed to parse model spec DOCX")
        raise HTTPException(
            status_code=422,
            detail=f"Failed to parse DOCX: {type(e).__name__}: {e}",
        )

    if not text.strip():
        warnings.append(
            "No paragraph text found. Tables, images, and comments are not extracted in v1."
        )

    logger.info(
        "Model spec uploaded: filename=%s size_bytes=%d sha256=%s paragraphs=%d",
        filename,
        len(content),
        sha256,
        paragraph_count,
    )

    return UploadModelSpecResponse(
        text=text,
        meta=ModelSpecMeta(
            filename=filename,
            size_bytes=len(content),
            sha256=sha256,
            paragraphs=paragraph_count,
        ),
        warnings=warnings,
    )
