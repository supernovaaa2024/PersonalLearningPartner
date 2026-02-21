# Implementation Plan

## Phase 1: Foundation (this scaffold)

- Define domain models and API contracts.
- Build session ingestion endpoints for listening + thoughts.
- Produce basic insights and link suggestions.
- Seed with your known projects/interests.

## Phase 2: Mobile + Offline

- Build React Native/Flutter client.
- Add on-device speech-to-text.
- Add local queue (SQLite on device) for no-Wi-Fi periods.
- Sync queued events when online.

## Phase 3: Integrations

- YouTube:
  - ingest watch metadata and transcript if available through allowed APIs.
- Spotify:
  - ingest currently playing metadata and episode info through official APIs.
- Normalize content entities across platforms.

## Phase 4: Verification and Source Quality

- Add retrieval pipeline (news, papers, trusted references).
- Add claim-verification classifier and confidence score.
- Persist citations with claim snapshots and timestamps.

## Phase 5: Knowledge Graph + Study Coach

- Connect sessions, projects, and concepts over time.
- Generate project-aware study briefs and weekly learning plans.
- Add "connect-the-dots" graph view across your domains.
