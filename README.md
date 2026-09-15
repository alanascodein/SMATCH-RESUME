# SMACTH AI Resume-to-Job Matcher

## What was built

A working end-to-end **AI-Powered Resume-to-Job Matcher** with the full master-plan architecture compressed to its five load-bearing modules:

| Module | File | Role |
|---|---|---|
| resume_parser | `backend/services/resume_parser.py` | TXT / DOCX / PDF → plain text |
| resume_analyzer | `backend/services/resume_analyzer.py` | text → atomic evidence units (bullet-level, skill-tagged, quantified-impact, seniority) |
| jd_analyzer | `backend/services/jd_analyzer.py` | JD text → requirement units (must/nice, categorised, implied skills) |
| skill normalization | `backend/services/skills.py` | canonical skills + synonyms ("JS"/"ES6"/"TypeScript" → JavaScript) |
| matching_service | `backend/services/matching_service.py` | deterministic requirement↔evidence scoring rollup (no LLM invents the number) |
| explanation_service | `backend/services/explanation_service.py` | grounded, evidence-cited, reworded-match & gap flagging |
| API | `backend/main.py` | FastAPI endpoints |
| UI | `src/` | React + Vite frontend, dark-glass/lime UI |

## How to run

```bash
# 1. Backend
cd backend
pip install -r requirements.txt
python main.py                      # http://127.0.0.1:8000

# 2. Frontend (new terminal)
npm install
npm run dev                         # http://localhost:5173
```
Open `http://localhost:5173`, click the **Senior Backend Engineer — Payments Platform** sample (the optimal listing for `demo_resume.txt`, scores ~82 Strong), upload/paste

`backend/data/demo_resume.txt`, hit **Analyze & Rank**.

## API

| Method | Path | Body |
|---|---|---|
| GET | `/api/health` | — |
| GET | `/api/samples` | — |
| GET | `/api/samples/{id}` | — |
| POST | `/api/parse_resume` | multipart `file` (PDF/DOCX/TXT) → text + evidence units |
| POST | `/api/parse_job` | `{ title, text }` → requirement units |
| POST | `/api/match` | `{ resume_text, jobs: [{ id, title, text }] }` → ranked matches |

Example `/api/match` response shape:
```json
{
  "matches": [{
    "id": "cloud-js", "title": "...", "score": 49, "bucket": "Low",
    "sub_scores": {"skill": 61, "experience": 50, "education": 0, "domain": 0, "soft": 0},
    "coverage": {"must_met": 7, "must_total": 8, "nice_met": 1, "nice_total": 2, "covered_score": 88},
    "explanation": "…",
    "requirement_details": [{ "text": "…", "status": "matched", "reworded": false, "evidence_text": "…", "score": 100 }]
  }]
}
```

## How scoring works (deterministic)

score = Σ(sub_scoreᶜ × weightᶜ) where weights: skill .35, experience .20,
coverage .20, education .10, domain .10, soft .05.
Every requirement keeps `status` (matched/partial/missing), its citing
evidence bullet, and a `reworded` flag when it matched only through synonyms.

## Known limitations (stated plainly)

- **Matching weights are hardcoded**, not tuned against labelled data yet.
- **Job dataset is static/curated** — no live scraping (deliberate, per plan).
- **Skills dictionary is scoped** to software/product roles in the demo dataset;
  other domains need dictionary expansion.
- **PDF extraction fails on image-only (scanned) PDFs** — error is surfaced to the UI.
- **No embeddings yet** — retrieval is currently dictionary/synonym-based, not
  vector-based. Adding `sentence-transformers` + FAISS is the natural next step.
- **No auth/persistence** — every run is stateless.

## Recommended next features (prioritized)

1. Embedding retrieval (bge-small + FAISS) behind the current synonym layer as a recall stage
2. Cross-encoder/LLM rerank on the top-K pairs only (precision stage)
3. Curated labelled dataset + nDCG to put a number on ranking quality
4. Skill gap % estimate and "why not this job" view
5. Multi-resume comparison (recruiter mode)

## Judge-friendly demo flow

1. Load **Senior Backend Engineer — Payments Platform** sample (optimal listing) + `demo_resume.txt`
2. Run match → scores **82 Strong**, clearly highest of the 6 ranking
3. Expand the top card → show the evidence-linked requirement rows and the
   reworded-match flag ("containerised applications" ↔ "Docker")
4. Show the missing must-have gap (server-side JavaScript) as an honest negative