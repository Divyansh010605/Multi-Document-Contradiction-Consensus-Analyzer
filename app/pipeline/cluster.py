"""Claim embedding and clustering."""

from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.pipeline.claims import Claim


def embed_claims(claims: List[Claim]) -> Tuple[np.ndarray, np.ndarray]:
    """Compute TF-IDF vectors and cosine similarity matrix."""
    if not claims:
        return np.array([]), np.array([])
    texts = [claim.normalized_text for claim in claims]
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
    vectors = vectorizer.fit_transform(texts).toarray()
    similarity = cosine_similarity(vectors)
    return vectors, similarity


def cluster_claims(claims: List[Claim], similarity_threshold: float = 0.35) -> Dict[str, int]:
    """
    Cluster semantically similar claims.

    Lower thresholds produce larger clusters. Output maps claim_id -> cluster_id.
    """
    if not claims:
        return {}
    if len(claims) == 1:
        return {claims[0].claim_id: 0}

    vectors, _ = embed_claims(claims)
    if vectors.size == 0:
        return {claim.claim_id: idx for idx, claim in enumerate(claims)}

    clustering = AgglomerativeClustering(
        metric="cosine",
        linkage="average",
        distance_threshold=1.0 - similarity_threshold,
        n_clusters=None,
    )
    labels = clustering.fit_predict(vectors)
    return {claim.claim_id: int(label) for claim, label in zip(claims, labels)}


def cluster_cohesion(claims: List[Claim], cluster_map: Dict[str, int]) -> Dict[int, float]:
    """Estimate cohesion score for each cluster from average similarity."""
    _, similarity = embed_claims(claims)
    if similarity.size == 0:
        return {}

    cluster_to_indices: Dict[int, List[int]] = {}
    for idx, claim in enumerate(claims):
        cluster_id = cluster_map.get(claim.claim_id, -1)
        cluster_to_indices.setdefault(cluster_id, []).append(idx)

    cohesion: Dict[int, float] = {}
    for cluster_id, indices in cluster_to_indices.items():
        if len(indices) <= 1:
            cohesion[cluster_id] = 1.0
            continue
        values = []
        for i in indices:
            for j in indices:
                if i >= j:
                    continue
                values.append(float(similarity[i, j]))
        cohesion[cluster_id] = float(np.mean(values)) if values else 1.0
    return cohesion
