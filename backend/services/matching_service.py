"""matching_service.py — requirement <-> evidence matching + deterministic
scoring rollup.

The score is ALWAYS deterministic: requirement-strength * priority covers,
rolled up by category. An LLM is never asked to invent the number (guardrail
from the master plan). Output keeps requirement-level provenance so the
explanation layer can cite exact evidence.
"""
from collections import defaultdict
from . import skills as sk


# Category weights for the final breakdown (master plan formula B, adapted).
CATEGORY_WEIGHTS = {
    "skill": 0.35,
    "experience": 0.20,
    "coverage": 0.20,
    "education": 0.10,
    "domain": 0.10,
    "soft": 0.05,
}


def _evidence_terms(ev: dict) -> set[str]:
    return set(ev.get("skills", [])) | set(ev.get("soft", [])) | set(ev.get("domain", []))


def _required_terms(req: dict) -> set[str]:
    return set(req.get("skills", [])) | set(req.get("soft", [])) | set(req.get("domain", []))


def _reworded_flag(required: set[str], ev_terms: set[str]) -> bool:
    return bool(sk.find_reworded_links(required, ev_terms))


def match_resume_to_job(resume: dict, job: dict) -> dict:
    """Score one job against one resume, returning a full, explainable breakdown."""

    requirements = job["requirements"]
    matched_reqs: list[dict] = []
    cat_scores: dict[str, list[int]] = defaultdict(list)

    for req in requirements:
        required = _required_terms(req)
        req_low = req["text"].lower()
        req_years = req.get("years", 0)

        best_ev: dict | None = None
        best_strength = 0.0
        best_status = "missing"
        best_reworded = False
        best_reason = ""

        for ev in resume["evidence"]:
            ev_terms = _evidence_terms(ev)
            strength, status = 0.0, "missing"

            if required:
                overlap = len(required & ev_terms)
                if overlap >= len(required):
                    strength, status = 1.0, "matched"
                elif overlap > 0:
                    strength, status = overlap / len(required), "partial"
            else:
                # Requirement has no explicit skills — treat any domain/soft
                # overlap as a weak contextual match.
                if ev_terms:
                    strength, status = 0.5, "partial"

            reason = ""
            if req_years > 0 and ev.get("years", 0) >= req_years and strength >= 1.0:
                reason = f"meets the {req_years}+ years of experience requirement ({ev['years']}y shown)"

            if strength > best_strength:
                best_ev = ev
                best_strength = strength
                best_status = status
                best_reason = reason
                best_reworded = _reworded_flag(required, ev_terms) and status != "missing"

        # Seniority-only credit: requirement satisfied by years even with no skill overlap.
        if req_years > 0 and not best_ev and any(e.get("years", 0) >= req_years for e in resume["evidence"]):
            best_ev = max(resume["evidence"], key=lambda e: e.get("years", 0))
            best_strength = 0.6
            best_status = "partial"
            best_reason = f"{best_ev['years']} years of experience (meets {req_years}+) — duration shown, but skill evidence unclear"

        score = round(best_strength * 100)

        matched_reqs.append({
            "text": req["text"],
            "must_have": req["must_have"],
            "category": req["category"],
            "required_skills": sorted(required),
            "score": score,
            "status": best_status,
            "reworded": best_reworded,
            "evidence_text": (best_ev["text"] if best_ev else None),
            "reason": best_reason or (f"evidenced by: “{best_ev['text'][:140]}…”" if best_ev else None),
        })

        cat_scores[req["category"]].append(score)

    # ---- determinISTic rollup --------------------------------------------
    musts = [r for r in matched_reqs if r["must_have"]]
    nices = [r for r in matched_reqs if not r["must_have"]]
    must_met = sum(1 for r in musts if r["score"] >= 50)
    nice_met = sum(1 for r in nices if r["score"] >= 50)
    cov_score = round((must_met / len(musts)) * 100) if musts else 100

    sub_scores = {cat: round(sum(s) / len(s)) for cat, s in cat_scores.items()}
    sub_scores.setdefault("skill", 50)
    sub_scores.setdefault("experience", 50)
    sub_scores.setdefault("education", 50)
    sub_scores.setdefault("domain", 50)
    sub_scores.setdefault("soft", 50)

    weighted = (
        sub_scores["skill"] * CATEGORY_WEIGHTS["skill"]
        + sub_scores["experience"] * CATEGORY_WEIGHTS["experience"]
        + sub_scores["education"] * CATEGORY_WEIGHTS["education"]
        + sub_scores["domain"] * CATEGORY_WEIGHTS["domain"]
        + sub_scores["soft"] * CATEGORY_WEIGHTS["soft"]
        + cov_score * CATEGORY_WEIGHTS["coverage"]
    )
    score = round(min(100, max(0, weighted)))

    return {
        "score": score,
        "bucket": _bucket(score),
        "sub_scores": sub_scores,
        "coverage": {
            "must_met": must_met,
            "must_total": len(musts),
            "nice_met": nice_met,
            "nice_total": len(nices),
            "covered_score": cov_score,
        },
        "requirements": matched_reqs,
    }


def _bucket(score: int) -> str:
    if score >= 85:
        return "Excellent"
    if score >= 70:
        return "Strong"
    if score >= 55:
        return "Potential"
    return "Low"