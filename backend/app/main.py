from __future__ import annotations

from fastapi import FastAPI, HTTPException

from app.models import (
    CreateSessionResponse,
    ListeningEvent,
    ListeningEventIn,
    ProfilePatch,
    Project,
    SessionInsight,
    SessionState,
    ThoughtEvent,
    ThoughtEventIn,
)
from app.services.analyzer import analyze_session
from app.store import InMemoryStore

app = FastAPI(title="Learning Partner API", version="0.1.0")
store = InMemoryStore()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/profile")
def get_profile():
    return store.profile


@app.patch("/profile")
def patch_profile(patch: ProfilePatch):
    if patch.interests is not None:
        store.profile.interests = patch.interests
    if patch.questions is not None:
        store.profile.questions = patch.questions
    return store.profile


@app.post("/profile/projects")
def add_project(project: Project):
    if any(existing.id == project.id for existing in store.profile.projects):
        raise HTTPException(status_code=400, detail="Project ID already exists")
    store.profile.projects.append(project)
    return project


@app.post("/sessions", response_model=CreateSessionResponse)
def create_session():
    session_id = store.create_session()
    return CreateSessionResponse(session_id=session_id)


@app.get("/sessions/{session_id}", response_model=SessionState)
def get_session(session_id: str):
    session = store.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@app.post("/sessions/{session_id}/events/listening", response_model=SessionState)
def add_listening_event(session_id: str, event_in: ListeningEventIn):
    session = store.append_listening_event(session_id, ListeningEvent(**event_in.model_dump()))
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@app.post("/sessions/{session_id}/events/thought", response_model=SessionState)
def add_thought_event(session_id: str, event_in: ThoughtEventIn):
    session = store.append_thought_event(session_id, ThoughtEvent(**event_in.model_dump()))
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@app.post("/sessions/{session_id}/analyze", response_model=SessionInsight)
def analyze(session_id: str, online_verification: bool = False):
    session = store.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    insight = analyze_session(
        session=session,
        profile=store.profile,
        online_verification=online_verification,
    )
    session.latest_insight = insight
    return insight
