"""resume_parser.py — convert PDF / DOCX / TXT uploads into plain text."""
import io
import re


def extract_text(filename: str, content: bytes) -> str:
    ext = (filename or "").lower().rsplit(".", 1)[-1]
    if ext == "pdf":
        return _from_pdf(content)
    if ext == "docx":
        return _from_docx(content)
    return _from_txt(content)


def _from_txt(content: bytes) -> str:
    for enc in ("utf-8", "latin-1", "cp1252"):
        try:
            return content.decode(enc)
        except UnicodeDecodeError:
            continue
    return content.decode("utf-8", errors="ignore")


def _from_pdf(content: bytes) -> str:
    try:
        import pdfplumber  # lazy import; app still works for TXT without it
    except ImportError as e:
        raise RuntimeError("pdfplumber is not installed — install backend/requirements.txt to parse PDFs.") from e
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        text = "\n".join((page.extract_text() or "") for page in pdf.pages)
    if not text.strip():
        raise RuntimeError("No text could be extracted — this PDF is likely image-based (scanned).")
    return _clean(text)


def _from_docx(content: bytes) -> str:
    try:
        import docx  # python-docx
    except ImportError as e:
        raise RuntimeError("python-docx is not installed — install backend/requirements.txt to parse DOCX files.") from e
    document = docx.Document(io.BytesIO(content))
    return _clean("\n".join(p.text for p in document.paragraphs))


def _clean(text: str) -> str:
    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in text.splitlines()]
    lines = [ln for ln in lines if ln]
    return "\n".join(lines)