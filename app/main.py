"""FastAPI entrypoint for contradiction and consensus analyzer."""

from __future__ import annotations

import os
from pathlib import Path
from typing import List

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.pipeline.ingest import InputDocument
from app.pipeline.file_parse import parse_uploaded_file
from app.pipeline.orchestrator import analyze_documents
from app.schemas import AnalyzeRequest, AnalyzeResponse

APP_TITLE = os.getenv("APP_TITLE", "Multi-Document Contradiction and Consensus Analyzer")
UPLOAD_MAX_BYTES = int(os.getenv("UPLOAD_MAX_BYTES", str(10 * 1024 * 1024)))
UPLOAD_MAX_FILES = int(os.getenv("UPLOAD_MAX_FILES", "25"))

app = FastAPI(title=APP_TITLE, version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

_last_result: dict | None = None


@app.get("/")
def index() -> FileResponse:
    """Serve minimal web UI."""
    return FileResponse(static_dir / "index.html")


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(payload: AnalyzeRequest) -> dict:
    """Analyze multi-document corpus and return contradiction/consensus report."""
    docs: List[InputDocument] = [
        InputDocument(doc_id=f"d{i}", source=document.source, text=document.text)
        for i, document in enumerate(payload.documents)
    ]
    result = analyze_documents(docs)
    global _last_result
    _last_result = result
    return result


@app.get("/result", response_model=AnalyzeResponse)
def last_result() -> dict:
    """Get latest computed analysis result."""
    if _last_result is None:
        raise HTTPException(status_code=404, detail="No analysis has been run yet.")
    return _last_result


@app.get("/health")
def health() -> dict:
    """Service health endpoint."""
    return {"status": "ok"}


@app.post("/upload-documents")
async def upload_documents(files: List[UploadFile] = File(...)) -> dict:
    """Parse uploaded documents and return extracted text payloads."""
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")
    if len(files) > UPLOAD_MAX_FILES:
        raise HTTPException(
            status_code=400,
            detail=f"Too many files ({len(files)}). Maximum allowed is {UPLOAD_MAX_FILES}.",
        )

    parsed = []
    for file in files:
        parsed_file = await parse_uploaded_file(file, max_bytes=UPLOAD_MAX_BYTES)
        parsed.append(parsed_file.model_dump())

    return {"documents": parsed, "count": len(parsed)}
