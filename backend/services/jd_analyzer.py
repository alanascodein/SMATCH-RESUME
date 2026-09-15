"""jd_analyzer.py — raw job posting text -> structured requirement units.

Each requirement unit is { text, must_have, category, skills } where skills
include implied / reworded variants inferred from synonyms.
"""
import re
from . import skills as sk


def split_requirements(text: str) -> list[str]:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    reqs: list[str] = []
    current: list[str] = []
    header: str | None = None  # section header to prepend to next requirement
    for line in lines:
        # section headers (ending with ':') get prepended to the next requirement
        # so the analyzer can detect must-have vs nice-to-have context
        if line.endswith(":"):
            header = line
            if current:
                reqs.append(" ".join(current))
                current = []
            continue
        if sk._BULLET_PREFIX.match(line):
            if current:
                reqs.append(" ".join(current))
                current = []
            current.append((header + " " + line) if header else line)
            header = None
        # treat short phrasing lines as their own requirement
        elif len(line) < 120 and (reqs or current):
            if current:
                reqs.append(" ".join(current))
                current = []
            current.append((header + " " + line) if header else line)
            header = None
        elif current:
            current.append(line)
        else:
            current.append((header + " " + line) if header else line)
            header = None
    if current:
        reqs.append(" ".join(current))
    return reqs


def _is_must_have(text: str) -> bool:
    low = text.lower()
    if any(k in low for k in sk.NICE_HAVE_KEYWORDS):
        return False
    return any(k in low for k in sk.MUST_HAVE_KEYWORDS) or True  # default to must-have


def _is_required_match(low: str) -> bool:
    return any(k in low for k in sk.MUST_HAVE_KEYWORDS)


def _is_nice_match(low: str) -> bool:
    return any(k in low for k in sk.NICE_HAVE_KEYWORDS)


def analyze(text: str) -> list[dict]:
    if not text.strip():
        raise ValueError("Job posting text is empty.")

    reqs: list[dict] = []
    for raw in split_requirements(text):
        req_text = re.sub(r"\s+", " ", raw).strip()
        req_low = req_text.lower()
        if len(req_text) < 8:
            continue

        skills = sk.detect_skills(req_text)
        soft = sk.detect_soft_skills(req_text)
        domain = sk.detect_domain(req_text)

        is_nice = _is_nice_match(req_low)
        is_must = _is_must_have(req_text) and not is_nice
        category = sk.category_of(req_text, sk.detect_education(req_text), sk.detect_years(req_text) > 0)

        reqs.append({
            "text": req_text,
            "must_have": is_must,
            "category": category,
            "skills": sorted(skills) if skills else [],
            "soft": sorted(soft),
            "domain": sorted(domain),
            "years": sk.detect_years(req_text) or (1 if _is_required_match(req_low) and "years" in req_low else 0),
        })
    return reqs