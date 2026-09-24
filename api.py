from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from services.llm_service import LLMService
from services.database_service import init_database, save_meeting
from services.meeting_service import clean_action_items, clean_participants

app=FastAPI(title="Meeting Intelligence API",version="1.0.0")
init_database()

class MeetingRequest(BaseModel):
    title:str
    transcript:str

@app.get("/")
def root():
    return {"service":"Meeting Intelligence API","status":"ok"}

@app.post("/process-meeting")
def process_meeting(req:MeetingRequest):
    try:
        intelligence=LLMService().process_long_transcript(req.transcript)
        intelligence["action_items"]=clean_action_items(intelligence["action_items"])
        intelligence["participants"]=clean_participants(intelligence["participants"])
        meeting_id=save_meeting(req.title,req.transcript,intelligence["summary"],**{k:intelligence[k] for k in ["key_points","decisions","action_items","participants","deadlines","priorities"]})
        return {"meeting_id":meeting_id,"intelligence":intelligence}
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
