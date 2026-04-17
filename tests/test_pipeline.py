"""Tests for the NLP analysis pipeline."""

from app.pipeline.ingest import InputDocument
from app.pipeline.orchestrator import analyze_documents


def test_pipeline_finds_claims_and_relations() -> None:
    docs = [
        InputDocument(
            doc_id="d0",
            source="Source A",
            text="The vaccine reduces severe disease. It improves recovery.",
        ),
        InputDocument(
            doc_id="d1",
            source="Source B",
            text="The vaccine does not reduce severe disease in this cohort.",
        ),
        InputDocument(
            doc_id="d2",
            source="Source C",
            text="Researchers found the vaccine reduces severe disease by 40 percent.",
        ),
    ]

    result = analyze_documents(docs)

    assert result["stats"]["document_count"] == 3
    assert result["stats"]["claim_count"] >= 2
    labels = {item["label"] for item in result["relations"]}
    assert "contradiction" in labels or "entailment" in labels


def test_pipeline_adds_confidence_to_each_claim() -> None:
    docs = [
        InputDocument(doc_id="d0", source="S1", text="Exercise improves cardiovascular health in adults."),
        InputDocument(doc_id="d1", source="S2", text="Exercise does not improve cardiovascular health in adults."),
        InputDocument(doc_id="d2", source="S3", text="A study says exercise improves cardiovascular health outcomes."),
    ]
    result = analyze_documents(docs)
    assert result["claims"], "Expected at least one claim"
    for claim in result["claims"]:
        assert 0.0 <= claim["confidence"] <= 1.0
        assert "rationale" in claim
