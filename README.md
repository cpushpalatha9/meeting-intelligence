# AI-Career Intelligence Platform — M1 to M4

A production-oriented meeting intelligence platform that transforms meeting audio/text into structured intelligence, persistent knowledge, semantic search, grounded RAG answers, analytics, reports, authentication, provider-ready integrations and deployment checks.

## Milestones

### M1 — Audio Processing & Transcription
- Audio/video upload validation
- Faster-Whisper transcription
- Transcript validation
- NLP preprocessing
- VADER sentiment analysis
- WER/accuracy lab

### M2 — Summarization & Action Extraction
- Gemini LLM processing
- Reusable prompt/schema flow
- Summary, key points and decisions
- Action items with assignee/deadline/priority/status
- Participant/responsibility mapping
- SQLite persistence
- Retry, quota and temporary failure handling

### M3 — Knowledge Repository, Semantic Search & RAG
- Historical meeting repository
- Gemini embeddings
- ChromaDB vector memory
- Semantic search
- Grounded RAG question answering
- Existing FastAPI integration
- Edge-case/failure handling

### M4 — Dashboard, Integrations & Deployment
- Streamlit dashboard and meeting analytics
- PDF and CSV report export
- Authentication and session access
- Owner-aware meeting retrieval
- Zoom and Google Meet connector-ready architecture
- FastAPI `/meetings`, `/meetings/{id}`, `/search`, `/ask`
- Deployment readiness checks

> Live Zoom/Google Meet recording retrieval requires provider OAuth credentials and the provider's approved recording permissions/API access. Downloaded recordings can already enter the existing M1-M3 pipeline.

## Run

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
streamlit run app.py
```

API:

```powershell
uvicorn api:app --reload
```

## Environment

Keep API keys only in `.env`; never commit `.env` to GitHub.

## Main workflow

`Audio/Text → Validation → Whisper → Preprocessing → VADER → Gemini → Structured Intelligence → SQLite → Embeddings → ChromaDB → Semantic Search → RAG → Dashboard/Reports/API`
