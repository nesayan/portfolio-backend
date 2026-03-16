# Agentic RAG Backend (FastAPI)

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt --no-cache-dir
```

3. Configure environment variables in `core/.env` (see `core/.env.example`).

Required variables:

- `GROQ_API_KEY`
- `LLM_MODEL`
- `EMBEDDING_MODEL`
- `QDRANT_ENDPOINT`
- `QDRANT_API_KEY`
- `VECTOR_COLLECTION` (optional, defaults to `documents`)
- `PRIVATE_ENDPOINT_USERNAME` (required for `/rag/run`)
- `PRIVATE_ENDPOINT_PASSWORD` (required for `/rag/run`)

## Run

```bash
uvicorn main:app --reload
```

## Endpoints

- `GET /` basic status message
- `GET /health` health check
