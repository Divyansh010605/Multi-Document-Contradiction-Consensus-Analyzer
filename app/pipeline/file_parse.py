"""Utilities for parsing uploaded document files into plain text."""

from __future__ import annotations

import io
import json
from pathlib import Path

from fastapi import HTTPException, UploadFile
from pydantic import BaseModel
from pypdf import PdfReader
from docx import Document as DocxDocument


class ParsedUpload(BaseModel):
    """Parsed upload result."""

    filename: str
    source: str
    text: str


async def read_upload_file_bytes(file: UploadFile, max_bytes: int) -> bytes:
    """Read upload body in chunks; reject when total size exceeds ``max_bytes``."""
    buf = bytearray()
    while len(buf) <= max_bytes:
        chunk = await file.read(65536)
        if not chunk:
            break
        buf.extend(chunk)
        if len(buf) > max_bytes:
            name = file.filename or "upload"
            raise HTTPException(
                status_code=413,
                detail=f"{name}: exceeds maximum size of {max_bytes} bytes.",
            )
    return bytes(buf)


def _normalize_source(filename: str) -> str:
    stem = Path(filename).stem.strip()
    return stem or "Uploaded Source"


def _parse_txt_or_md(raw_bytes: bytes) -> str:
    return raw_bytes.decode("utf-8", errors="ignore").strip()


def _parse_json(raw_bytes: bytes) -> str:
    payload = json.loads(raw_bytes.decode("utf-8", errors="ignore"))
    if isinstance(payload, dict):
        if "text" in payload and isinstance(payload["text"], str):
            return payload["text"].strip()
        if "content" in payload and isinstance(payload["content"], str):
            return payload["content"].strip()
        return json.dumps(payload, ensure_ascii=True)
    if isinstance(payload, list):
        lines = [str(item) for item in payload]
        return "\n".join(lines).strip()
    return str(payload).strip()


def _parse_pdf(raw_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(raw_bytes))
    pages = []
    for page in reader.pages:
        extracted = page.extract_text() or ""
        if extracted.strip():
            pages.append(extracted.strip())
    return "\n".join(pages).strip()


def _parse_docx(raw_bytes: bytes) -> str:
    doc = DocxDocument(io.BytesIO(raw_bytes))
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text and p.text.strip()]
    return "\n".join(paragraphs).strip()


async def parse_uploaded_file(file: UploadFile, *, max_bytes: int) -> ParsedUpload:
    """Parse a supported uploaded file and return normalized text."""
    filename = file.filename or "uploaded_document"
    extension = Path(filename).suffix.lower()
    raw_bytes = await read_upload_file_bytes(file, max_bytes)

    if not raw_bytes:
        raise HTTPException(status_code=400, detail=f"{filename}: file is empty.")

    try:
        if extension in {".txt", ".md"}:
            text = _parse_txt_or_md(raw_bytes)
        elif extension == ".json":
            text = _parse_json(raw_bytes)
        elif extension == ".pdf":
            text = _parse_pdf(raw_bytes)
        elif extension == ".docx":
            text = _parse_docx(raw_bytes)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"{filename}: unsupported type. Allowed: txt, md, json, pdf, docx.",
            )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"{filename}: parse failed ({exc}).") from exc

    if not text:
        raise HTTPException(status_code=400, detail=f"{filename}: no readable text found.")

    return ParsedUpload(filename=filename, source=_normalize_source(filename), text=text)
