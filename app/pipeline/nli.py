"""Lightweight NLI-style agreement/contradiction detection."""

from __future__ import annotations

import re
from typing import Dict, List, Literal

from pydantic import BaseModel
from app.pipeline.claims import Claim
from app.pipeline.cluster import embed_claims


Label = Literal["entailment", "contradiction", "neutral"]


class ClaimRelation(BaseModel):
    """Relation between two claim statements."""

    claim_id_a: str
    claim_id_b: str
    label: Label
    confidence: float


_NEGATIONS = {"not", "no", "never", "none", "without", "cannot", "n't"}
_NUM_RE = re.compile(r"\d+(?:\.\d+)?")


def _token_set(text: str) -> set[str]:
    return set(text.lower().split())


def _negation_mismatch(a: str, b: str) -> bool:
    a_tokens = _token_set(a)
    b_tokens = _token_set(b)
    a_neg = any(tok in a_tokens for tok in _NEGATIONS)
    b_neg = any(tok in b_tokens for tok in _NEGATIONS)
    return a_neg != b_neg


def _numeric_conflict(a: str, b: str) -> bool:
    a_nums = _NUM_RE.findall(a)
    b_nums = _NUM_RE.findall(b)
    return bool(a_nums and b_nums and a_nums != b_nums)


def infer_relations(claims: List[Claim], cluster_map: Dict[str, int]) -> List[ClaimRelation]:
    """
    Infer pairwise relationships within each cluster.

    This approximates NLI behavior for an MVP:
    - high lexical similarity + no conflict => entailment
    - high lexical similarity + negation/number conflict => contradiction
    - otherwise neutral
    """
    if len(claims) < 2:
        return []

    _, sim = embed_claims(claims)
    if sim.size == 0:
        return []

    relations: List[ClaimRelation] = []
    for i, claim_a in enumerate(claims):
        for j, claim_b in enumerate(claims):
            if i >= j:
                continue
            if cluster_map.get(claim_a.claim_id) != cluster_map.get(claim_b.claim_id):
                continue

            similarity = float(sim[i, j])
            contradiction = _negation_mismatch(claim_a.text, claim_b.text) or _numeric_conflict(
                claim_a.text, claim_b.text
            )
            if similarity >= 0.55 and contradiction:
                label: Label = "contradiction"
                confidence = min(1.0, 0.6 + similarity * 0.35)
            elif similarity >= 0.5:
                label = "entailment"
                confidence = min(1.0, 0.5 + similarity * 0.45)
            else:
                label = "neutral"
                confidence = max(0.1, 1.0 - similarity)

            relations.append(
                ClaimRelation(
                    claim_id_a=claim_a.claim_id,
                    claim_id_b=claim_b.claim_id,
                    label=label,
                    confidence=round(confidence, 3),
                )
            )
    return relations
