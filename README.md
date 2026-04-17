# Multi-Document Contradiction & Consensus Analyzer 

This project analyzes multiple documents and identifies:
- key extracted claims,
- agreement vs contradiction relations,
- confidence scores per claim,
- supporting and contradicting snippets.

It uses a Python `FastAPI` backend with a minimal web UI.

## Features

- Multi-document ingestion (minimum 3 documents)
- Sentence segmentation + rule-based claim extraction
- TF-IDF similarity clustering for claim grouping
- Lightweight NLI-style relation detection:
  - `entailment`
  - `contradiction`
  - `neutral`
- Confidence scoring based on:
  - support count,
  - contradiction count,
  - source signal,
  - cluster cohesion
- JSON API and browser-based UI

## Project Structure

- `app/main.py` - FastAPI app and routes
- `app/schemas.py` - API request/response schemas
- `app/pipeline/ingest.py` - normalization and sentence segmentation
- `app/pipeline/claims.py` - claim extraction
- `app/pipeline/cluster.py` - embedding and clustering
- `app/pipeline/nli.py` - relation inference
- `app/pipeline/graph.py` - claim graph model
- `app/pipeline/score.py` - confidence scoring
- `app/pipeline/orchestrator.py` - end-to-end pipeline coordination
- `app/static/index.html` - minimal frontend
- `tests/` - unit and API tests
- `data/sample_documents.json` - sample request payload

## Setup

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

## Run

Start the server:

```powershell
uvicorn app.main:app --reload
```

Then open:
- UI: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## API Usage

### Analyze documents

`POST /analyze`

Request body:

```json
{
  "documents": [
    { "source": "Medical News A", "text": "The drug reduces symptoms." },
    { "source": "Clinical Trial B", "text": "The drug does not reduce symptoms." },
    { "source": "Journal C", "text": "Researchers found reduced symptoms." }
  ]
}
```

### Retrieve latest result

`GET /result`

### Health check

`GET /health`

## Tests

Run tests with:

```powershell
pytest -q
```

## Notes

- For stronger quality, replace `app/pipeline/nli.py` with a transformer-based NLI model.
