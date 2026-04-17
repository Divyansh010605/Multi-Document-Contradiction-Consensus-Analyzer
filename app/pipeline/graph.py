"""Graph builder for claim relations."""

from __future__ import annotations

from typing import Dict, List

from pydantic import BaseModel

from app.pipeline.claims import Claim
from app.pipeline.nli import ClaimRelation


class GraphNode(BaseModel):
    """Claim node in relation graph."""

    claim_id: str
    cluster_id: int
    text: str
    source: str


class GraphEdge(BaseModel):
    """Typed relation edge."""

    source_claim_id: str
    target_claim_id: str
    relation: str
    confidence: float


class ClaimGraph(BaseModel):
    """Graph container for analysis output."""

    nodes: List[GraphNode]
    edges: List[GraphEdge]


def build_claim_graph(
    claims: List[Claim], cluster_map: Dict[str, int], relations: List[ClaimRelation]
) -> ClaimGraph:
    """Build graph with nodes for claims and edges for inferred relations."""
    nodes = [
        GraphNode(
            claim_id=claim.claim_id,
            cluster_id=cluster_map.get(claim.claim_id, -1),
            text=claim.text,
            source=claim.source,
        )
        for claim in claims
    ]
    edges = [
        GraphEdge(
            source_claim_id=relation.claim_id_a,
            target_claim_id=relation.claim_id_b,
            relation=relation.label,
            confidence=relation.confidence,
        )
        for relation in relations
        if relation.label != "neutral"
    ]
    return ClaimGraph(nodes=nodes, edges=edges)
