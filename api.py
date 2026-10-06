from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from services.llm_service import LLMService
from services.database_service import init_database, save_meeting, get_all_meetings, get_meeting
from services.meeting_service import clean_action_items, clean_participants
from services.search_service import SearchService
from services.rag_service import RAGService

app = FastAPI(title="AI-Career Intelligence Platform API", version="2.0.0")
init_database()

class MeetingRequest(BaseModel):
    title: str
    transcript: str

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

class AskRequest(BaseModel):
    question: str
    top_k: int = 5

@app.get("/")
def root():
    return {"service":"AI-Career Intelligence Platform API","status":"ok","milestones":"M1-M4"}

@app.get("/meetings")
def meetings():
    return {"meetings": get_all_meetings()}

@app.get("/meetings/{meeting_id}")
def meeting(meeting_id: int):
    item = get_meeting(meeting_id)
    if not item:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return item

@app.post("/process-meeting")
def process_meeting(req: MeetingRequest):
    try:
        intelligence = LLMService().process_long_transcript(req.transcript)
        intelligence["action_items"] = clean_action_items(intelligence.get("action_items", []))
        intelligence["participants"] = clean_participants(intelligence.get("participants", []))
        meeting_id = save_meeting(
            req.title, req.transcript, intelligence.get("summary", ""),
            **{k: intelligence.get(k, []) for k in ["key_points","decisions","action_items","participants","deadlines","priorities"]}
        )
        return {"meeting_id": meeting_id, "intelligence": intelligence}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search")
def search(req: SearchRequest):
    try:
        return {"query": req.query, "results": SearchService().search(req.query, top_k=req.top_k)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask")
def ask(req: AskRequest):
    try:
        return RAGService().answer(req.question, top_k=req.top_k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
