from __future__ import annotations

import re

from app.models import (
    InterestProfile,
    LinkSuggestion,
    SessionInsight,
    SessionState,
    VerificationItem,
    VerificationStatus,
)

TOPIC_LINKS: dict[str, str] = {
    "consumer behavior": "https://en.wikipedia.org/wiki/Consumer_behaviour",
    "household": "https://en.wikipedia.org/wiki/Household",
    "sustainability": "https://en.wikipedia.org/wiki/Sustainability",
    "real estate": "https://en.wikipedia.org/wiki/Real_estate",
    "divergence": "https://en.wikipedia.org/wiki/Divergence",
    "semiconductor": "https://en.wikipedia.org/wiki/Semiconductor_device_fabrication",
    "ai infrastructure": "https://en.wikipedia.org/wiki/Artificial_intelligence#Hardware_and_software",
    "bottleneck": "https://en.wikipedia.org/wiki/Bottleneck_(engineering)",
    "inference": "https://en.wikipedia.org/wiki/Transformer_(deep_learning_architecture)",
}

SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
CLAIM_HINTS = (" is ", " are ", " causes ", " will ", " leads to ", " reduces ", " increases ")


def _join_text(session: SessionState) -> str:
    parts: list[str] = []
    for event in session.listening_events:
        parts.append(event.transcript_chunk.strip())
    for thought in session.thought_events:
        parts.append(thought.transcript_chunk.strip())
    return " ".join(p for p in parts if p)


def _extract_sentences(text: str) -> list[str]:
    if not text:
        return []
    return [s.strip() for s in SENTENCE_SPLIT.split(text) if s.strip()]


def _extract_claims(sentences: list[str], limit: int = 5) -> list[str]:
    claims: list[str] = []
    for sentence in sentences:
        lowered = sentence.lower()
        if any(hint in lowered for hint in CLAIM_HINTS) or re.search(r"\d", sentence):
            claims.append(sentence)
        if len(claims) >= limit:
            break
    return claims


def _extract_topics(text: str) -> list[str]:
    lowered = text.lower()
    topics = [topic for topic in TOPIC_LINKS.keys() if topic in lowered]
    # Keep stable order and uniqueness.
    seen: set[str] = set()
    unique_topics = []
    for topic in topics:
        if topic not in seen:
            unique_topics.append(topic)
            seen.add(topic)
    return unique_topics


def _summary_from_sentences(sentences: list[str]) -> str:
    if not sentences:
        return "No content captured yet."
    return " ".join(sentences[:2])


def _explanation_from_topics(topics: list[str]) -> str:
    if not topics:
        return (
            "The session discussed mixed ideas. Add a few explicit keywords in your thoughts "
            "to improve topic linking and deeper guidance."
        )
    return (
        "This session connects to: "
        + ", ".join(topics[:5])
        + ". The app should verify major claims and then build a study path from foundational "
          "concepts to your project-specific questions."
    )


def _verification_items(claims: list[str], online_verification: bool) -> list[VerificationItem]:
    items: list[VerificationItem] = []
    for claim in claims:
        if online_verification:
            items.append(
                VerificationItem(
                    claim=claim,
                    status=VerificationStatus.UNCERTAIN,
                    note="Needs retrieval pipeline wiring for true source-backed verification.",
                    source_url=None,
                )
            )
        else:
            items.append(
                VerificationItem(
                    claim=claim,
                    status=VerificationStatus.PENDING_ONLINE_CHECK,
                    note="Offline mode: queued for online verification.",
                    source_url=None,
                )
            )
    return items


def _suggested_links(topics: list[str]) -> list[LinkSuggestion]:
    links: list[LinkSuggestion] = []
    for topic in topics[:6]:
        url = TOPIC_LINKS.get(topic)
        if url is None:
            continue
        links.append(
            LinkSuggestion(
                topic=topic,
                reason="Found in your listening/thought stream; useful for deeper background.",
                url=url,
            )
        )
    return links


def _connected_projects(profile: InterestProfile, topics: list[str]) -> list[str]:
    topic_set = set(topics)
    matches: list[str] = []
    for project in profile.projects:
        project_words = set(" ".join(project.tags + [project.name.lower(), project.description.lower()]).split())
        if topic_set.intersection(project_words):
            matches.append(project.name)
    return matches


def analyze_session(
    session: SessionState,
    profile: InterestProfile,
    online_verification: bool,
) -> SessionInsight:
    full_text = _join_text(session)
    sentences = _extract_sentences(full_text)
    claims = _extract_claims(sentences)
    topics = _extract_topics(full_text)

    return SessionInsight(
        summary=_summary_from_sentences(sentences),
        explanation=_explanation_from_topics(topics),
        verification=_verification_items(claims, online_verification=online_verification),
        suggested_links=_suggested_links(topics),
        connected_projects=_connected_projects(profile, topics),
    )
