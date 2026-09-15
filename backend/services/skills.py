"""Skill normalization layer: canonical skills, aliases/synonyms, category
classification and detection. This is the "skill normalization layer" from the
master plan — matching happens on canonical names, so "JS", "JavaScript" and
"ES6" all resolve to the same skill.
"""
import re

# ---------------------------------------------------------------------------
# Skill database: canonical skill -> set of aliases (synonyms / rewordings)
# ---------------------------------------------------------------------------
TECH_SKILLS: dict[str, set[str]] = {
    "Python": {"python", "django", "flask", "fastapi"},
    "JavaScript": {"javascript", "js", "es6", "typescript", "ts", "node", "nodejs", "node.js"},
    "React": {"react", "reactjs", "react.js"},
    "Vue": {"vue", "vuejs"},
    "Angular": {"angular", "angularjs"},
    "HTML/CSS": {"html", "css", "html5", "css3"},
    "SQL": {"sql", "postgres", "postgresql", "mysql", "sqlite", "rdbms"},
    "NoSQL": {"nosql", "mongodb", "mongo", "redis", "cassandra", "dynamodb"},
    "Java": {"java", "spring", "spring boot"},
    "C/C++": {"c++", "cpp", "c programming"},
    "C#": {"c#", "csharp", ".net", "dotnet"},
    "Go": {"golang", "go programming"},
    "Rust": {"rust programming"},
    "Ruby": {"ruby", "rails"},
    "PHP": {"php", "laravel"},
    "Swift": {"swift programming", "ios development"},
    "Kotlin": {"kotlin", "android development"},
    "DevOps": {"devops", "ci/cd", "continuous integration", "continuous deployment", "pipeline"},
    "Docker": {"docker", "containerization", "containers", "containerised", "containerized"},
    "Kubernetes": {"kubernetes", "k8s", "orchestration", "container orchestration"},
    "Cloud": {"aws", "amazon web services", "azure", "gcp", "google cloud", "cloud", "ec2", "s3", "lambda", "cloudformation", "terraform", "infrastructure as code"},
    "Machine Learning": {"machine learning", "ml", "deep learning", "neural networks", "nlp", "computer vision", "tensorflow", "pytorch", "keras", "scikit-learn"},
    "Data Science": {"data science", "pandas", "numpy", "data analysis", "statistical modeling", "statsmodels", "jupyter"},
    "Data Engineering": {"data engineering", "apache spark", "spark", "hadoop", "kafka", "airflow", "etl", "data pipelines", "data warehouse"},
    "Data Visualization": {"tableau", "power bi", "looker", "data visualization", "matplotlib", "seaborn", "d3"},
    "Git": {"git", "github", "gitlab", "version control", "bitbucket"},
    "REST APIs": {"rest", "rest api", "restful", "api design", "graphql", "grpc"},
    "Testing": {"testing", "unit test", "unit tests", "tdd", "pytest", "jest", "cypress", "selenium", "playwright", "test-driven"},
    "Microservices": {"microservices", "distributed systems", "event-driven", "event driven", "message queues", "message queue"},
    "System Design": {"system design", "architecture", "scalability", "high availability", "load balancing"},
    "Security": {"security", "cybersecurity", "encryption", "oauth", "authentication", "authorization", "penetration testing", "owasp"},
    "Agile": {"agile", "scrum", "kanban", "sprint", "jira"},
    "Linux": {"linux", "unix", "bash", "shell scripting", "shell"},
    "Figma": {"figma", "ui/ux", "ui design", "ux design", "user experience", "user interface"},
    "Excel": {"excel", "spreadsheet", "vba"},
    "Project Management": {"project management", "project manager", "roadmap", "stakeholder", "program management", "product management", "product manager"},
    "Communication": {"communication", "presentation skills", "public speaking", "presented", "presenting", "reporting"},
    "Leadership": {"leadership", "led", "lead", "leads", "leading", "mentor", "mentoring", "managed", "managing", "team management", "people management", "leadership skills"},
    "Teamwork": {"teamwork", "team", "collaboration", "collaborated", "cross-functional", "cross functional", "working with"},
    "Problem Solving": {"problem solving", "problem-solving", "critical thinking", "analytical", "troubleshooting", "debug", "debugging"},
    "Time Management": {"time management", "prioritization", "deadline-driven", "deadlines"},
    "Adaptability": {"adaptability", "fast-paced", "fast paced", "self-starter", "self motivated"},
    "Finance": {"finance", "financial", "fintech", "banking", "payments", "trading"},
    "Healthcare": {"healthcare", "health", "medical", "clinical", "medtech", "biotech"},
    "E-commerce": {"e-commerce", "ecommerce", "retail", "marketplace"},
    "Logistics": {"logistics", "supply chain", "warehousing", "fulfillment", "operations", "inventory"},
    "Data Analytics": {"data analytics", "data analysis", "analytics", "kpi", "kpis", "dashboards", "business intelligence", "a/b testing", "ab testing", "sql queries"},
}

# Synonyms that let different wording resolve to the same skill.
SYNONYMS: dict[str, set[str]] = {
    "JS": {"javascript", "typescript", "es6"},
    "containerization experts": {"docker", "kubernetes", "containers"},
    "cloud specialist": {"aws", "azure", "gcp"},
    "programming": {"python", "javascript", "java", "c++", "go"},
    "frontend": {"react", "vue", "angular", "html/css", "javascript"},
    "backend": {"python", "java", "node", "sql", "rest apis", "go"},
    "data expert": {"data science", "data engineering", "data analytics"},
}

DEGREE_PATTERNS = [
    r"bachelor", r"master", r"ph\.?d", r"mb[ba]", r"bachelor's?",
    r"master's?", r"b\.eng", r"bachelor of (science|arts|engineering)",
    r"graduate|undergraduate", r"degree in",
]

CATEGORY_KEYWORDS: dict[str, set[str]] = {
    "experience": {"years", "experience", "yrs", "seniority"},
    "domain": set(TECH_SKILLS.get("Finance", {}) | TECH_SKILLS.get("Healthcare", {}) | TECH_SKILLS.get("E-commerce", {}) | TECH_SKILLS.get("Logistics", {})),
    "soft": set(
        TECH_SKILLS.get("Communication", {})
        | TECH_SKILLS.get("Leadership", {})
        | TECH_SKILLS.get("Teamwork", {})
        | TECH_SKILLS.get("Problem Solving", {})
        | TECH_SKILLS.get("Time Management", {})
        | TECH_SKILLS.get("Adaptability", {})
    ),
}

MUST_HAVE_KEYWORDS = ["must", "required", "requirement", "require", "need", "expected",
                       "essential", "minimum qualification", "qualifications", "ability to", "should have"]
NICE_HAVE_KEYWORDS = ["nice to have", "nice-to-have", "preferred", "plus", "good to have",
                      "bonus", "familiarity with", "a plus"]

_YEAR_REGEX = re.compile(r"(\d{1,2})\+?\s*(?:years|yrs|year)", re.IGNORECASE)
_INDEXED_REGEX = re.compile(r"\d{2,}|\b\d+%\b")
_QUANTIFIED_REGEX = re.compile(r"(\d+%|\$\d+[kKmM]?|\d+\s*(?:users|customers|revenue|people))", re.IGNORECASE)
_BULLET_PREFIX = re.compile(r"^\s*(?:[-•*▪·]|\d+[.)])\s*")


def normalize_term(term: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", term.lower().strip())


def _word_set(text: str) -> set[str]:
    return set(normalize_term(t) for t in re.split(r"\W+", text) if t)


def detect_skills(text: str) -> set[str]:
    """Return canonical skills mentioned in text (word-boundary aware, handles plurals)."""
    found: set[str] = set()
    low = text.lower()
    for canonical, aliases in TECH_SKILLS.items():
        for alias in aliases:
            pattern = rf"(?<![a-z0-9]){re.escape(alias)}(?:s|es)?(?![a-z0-9])"
            if re.search(pattern, low):
                found.add(canonical)
                break
    return found


def detect_soft_skills(text: str) -> set[str]:
    found: set[str] = set()
    low = text.lower()
    for canonical in ["Communication", "Leadership", "Teamwork", "Problem Solving", "Time Management", "Adaptability"]:
        for alias in TECH_SKILLS[canonical]:
            if re.search(rf"(?<![a-z0-9]){re.escape(alias)}(?:s|es)?(?![a-z0-9])", low):
                found.add(canonical)
                break
    return found


def detect_domain(text: str) -> set[str]:
    found: set[str] = set()
    low = text.lower()
    for canonical in ["Finance", "Healthcare", "E-commerce", "Logistics"]:
        for alias in TECH_SKILLS[canonical]:
            if re.search(rf"(?<![a-z0-9]){re.escape(alias)}(?:s|es)?(?![a-z0-9])", low):
                found.add(canonical)
                break
    return found


def detect_education(text: str) -> bool:
    low = text.lower()
    return any(re.search(p, low) for p in DEGREE_PATTERNS)


def detect_years(text: str) -> int:
    m = _YEAR_REGEX.search(text.lower())
    return int(m.group(1)) if m else 0


def detect_quantified(text: str) -> bool:
    return bool(_QUANTIFIED_REGEX.search(text))


def category_of(unit_text: str, is_education: bool, has_years: bool) -> str:
    if is_education:
        return "education"
    if has_years and not detect_skills(unit_text):
        return "experience"
    if detect_soft_skills(unit_text):
        return "soft"
    if detect_domain(unit_text):
        return "domain"
    if detect_skills(unit_text):
        return "skill"
    return "experience" if has_years else "skill"


def find_reworded_links(require_skills: set[str], evidence_skills: set[str]) -> set[tuple[str, str]]:
    """Return (requirement_skill, evidence_skill) pairs that are the 'same skill,
    different wording' — i.e. they only match through a synonym cluster, not
    literally."""
    links: set[tuple[str, str]] = set()
    for r in require_skills:
        if r in evidence_skills:
            continue  # literal match, not reworded
        for e in evidence_skills:
            for cluster in SYNONYMS.values():
                if r in cluster and e in cluster:
                    links.add((r, e))
                    break
    return links