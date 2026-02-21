# Architecture (MVP)

## Design principles

- Local-first for no-connectivity moments.
- Event-driven data model (listening/thought stream).
- Strict separation:
  - Local SLM analysis.
  - Online verification/retrieval.
- Project-aware memory to connect new ideas with existing goals.

## Components

1. Mobile client (future implementation)
   - Audio thought capture (speech-to-text on-device).
   - Playback metadata ingestion (YouTube/Spotify integrations).
   - Local queue when offline.
2. API service (this repo scaffold)
   - Profile/project/topic management.
   - Session event ingestion.
   - Insight generation orchestration.
3. Local analysis engine (stubbed)
   - Summarization/explanation/topic extraction.
4. Verification engine (stubbed)
   - Claim checking and source attachment when online.
5. Knowledge graph store (future)
   - Tracks entities, claims, projects, and links over time.

## Data model (MVP)

- `InterestProfile`
  - `projects[]`
  - `interests[]`
  - `questions[]`
- `SessionState`
  - `listening_events[]`
  - `thought_events[]`
  - `latest_insight`
- `SessionInsight`
  - `summary`
  - `explanation`
  - `verification[]`
  - `suggested_links[]`
  - `connected_projects[]`

## Offline/online behavior

- Offline:
  - Accept and store events.
  - Local insight generation.
  - Mark verification as `pending_online_check`.
- Online:
  - Run source retrieval and claim checks.
  - Update verification status and attach source URLs.

## Security/privacy considerations

- Keep raw audio local when possible.
- Store transcripts encrypted at rest in production.
- Require explicit permissions for microphone/media access.
- Make source attribution visible and auditable.
