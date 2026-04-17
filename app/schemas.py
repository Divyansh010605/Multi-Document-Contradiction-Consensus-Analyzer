"""Pydantic schemas for API requests and responses."""

from __future__ import annotations

from typing import Dict, List

from pydantic import BaseModel, Field


class DocumentInput(BaseModel):
    """Single input document payload."""

    source: str = Field(..., min_length=1, description="Source label (news outlet, paper, etc.)")
    text: str = Field(..., min_length=1, description="Document text to analyze")


class AnalyzeRequest(BaseModel):
    """Analysis request payload."""

    documents: List[DocumentInput] = Field(..., min_length=3, description="At least 3 documents")


class ClaimOutput(BaseModel):
    claim_id: str
    text: str
    source: str
    cluster_id: int
    confidence: float
    support_count: int
    contradiction_count: int
    rationale: Dict[str, float]
    supporting_snippets: List[str]
    contradicting_snippets: List[str]


class StatsOutput(BaseModel):
    document_count: int
    sentence_count: int
    claim_count: int
    relation_count: int
    cluster_count: int


class AnalyzeResponse(BaseModel):
    stats: StatsOutput
    claims: List[ClaimOutput]
    relations: List[Dict]
    graph: Dict
