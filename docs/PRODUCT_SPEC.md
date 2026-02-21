# Product Spec: Learning Partner

## Vision

Build a personal AI learning partner that listens with you, thinks with you, and helps you study better by combining:

- Media intake (YouTube/Spotify).
- Real-time voice thoughts.
- Project-aware knowledge organization.
- Claim checking with sources.
- Guided next-step exploration links.

## Primary user flows

1. Start a learning session while walking/commuting.
2. App captures currently playing content metadata + transcript chunks.
3. User speaks thoughts/questions in real time.
4. On-device SLM summarizes and explains ideas locally.
5. Claims are marked:
   - `pending_online_check` while offline.
   - `verified` / `disputed` / `uncertain` when online checks run.
6. App provides:
   - Session summary.
   - Explanation in simple terms.
   - Links to deeper sources/topics.
   - Cross-links to active projects/interests.

## Your current project domains (seed profile)

- Consumer behavior:
  - How household characteristics affect purchasing behavior.
  - Environmentally friendly decisions.
- Real estate:
  - Divergence studies.
- AI landscape:
  - Semiconductors, infrastructure bottlenecks, latest AI news.

## MVP requirements

- Profile + projects + interests + questions.
- Session timeline with listening events + thought events.
- Local analysis pipeline (summary, explanation, topic extraction).
- Basic claim extraction and verification status model.
- Suggested links for deeper study.
- Offline-first flow with queued online verification.

## Non-MVP (later)

- Full playback/audio capture implementation details per platform.
- Multi-user collaboration.
- Advanced citation ranking and trust scoring.
- Agentic autonomous study plan generation.

## Success metrics

- Daily active learning sessions.
- % of sessions with at least one actionable follow-up link saved.
- Verification turnaround time after reconnecting online.
- User-rated usefulness of summaries/explanations.
