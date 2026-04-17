"""Claim extraction from sentence units."""

from __future__ import annotations

import re
from typing import List, Set

from pydantic import BaseModel

from app.pipeline.ingest import SentenceUnit


class Claim(BaseModel):
    """Extracted factual claim candidate."""

    claim_id: str
    sentence_id: str
    doc_id: str
    source: str
    text: str
    normalized_text: str


_CLAIM_VERBS = {
    "is",
    "are",
    "was",
    "were",
    "has",
    "have",
    "had",
    "can",
    "could",
    "will",
    "would",
    "should",
    "did",
    "does",
    "do",
    "increased",
    "decreased",
    "causes",
    "prevents",
    "reduces",
    "improves",
}
_NORMALIZE_RE = re.compile(r"[^a-z0-9\s]")


def _normalize_claim_text(text: str) -> str:
    lowered = text.lower()
    lowered = _NORMALIZE_RE.sub(" ", lowered)
    lowered = re.sub(r"\s+", " ", lowered).strip()
    return lowered


def _looks_like_claim(sentence: str) -> bool:
    """Heuristic filter for factual/relational statements."""
    words = sentence.lower().split()
    if len(words) < 4:
        return False
    if words[0] in {"why", "how", "what", "when", "where", "who"}:
        return False
    return any(verb in words for verb in _CLAIM_VERBS)


def extract_claims(sentences: List[SentenceUnit]) -> List[Claim]:
    """Extract claim candidates from sentence units."""
    claims: List[Claim] = []
    seen: Set[str] = set()
    for idx, sentence in enumerate(sentences):
        if not _looks_like_claim(sentence.text):
            continue
        normalized = _normalize_claim_text(sentence.text)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        claims.append(
            Claim(
                claim_id=f"c{idx}",
                sentence_id=sentence.sentence_id,
                doc_id=sentence.doc_id,
                source=sentence.source,
                text=sentence.text,
                normalized_text=normalized,
            )
        )
    return claims
