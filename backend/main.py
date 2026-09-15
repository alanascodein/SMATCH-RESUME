"""Resume-to-Job Matcher — API entry point.

Endpoints
---------
GET  /api/health
GET  /api/samples                   curated demo job postings
POST /api/parse_resume              multipart PDF/DOCX/TXT -> text + evidence units
POST /api/parse_job                 text -> requirement units
POST /api/match                     resume + jobs -> ranked matches with explanations
"""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from services import resume_parser, resume_analyzer, jd_analyzer
from services import matching_service, explanation_service
from data.sample_jobs import SAMPLE_JOBS

app = FastAPI(title="Resume-to-Job Matcher", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------------------------------
# Schemas
# --------------------------------------------------------------------------
class JobIn(BaseModel):
    id: str
    title: str
    text: str


class JobParseIn(BaseModel):
    title: str = "Untitled posting"
    text: str


class MatchIn(BaseModel):
    resume_text: str
    resume_name: str = "My Resume"
    jobs: list[JobIn]


# --------------------------------------------------------------------------
# Routes
# --------------------------------------------------------------------------
@app.get("/api/health")
def health():
    return {"status": "ok", "service": "resume-job-matcher"}


@app.get("/api/samples")
def samples():
    return [{"id": j["id"], "title": j["title"]} for j in SAMPLE_JOBS]


@app.get("/api/samples/{job_id}")
def sample_job(job_id: str):
    for j in SAMPLE_JOBS:
        if j["id"] == job_id:
            return {"id": j["id"], "title": j["title"], "text": j["text"]}
    raise HTTPException(status_code=404, detail="Unknown sample job id")


def _resume_analysis(text: str) -> dict:
    return resume_analyzer.analyze(text)


@app.post("/api/parse_resume")
async def parse_resume(file: UploadFile = File(...)):
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file uploaded")
    try:
        text = resume_parser.extract_text(file.filename or "resume.txt", content)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    analysis = _resume_analysis(text)
    return {
        "filename": file.filename,
        "text": text,
        "summary": analysis["summary"],
        "evidence": analysis["evidence"],
        "evidence_count": len(analysis["evidence"]),
    }


@app.post("/api/parse_job")
def parse_job(body: JobParseIn):
    try:
        return {"title": body.title, "requirements": jd_analyzer.analyze(body.text)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/match")
def match(body: MatchIn):
    try:
        resume = _resume_analysis(body.resume_text)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Resume: {e}")

    matches = []
    for job in body.jobs:
        try:
            requirements = jd_analyzer.analyze(job.text)
        except ValueError:
            continue
        j = {"id": job.id, "title": job.title, "requirements": requirements}
        result = matching_service.match_resume_to_job(resume, j)
        result["id"] = job.id
        result["title"] = job.title
        result["requirement_details"] = explanation_service.build_requirement_details(result)
        result["explanation"] = explanation_service.generate_explanation(result, job.title)
        matches.append(result)

    matches.sort(key=lambda m: m["score"], reverse=True)
    return {
        "resume_name": body.resume_name,
        "evidence_count": len(resume["evidence"]),
        "matches": matches,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)