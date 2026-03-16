# Learning Partner (Local-First)

I want ot create an app that can record what i listen to in youtube and spotify and then checks fi the information is correct, summarize and explain the information, and provide links to specifc topcis mentioned that I could explore further, andalso record my thoughts via voice in real time and provide feedback and collect links and websources which i could then go on to study further later. I love listening to podcasts while I am walking and on the train (PATH NJ, no wifi), so there should be an LLM that analyzes what I am learning (listening) and thinking in real time, locally on the device SLM. Also I want to to know my current projects and interests - for example i should be able to add my projects on consumer behavior and how household characteristic affect their purchasing and behavior and environemntally friendly decisions. also i wanna add my real estate project studying .divergence. also i want it to track AI semis landscpa eAI infra bottlenecks and laests AI news and connect the dots between everything that i am thiknnig and leanring. Bascially, I should add topics of interest and questions that I am curious about and study it with me( listen to podcasts and videos that I am listening to and think along with me while double chekcing the information - make sure they are correct and provide sources so i could dive deeper) - basically a learning partner.


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
