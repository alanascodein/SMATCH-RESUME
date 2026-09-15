"""explanation_service.py — grounded, evidence-cited explanations.

Never LLM-invented: sentences are assembled deterministically from the exact
requirement <-> evidence pairs produced by the matching engine, so every claim
is falsifiable against the source text. Follows the master plan's prompt rules:
cite the specific bullet, flag reworded matches, and list gaps.
"""
from . import skills as sk


def _flagged_gaps(reqs: list[dict]) -> list[dict]:
    return [r for r in reqs if r["status"] in ("missing", "partial") and r["score"] < 50]


def _reworded_matches(reqs: list[dict]) -> list[dict]:
    return [r for r in reqs if r["reworded"]]


def generate_explanation(result: dict, job_title: str) -> str:
    score = result["score"]
    sub = result["sub_scores"]
    cov = result["coverage"]

    # ---- opening ---------------------------------------------------------
    opening = (
        f"{'Strong' if score >= 70 else 'Moderate' if score >= 55 else 'Low'} match for "
        f"“{job_title}” — {score}/100 ({result['bucket']})."
    )

    # ---- coverage --------------------------------------------------------
    coverage = f"Covers {cov['must_met']}/{cov['must_total']} must-haves and {cov['nice_met']}/{cov['nice_total']} nice-to-haves."

    # ---- strongest evidence (reworded flagged) ----------------------------
    reqs = result["requirements"]
    best_req = max(reqs, key=lambda r: r["score"]) if reqs else None
    evidence_point = ""
    if best_req and best_req["score"] >= 70 and best_req["evidence_text"]:
        ev = best_req["evidence_text"][:150]
        if best_req["reworded"]:
            evidence_point = (
                f"Your bullet “{ev}” directly evidences the JD's “{best_req['text'][:90]}” requirement — "
                "worded completely differently but the same underlying skill."
            )
        else:
            evidence_point = (
                f"Your bullet “{ev}” directly evidences the JD's “{best_req['text'][:90]}” requirement."
            )

    # ---- gaps -------------------------------------------------------------
    gaps = _flagged_gaps(reqs)
    gap_text = ""
    if gaps:
        names = "', '".join(g["text"][:60] for g in gaps[:3])
        extra = f" and {len(gaps) - 3} more" if len(gaps) > 3 else ""
        gap_text = f"Gap: no strong evidence found for '{names}'{extra}."

    parts = [s for s in [opening, coverage, evidence_point, gap_text] if s]
    return " ".join(parts)


def build_requirement_details(result: dict) -> list[dict]:
    """Expandable per-requirement rows for the UI: requirement text, skill
    overlap, the citing evidence bullet and a human label."""
    out = []
    reqs = result["requirements"]
    for r in reqs:
        label = "Must-have" if r["must_have"] else "Nice-to-have"
        if r["status"] == "matched":
            status_label = "Matched"
        elif r["status"] == "partial":
            status_label = "Partial"
        else:
            status_label = "Missing"
        if r["reworded"]:
            status_label = "Matched · different wording"
        out.append({
            "text": r["text"],
            "label": f"{label} · {status_label}",
            "score": r["score"],
            "must_have": r["must_have"],
            "skills": r["required_skills"],
            "evidence_text": r["evidence_text"],
            "reason": r["reason"],
            "status": r["status"],
            "reworded": r["reworded"],
        })
    # strongest first
    out.sort(key=lambda x: x["score"], reverse=True)
    return out