"""Confidence scoring for claims."""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List

from pydantic import BaseModel

from app.pipeline.claims import Claim
from app.pipeline.nli import ClaimRelation


class ClaimScore(BaseModel):
    """Computed confidence score for a claim."""

    claim_id: str
    confidence: float
    support_count: int
    contradiction_count: int
    rationale: Dict[str, float]


def score_claims(
    claims: List[Claim],
    relations: List[ClaimRelation],
    cluster_map: Dict[str, int],
    cohesion_by_cluster: Dict[int, float],
) -> Dict[str, ClaimScore]:
    """Compute confidence per claim using support, consistency, and cohesion."""
    support = defaultdict(int)
    contradiction = defaultdict(int)

    for relation in relations:
        if relation.label == "entailment":
            support[relation.claim_id_a] += 1
            support[relation.claim_id_b] += 1
        elif relation.label == "contradiction":
            contradiction[relation.claim_id_a] += 1
            contradiction[relation.claim_id_b] += 1

    source_presence = defaultdict(set)
    for claim in claims:
        source_presence[claim.claim_id].add(claim.source)

    scores: Dict[str, ClaimScore] = {}
    for claim in claims:
        support_count = support[claim.claim_id]
        contradiction_count = contradiction[claim.claim_id]
        cluster_id = cluster_map.get(claim.claim_id, -1)
        cohesion = cohesion_by_cluster.get(cluster_id, 0.5)
        source_count = len(source_presence[claim.claim_id])

        support_factor = min(1.0, support_count / 3.0)
        contradiction_penalty = min(1.0, contradiction_count / 3.0)
        source_factor = min(1.0, source_count / 2.0)
        consistency = max(0.0, 1.0 - contradiction_penalty)

        confidence = 0.4 * support_factor + 0.2 * source_factor + 0.25 * consistency + 0.15 * cohesion
        scores[claim.claim_id] = ClaimScore(
            claim_id=claim.claim_id,
            confidence=round(float(confidence), 3),
            support_count=support_count,
            contradiction_count=contradiction_count,
            rationale={
                "support_factor": round(support_factor, 3),
                "source_factor": round(source_factor, 3),
                "consistency": round(consistency, 3),
                "cluster_cohesion": round(float(cohesion), 3),
            },
        )
    return scores
