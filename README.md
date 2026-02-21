# Learning Partner (Local-First)

This project is a starter implementation for a personal learning partner app that:

- Tracks what you listen to on YouTube and Spotify.
- Captures your spoken thoughts in real time.
- Summarizes and explains ideas as you learn.
- Flags claims for verification and attaches sources.
- Suggests links/topics to study next.
- Connects learning to your active projects and interests.

## Why this is local-first

You mentioned walking/train use (PATH NJ, often no Wi-Fi). The architecture supports:

- On-device transcription and lightweight analysis (SLM path).
- Offline session buffering.
- Deferred online fact checking/source retrieval once connected.

## Important integration constraints

- Spotify and YouTube terms/APIs usually allow metadata and approved transcript workflows, not unrestricted raw audio scraping.
- Real-time source-backed verification requires internet; offline mode marks claims as pending verification.

## MVP scope in this repo

- Backend API scaffold with in-memory storage.
- Core data models for profile, projects, listening events, thoughts, and insights.
- Basic analysis pipeline with:
  - Summary/explanation generation
  - Claim extraction (heuristic)
  - Verification placeholders
  - Topic link suggestions
  - Project-topic connection hints

## Quick start

1. Create a Python 3.11+ environment.
2. Install dependencies:

```bash
cd /Users/owenhuang/Documents/New\ project/backend
pip install -e .
```

3. Run API:

```bash
uvicorn app.main:app --reload
```

4. Open docs:

- http://127.0.0.1:8000/docs

## Repo structure

- `/Users/owenhuang/Documents/New project/docs/PRODUCT_SPEC.md`
- `/Users/owenhuang/Documents/New project/docs/ARCHITECTURE.md`
- `/Users/owenhuang/Documents/New project/backend/app/main.py`
- `/Users/owenhuang/Documents/New project/backend/app/models.py`
- `/Users/owenhuang/Documents/New project/backend/app/services/analyzer.py`

## Next steps after scaffold

1. Add persistent storage (SQLite/Postgres).
2. Integrate mobile client for on-device transcription + offline queue.
3. Implement real verifier with web sources when online.
4. Add graph memory to connect ideas across sessions/projects.
