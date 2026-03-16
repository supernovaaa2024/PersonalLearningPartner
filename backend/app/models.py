from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class SourcePlatform(str, Enum):
    YOUTUBE = "youtube"
    SPOTIFY = "spotify"
    LOCAL_AUDIO = "local_audio"
    MANUAL = "manual"


class VerificationStatus(str, Enum):
    VERIFIED = "verified"
    DISPUTED = "disputed"
    UNCERTAIN = "uncertain"
    PENDING_ONLINE_CHECK = "pending_online_check"


class LinkSuggestion(BaseModel):
    topic: str
    reason: str
    url: str


class VerificationItem(BaseModel):
    claim: str
    status: VerificationStatus
    note: str
    source_url: Optional[str] = None


class SessionInsight(BaseModel):
    summary: str
    explanation: str
    feedback: str
    verification: list[VerificationItem] = Field(default_factory=list)
    suggested_links: list[LinkSuggestion] = Field(default_factory=list)
    connected_projects: list[str] = Field(default_factory=list)


class ListeningEventIn(BaseModel):
    platform: SourcePlatform
    title: str
    creator: Optional[str] = None
    content_url: Optional[str] = None
    transcript_chunk: str
    topics: list[str] = Field(default_factory=list)
    duration_seconds: Optional[int] = None


class ListeningEvent(ListeningEventIn):
    occurred_at: datetime = Field(default_factory=utc_now)


class ThoughtEventIn(BaseModel):
    transcript_chunk: str
    confidence: float = Field(default=0.7, ge=0.0, le=1.0)


class ThoughtEvent(ThoughtEventIn):
    occurred_at: datetime = Field(default_factory=utc_now)


class Project(BaseModel):
    id: str
    name: str
    description: str
    tags: list[str] = Field(default_factory=list)


class InterestProfile(BaseModel):
    user_id: str = "default"
    projects: list[Project] = Field(default_factory=list)
    interests: list[str] = Field(default_factory=list)
    questions: list[str] = Field(default_factory=list)


class ProfilePatch(BaseModel):
    interests: Optional[list[str]] = None
    questions: Optional[list[str]] = None


class SessionState(BaseModel):
    id: str
    created_at: datetime = Field(default_factory=utc_now)
    listening_events: list[ListeningEvent] = Field(default_factory=list)
    thought_events: list[ThoughtEvent] = Field(default_factory=list)
    latest_insight: Optional[SessionInsight] = None


class CreateSessionResponse(BaseModel):
    session_id: str
