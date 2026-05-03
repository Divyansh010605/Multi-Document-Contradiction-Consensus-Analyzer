import sys
import json
sys.path.append('.')
from app.pipeline.ingest import InputDocument
from app.pipeline.orchestrator import analyze_documents
from app.pipeline.claims import extract_claims
from app.pipeline.ingest import segment_sentences
from app.pipeline.cluster import embed_claims
from app.pipeline.nli import infer_relations

docs = [
    InputDocument(doc_id='1', source='doc1', text='Drinking moderate amounts of coffee daily, around 2 to 3 cups, significantly lowers the risk of developing cardiovascular disease. The antioxidants found in coffee provide a protective effect for the heart.'),
    InputDocument(doc_id='2', source='doc2', text='Recent medical research indicates that even moderate coffee consumption increases the risk of high blood pressure and heart palpitations. Caffeine is ultimately detrimental to long-term cardiovascular health.'),
    InputDocument(doc_id='3', source='doc3', text='A massive longitudinal study confirms that 2 to 4 cups of coffee per day provides a strong protective effect against heart disease, underscoring its cardiovascular benefits.')
]

sentences = segment_sentences(docs)
claims = extract_claims(sentences)
vectors, similarity = embed_claims(claims)

print("CLAIMS:")
for i, c in enumerate(claims):
    print(f"{i}: {c.text}")

print("\nSIMILARITY MATRIX:")
print(similarity)

print("\nNLI:")
relations = infer_relations(claims, {c.claim_id: 0 for c in claims}, similarity=similarity)
for r in relations:
    print(r)
