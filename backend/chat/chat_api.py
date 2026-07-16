"""
backend/chat/chat_api.py
Enterprise Chat API
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid

app=FastAPI(title="Enterprise Chat API")
sessions={}

class ChatRequest(BaseModel):
    session_id:str|None=None
    question:str

@app.post("/chat")
def chat(req:ChatRequest):
    sid=req.session_id or str(uuid.uuid4())
    sessions.setdefault(sid,[])
    answer=f"Demo answer for: {req.question}"
    sources=[{"file":"HR Policy.pdf","page":18,"section":"4.2"}]
    sessions[sid].append({"question":req.question,"answer":answer})
    return {"session_id":sid,"answer":answer,"sources":sources,"confidence":96}

@app.post("/chat/history")
def history(body:dict):
    sid=body.get("session_id")
    if sid not in sessions:
        raise HTTPException(404,"Session not found")
    return {"session_id":sid,"history":sessions[sid]}

@app.delete("/chat/history")
def delete_history(body:dict):
    sid=body.get("session_id")
    sessions.pop(sid,None)
    return {"message":"History deleted"}

@app.get("/chat/session/{session_id}")
def get_session(session_id:str):
    if session_id not in sessions:
        raise HTTPException(404,"Session not found")
    return {"session_id":session_id,"messages":sessions[session_id]}
