# NexusDocs: Multi-Document Contradiction & Consensus Analyzer

NexusDocs is an advanced NLP-driven diagnostic tool designed to ingest a corpus of documents and automatically map out agreements (consensus) and disagreements (contradictions) across them. It helps researchers, journalists, and analysts quickly verify claims by cross-referencing information from multiple sources.

## 🧠 NLP Diagnostic Pipeline

The core of NexusDocs is a multi-stage Natural Language Processing pipeline that transforms raw text into structured insights.

### 1. Linguistic Ingestion & Segmentation
*   **Preprocessing**: Normalization of diverse document formats (.pdf, .docx, .json, .txt).
*   **Sentence Segmentation**: Utilizing heuristic-based tokenization to break documents into atomic linguistic units, ensuring context is preserved while isolating specific claims.

### 2. Semantic Claim Extraction
*   **Syntactic Analysis**: Identifying potential factual claims by filtering sentences based on linguistic structure (SVO patterns) and removing subjective or filler content.
*   **Rule-Based Filtering**: Eliminating questions, greetings, and short fragments to focus on high-signal informational units.

### 3. Claim Clustering (TF-IDF & Cosine Similarity)
*   **Vectorization**: Transforming extracted claims into numerical representations using **TF-IDF (Term Frequency-Inverse Document Frequency)** to weight important keywords.
*   **Unsupervised Clustering**: Grouping semantically similar claims across different documents into "Claim Clusters." This allows the engine to compare what different sources are saying about the same specific topic.

### 4. Relation Inference (NLI Engine)
*   **Natural Language Inference**: For each cluster, the engine performs a pairwise comparison of claims to detect logical relationships:
    *   **Entailment (Consensus)**: Multiple sources agree on the same fact.
    *   **Contradiction**: Sources provide conflicting or opposing information.
    *   **Neutral**: Information is related but not logically connected in terms of truth-value.

### 5. Confidence Scoring & Consensus Mapping
*   **Probabilistic Scoring**: Calculating a confidence value for every extracted claim based on:
    *   **Support Count**: Number of independent sources confirming the claim.
    *   **Contradiction Ratio**: Frequency of opposing evidence.
    *   **Source Diversity**: Weighted signal from unique document origins.
    *   **Cluster Cohesion**: Mathematical tightness of the semantic grouping.

---

## 🛠️ Project Structure

- `app/main.py` - FastAPI entrypoint and static file routing.
- `app/pipeline/orchestrator.py` - Coordination of the full NLP lifecycle.
- `app/pipeline/nli.py` - Logic for logical relation detection (Entailment/Contradiction).
- `app/pipeline/cluster.py` - TF-IDF vectorization and claim grouping.
- `app/static/` - Premium "NexusDocs" dashboard (HTML/CSS/JS).

---

## 🚀 Getting Started

### 1. Installation
Install the necessary Python dependencies globally or in a virtual environment:
```powershell
pip install -r requirements.txt
```

### 2. Run the Application
Start the NexusDocs engine:
```powershell
python -m uvicorn app.main:app --reload
```

### 3. Usage
1. Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser.
2. Add at least **3 documents** (manual text or file upload).
3. Click **"Run Analysis"** to expand the side-by-side diagnostic dashboard.
4. Inspect the **Claim Cards** to see confidence scores and supporting/contradicting snippets.

---

## 🧪 Testing
Run the automated test suite to verify pipeline integrity:
```powershell
pytest -q
```

---

## 📅 Roadmap & Enhancements
- [ ] Integration with Transformer-based NLI models (e.g., RoBERTa-large-mnli) for higher accuracy.
- [ ] Visual Relationship Graphs for claim networks.
- [ ] Multi-language support using cross-lingual embeddings.
