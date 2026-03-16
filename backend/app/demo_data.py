from __future__ import annotations

from app.models import ListeningEvent, SessionState, ThoughtEvent
from app.services.analyzer import analyze_session
from app.store import InMemoryStore

DEMO_LISTENING_EVENTS = [
    {
        "platform": "spotify",
        "title": "Households, Habits, and Green Purchasing",
        "creator": "Behavior Lab",
        "content_url": "https://open.spotify.com/show/demo-learning-partner",
        "transcript_chunk": (
            "The speaker argues that household liquidity and time pressure shape whether families "
            "follow through on environmentally friendly purchases. Two households can express the "
            "same values yet behave differently because constraints change what feels affordable "
            "and convenient."
        ),
        "topics": ["consumer behavior", "household", "sustainability"],
        "duration_seconds": 420,
    },
    {
        "platform": "youtube",
        "title": "Why Packaging and Power Are AI Infrastructure Bottlenecks",
        "creator": "Compute Frontier",
        "content_url": "https://www.youtube.com/watch?v=demo-learning-partner",
        "transcript_chunk": (
            "The video explains that semiconductor packaging, power delivery, and inference demand "
            "are creating bottlenecks in AI infrastructure. More compute is not just a model problem; "
            "it is also a supply chain and deployment problem."
        ),
        "topics": ["semiconductor", "ai infrastructure", "bottleneck", "inference"],
        "duration_seconds": 510,
    },
    {
        "platform": "spotify",
        "title": "Real Estate Divergence Signals",
        "creator": "Macro Streets",
        "content_url": "https://open.spotify.com/episode/demo-learning-partner",
        "transcript_chunk": (
            "The host says real estate divergence shows up when neighborhoods with similar starting "
            "points separate because rates, migration, and local income shocks compound differently. "
            "Divergence is presented as a measurable pattern instead of a vague story."
        ),
        "topics": ["real estate", "divergence"],
        "duration_seconds": 360,
    },
]

DEMO_THOUGHT_EVENTS = [
    {
        "transcript_chunk": (
            "I want to test whether household constraints explain the gap between climate intent "
            "and actual sustainable purchasing behavior."
        ),
        "confidence": 0.89,
    },
    {
        "transcript_chunk": (
            "Could real estate divergence be analyzed like an allocation bottleneck, where a few "
            "inputs create outsized separation across markets?"
        ),
        "confidence": 0.82,
    },
    {
        "transcript_chunk": (
            "For the AI infra project, I should track which bottlenecks are fabrication limited "
            "versus power limited versus inference demand limited."
        ),
        "confidence": 0.9,
    },
]


def bootstrap_demo_session(store: InMemoryStore, online_verification: bool) -> SessionState:
    session_id = store.create_session()
    for event_data in DEMO_LISTENING_EVENTS:
        store.append_listening_event(session_id, ListeningEvent(**event_data))
    for thought_data in DEMO_THOUGHT_EVENTS:
        store.append_thought_event(session_id, ThoughtEvent(**thought_data))

    session = store.get_session(session_id)
    if session is None:
        raise RuntimeError("Demo session could not be created")

    session.latest_insight = analyze_session(
        session=session,
        profile=store.profile,
        online_verification=online_verification,
    )
    return session
