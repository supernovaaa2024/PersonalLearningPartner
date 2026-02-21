from __future__ import annotations

from uuid import uuid4

from app.models import InterestProfile, ListeningEvent, Project, SessionState, ThoughtEvent


class InMemoryStore:
    def __init__(self) -> None:
        self.profile = InterestProfile(
            user_id="default",
            projects=[
                Project(
                    id="consumer-behavior",
                    name="Consumer Behavior",
                    description=(
                        "How household characteristics affect purchasing "
                        "behavior and environmentally friendly decisions."
                    ),
                    tags=["consumer behavior", "households", "sustainability"],
                ),
                Project(
                    id="real-estate-divergence",
                    name="Real Estate Divergence",
                    description="Research project studying divergence patterns in real estate.",
                    tags=["real estate", "divergence"],
                ),
                Project(
                    id="ai-infra-landscape",
                    name="AI Infra and Semiconductors",
                    description=(
                        "Track semiconductor landscape, AI infrastructure bottlenecks, "
                        "and major AI news."
                    ),
                    tags=["AI", "semiconductors", "infrastructure", "news"],
                ),
            ],
            interests=[
                "consumer behavior",
                "real estate divergence",
                "AI semiconductors",
                "AI infrastructure bottlenecks",
                "AI news",
            ],
            questions=[],
        )
        self.sessions: dict[str, SessionState] = {}

    def create_session(self) -> str:
        session_id = str(uuid4())
        self.sessions[session_id] = SessionState(id=session_id)
        return session_id

    def get_session(self, session_id: str) -> SessionState | None:
        return self.sessions.get(session_id)

    def append_listening_event(self, session_id: str, event: ListeningEvent) -> SessionState | None:
        session = self.get_session(session_id)
        if session is None:
            return None
        session.listening_events.append(event)
        return session

    def append_thought_event(self, session_id: str, event: ThoughtEvent) -> SessionState | None:
        session = self.get_session(session_id)
        if session is None:
            return None
        session.thought_events.append(event)
        return session
