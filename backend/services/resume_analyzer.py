"""resume_analyzer.py — raw resume text -> structured evidence units.

Each evidence unit is an atomic, evidence-bearing claim (one per bullet /
achievement) tagged with the skills it demonstrates, its implied skills, a
seniority signal and whether it contains a quantified impact. This is the
"decompose before comparing" step from the master plan.
"""
import re
from . import skills as sk

BulletPrefix = re.compile(r"^\s*(?:[-•*▪·]|\d+[.)])\s*")


def split_units(text: str) -> list[str]:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    units: list[str] = []
    current: list[str] = []
    for line in lines:
        if BulletPrefix.match(line) or line.isupper() and len(line) < 60:
            if current:
                units.append(" ".join(current))
                current = []
            current.append(line)
        elif current:
            current.append(line)
        else:
            current.append(line)
    if current:
        units.append(" ".join(current))
    return units


def analyze(text: str) -> dict:
    """Return { summary, evidence: [{text, skills, soft, domain, years, quantified}] }."""
    if not text.strip():
        raise ValueError("Resume text is empty.")

    summary_excerpt = text.strip()[:500]

    units: list[dict] = []
    seen: set[str] = set()
    for raw in split_units(text):
        unit_text = re.sub(r"\s+", " ", raw).strip()
        if len(unit_text) < 12 or unit_text.lower() in seen:
            continue
        seen.add(unit_text.lower())
        units.append({
            "text": unit_text,
            "skills": sorted(sk.detect_skills(unit_text)),
            "soft": sorted(sk.detect_soft_skills(unit_text)),
            "domain": sorted(sk.detect_domain(unit_text)),
            "years": sk.detect_years(unit_text),
            "quantified": sk.detect_quantified(unit_text),
        })

    # A global summary/header unit so header-level skills still count.
    summary_unit = {
        "text": summary_excerpt.replace("\n", " "),
        "skills": sorted(sk.detect_skills(summary_excerpt)),
        "soft": sorted(sk.detect_soft_skills(summary_excerpt)),
        "domain": sorted(sk.detect_domain(summary_excerpt)),
        "years": sk.detect_years(summary_excerpt),
        "quantified": False,
    }

    return {
        "summary": summary_excerpt,
        "evidence": [summary_unit] + units,
    }