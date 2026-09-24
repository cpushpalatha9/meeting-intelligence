# Meeting Intelligence System

Integrated Milestone 1–3 implementation.

## Milestone 1
- Audio/video upload and validation
- Faster-Whisper transcription
- Transcript validation and preprocessing
- VADER sentiment analysis
- Streamlit workflow
- WER/accuracy testing

## Milestone 2
- Gemini structured JSON intelligence
- Reusable prompts
- Pydantic validation
- Long-transcript handling
- Retry/quota/error handling
- Summary, key points, decisions
- Action items with assignee/deadline/priority/status
- Participant/responsibility mapping
- SQLite persistence
- FastAPI integration

## Milestone 3
- Historical meeting repository
- Gemini embeddings
- ChromaDB vector storage
- Re-indexing
- Metadata filtering
- Semantic search
- Grounded RAG Q&A
- Local evidence fallback when generation quota is unavailable

## Run

1. `python -m pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and add your Gemini API key.
3. `streamlit run app.py`

FastAPI:
`uvicorn api:app --reload`
