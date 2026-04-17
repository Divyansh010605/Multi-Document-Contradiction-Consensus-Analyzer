"""End-to-end orchestration for contradiction and consensus analysis."""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List

from app.pipeline.claims import Claim, extract_claims
from app.pipeline.cluster import cluster_claims, cluster_cohesion
from app.pipeline.graph import build_claim_graph
from app.pipeline.ingest import InputDocument, segment_sentences
from app.pipeline.nli import ClaimRelation, infer_relations
from app.pipeline.score import score_claims


def _group_supporting_and_contradicting_snippets(
    claims: List[Claim], relations: List[ClaimRelation]
) -> Dict[str, Dict[str, List[str]]]:
    by_id = {claim.claim_id: claim for claim in claims}
    result: Dict[str, Dict[str, List[str]]] = defaultdict(lambda: {"supporting": [], "contradicting": []})
    for relation in relations:
        a = by_id.get(relation.claim_id_a)
        b = by_id.get(relation.claim_id_b)
        if not a or not b:
            continue
        if relation.label == "entailment":
            result[a.claim_id]["supporting"].append(b.text)
            result[b.claim_id]["supporting"].append(a.text)
        elif relation.label == "contradiction":
            result[a.claim_id]["contradicting"].append(b.text)
            result[b.claim_id]["contradicting"].append(a.text)
    return result


def analyze_documents(documents: List[InputDocument]) -> Dict:
    """Run full analysis pipeline and return structured output."""
    sentences = segment_sentences(documents)
    claims = extract_claims(sentences)
    cluster_map = cluster_claims(claims)
    cohesion = cluster_cohesion(claims, cluster_map)
    relations = infer_relations(claims, cluster_map)
    graph = build_claim_graph(claims, cluster_map, relations)
    score_map = score_claims(claims, relations, cluster_map, cohesion)
    snippets = _group_supporting_and_contradicting_snippets(claims, relations)

    claim_results = []
    for claim in claims:
        score = score_map[claim.claim_id]
        cluster_id = cluster_map.get(claim.claim_id, -1)
        claim_results.append(
            {
                "claim_id": claim.claim_id,
                "text": claim.text,
                "source": claim.source,
                "cluster_id": cluster_id,
                "confidence": score.confidence,
                "support_count": score.support_count,
                "contradiction_count": score.contradiction_count,
                "rationale": score.rationale,
                "supporting_snippets": snippets[claim.claim_id]["supporting"][:3],
                "contradicting_snippets": snippets[claim.claim_id]["contradicting"][:3],
            }
        )

    return {
        "stats": {
            "document_count": len(documents),
            "sentence_count": len(sentences),
            "claim_count": len(claims),
            "relation_count": len(relations),
            "cluster_count": len(set(cluster_map.values())) if cluster_map else 0,
        },
        "claims": claim_results,
        "relations": [relation.model_dump() for relation in relations],
        "graph": graph.model_dump(),
    }
