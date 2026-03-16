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

TOPIC_ALIASES: dict[str, str] = {
    "consumer behaviour": "consumer behavior",
    "green purchasing": "sustainability",
    "green purchase": "sustainability",
    "households": "household",
    "housing": "real estate",
    "property": "real estate",
    "chip": "semiconductor",
    "chips": "semiconductor",
    "semiconductors": "semiconductor",
    "compute bottleneck": "bottleneck",
    "inference demand": "inference",
    "ai infra": "ai infrastructure",
    "power delivery": "ai infrastructure",
    "packaging": "semiconductor",
}

SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
CLAIM_HINTS = (" is ", " are ", " causes ", " will ", " leads to ", " reduces ", " increases ")
QUESTION_HINTS = ("?", "how ", "why ", "could ", "should ", "what if ")


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


def _canonicalize_topic(topic: str) -> str:
    normalized = " ".join(topic.lower().strip().split())
    return TOPIC_ALIASES.get(normalized, normalized)


def _dedupe_keep_order(items: list[str]) -> list[str]:
    # Keep stable order and uniqueness.
    seen: set[str] = set()
    unique_items: list[str] = []
    for topic in items:
        if topic not in seen:
            unique_items.append(topic)
            seen.add(topic)
    return unique_items


def _extract_topics(session: SessionState, profile: InterestProfile, text: str) -> list[str]:
    lowered = text.lower()
    topics: list[str] = []

    for event in session.listening_events:
        topics.extend(_canonicalize_topic(topic) for topic in event.topics)

    for explicit_topic in list(TOPIC_LINKS.keys()) + list(TOPIC_ALIASES.keys()):
        if explicit_topic in lowered:
            topics.append(_canonicalize_topic(explicit_topic))

    for interest in profile.interests:
        canonical_interest = _canonicalize_topic(interest)
        if canonical_interest in lowered or interest.lower() in lowered:
            topics.append(canonical_interest)

    for question in profile.questions:
        normalized_question = question.lower()
        for explicit_topic in list(TOPIC_LINKS.keys()) + list(TOPIC_ALIASES.keys()):
            if explicit_topic in normalized_question and explicit_topic in lowered:
                topics.append(_canonicalize_topic(explicit_topic))

    return _dedupe_keep_order(topics)


def _summary_from_session(session: SessionState, topics: list[str], sentences: list[str]) -> str:
    if not sentences:
        return "No content captured yet."
    titles = [event.title for event in session.listening_events[:2]]
    title_fragment = ", ".join(titles) if titles else "your latest audio"
    if topics:
        return (
            f"This session captured ideas from {title_fragment} and centered on "
            f"{', '.join(topics[:4])}. {sentences[0]}"
        )
    return f"This session captured ideas from {title_fragment}. {sentences[0]}"


def _explanation_from_topics(topics: list[str], connected_projects: list[str], online_verification: bool) -> str:
    if not topics:
        return (
            "The session discussed mixed ideas. Add a few explicit keywords in your thoughts "
            "to improve topic linking and deeper guidance."
        )
    mode_note = (
        "Claims are currently marked with placeholder checks because this demo is still using "
        "local heuristics instead of a live retrieval pipeline."
        if online_verification
        else "Because the session is in offline-first mode, claims are queued for source checks later."
    )
    explanation = "This session connects to " + ", ".join(topics[:5]) + ". "
    if connected_projects:
        explanation += "It lines up with " + ", ".join(connected_projects[:3]) + ". "
    explanation += (
        "A useful next step is to move from broad media takeaways into one testable question "
        "for each project. "
        + mode_note
    )
    return explanation


def _feedback_from_thoughts(session: SessionState, topics: list[str]) -> str:
    if not session.thought_events:
        return (
            "Record a voice note while listening so the app can compare your interpretation "
            "against the source material."
        )

    questioning = any(
        any(hint in thought.transcript_chunk.lower() for hint in QUESTION_HINTS)
        for thought in session.thought_events
    )
    average_confidence = sum(thought.confidence for thought in session.thought_events) / len(session.thought_events)
    confidence_note = "high conviction" if average_confidence >= 0.8 else "tentative framing"
    if questioning and topics:
        return (
            f"Your thoughts already contain researchable questions with {confidence_note}. "
            f"Turn the next note on {topics[0]} into a hypothesis, variable, and source to verify."
        )
    if topics:
        return (
            f"Your notes are mostly observational with {confidence_note}. Add one explicit 'why' "
            f"or 'how would I test this' question about {topics[0]} to deepen the session."
        )
    return (
        f"Your notes are coherent but still broad, with {confidence_note}. Add a sharper topic "
        "label or a falsifiable question to improve project matching."
    )


def _source_url_for_text(text: str) -> str | None:
    for topic, url in TOPIC_LINKS.items():
        if topic in text:
            return url
    for alias, canonical_topic in TOPIC_ALIASES.items():
        if alias in text and canonical_topic in TOPIC_LINKS:
            return TOPIC_LINKS[canonical_topic]
    return None


def _verification_items(claims: list[str], online_verification: bool) -> list[VerificationItem]:
    items: list[VerificationItem] = []
    for claim in claims:
        lowered_claim = claim.lower()
        source_url = _source_url_for_text(lowered_claim)
        if online_verification:
            items.append(
                VerificationItem(
                    claim=claim,
                    status=VerificationStatus.UNCERTAIN,
                    note="Matched to a topic source, but still needs real source-backed verification.",
                    source_url=source_url,
                )
            )
        else:
            items.append(
                VerificationItem(
                    claim=claim,
                    status=VerificationStatus.PENDING_ONLINE_CHECK,
                    note="Offline mode: queued for online verification.",
                    source_url=source_url,
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
        project_terms = [
            _canonicalize_topic(term)
            for term in project.tags + [project.name.lower(), project.description.lower()]
        ]
        if topic_set.intersection(project_terms):
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
    topics = _extract_topics(session, profile, full_text)
    connected_projects = _connected_projects(profile, topics)

    return SessionInsight(
        summary=_summary_from_session(session, topics, sentences),
        explanation=_explanation_from_topics(
            topics,
            connected_projects=connected_projects,
            online_verification=online_verification,
        ),
        feedback=_feedback_from_thoughts(session, topics),
        verification=_verification_items(claims, online_verification=online_verification),
        suggested_links=_suggested_links(topics),
        connected_projects=connected_projects,
    )
