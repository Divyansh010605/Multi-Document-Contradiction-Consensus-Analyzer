"""Document ingestion and sentence segmentation utilities."""

from __future__ import annotations

import re
from typing import List

from pydantic import BaseModel


class InputDocument(BaseModel):
    """Normalized input document."""

    doc_id: str
    source: str
    text: str


class SentenceUnit(BaseModel):
    """Single sentence extracted from a source document."""

    sentence_id: str
    doc_id: str
    source: str
    text: str


_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
_SPACE_RE = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    """Collapse extra whitespace and trim boundaries."""
    text = _SPACE_RE.sub(" ", text or "")
    return text.strip()


def segment_sentences(documents: List[InputDocument]) -> List[SentenceUnit]:
    """Split normalized documents into sentence units."""
    sentence_units: List[SentenceUnit] = []
    for doc in documents:
        normalized = normalize_text(doc.text)
        if not normalized:
            continue
        raw_sentences = _SENTENCE_SPLIT_RE.split(normalized)
        for idx, sentence in enumerate(raw_sentences):
            clean_sentence = sentence.strip()
            if not clean_sentence:
                continue
            sentence_units.append(
                SentenceUnit(
                    sentence_id=f"{doc.doc_id}-s{idx}",
                    doc_id=doc.doc_id,
                    source=doc.source,
                    text=clean_sentence,
                )
            )
    return sentence_units
