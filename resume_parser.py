"""Resume parser using regex and spaCy for named-entity extraction."""

import re
from typing import Any

import spacy

_nlp = None


def _get_nlp():
    global _nlp
    if _nlp is None:
        try:
            _nlp = spacy.load("en_core_web_sm")
        except OSError:
            _nlp = spacy.blank("en")
    return _nlp


def extract_email(text: str) -> str | None:
    match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
    return match.group(0) if match else None


def extract_phone(text: str) -> str | None:
    patterns = [
        r"\+?\d{1,3}[-.\s]?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}",
        r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0).strip()
    return None


def extract_name(text: str) -> str | None:
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    if not lines:
        return None

    first_line = lines[0]
    label_match = re.match(r"^name\s*:\s*(.+)$", first_line, re.IGNORECASE)
    if label_match:
        return label_match.group(1).strip()

    nlp = _get_nlp()
    doc = nlp(first_line)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text.strip()

    if len(first_line.split()) <= 4 and not re.search(r"[@\d]", first_line):
        return first_line

    return None


def extract_labeled_field(text: str, label: str) -> str | None:
    pattern = rf"^{re.escape(label)}\s*:\s*(.+)$"
    for line in text.splitlines():
        match = re.match(pattern, line.strip(), re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def extract_skills(text: str) -> list[str]:
    labeled = extract_labeled_field(text, "skills")
    source = labeled or text

    common_skills = {
        "python", "java", "javascript", "typescript", "sql", "react", "angular",
        "vue", "node.js", "nodejs", "docker", "kubernetes", "aws", "azure",
        "gcp", "machine learning", "deep learning", "nlp", "data science",
        "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "flask",
        "django", "fastapi", "git", "linux", "html", "css", "c++", "c#",
        "ruby", "go", "rust", "mongodb", "postgresql", "mysql", "redis",
        "spark", "hadoop", "tableau", "power bi", "excel", "agile", "scrum",
    }

    found: list[str] = []
    lower_source = source.lower()

    if labeled:
        parts = re.split(r"[,;|/•·]", labeled)
        for part in parts:
            skill = part.strip()
            if skill and len(skill) > 1:
                found.append(skill)
        return found

    for skill in sorted(common_skills, key=len, reverse=True):
        if skill in lower_source and skill.title() not in found:
            found.append(skill.title())

    return found[:20]


def extract_experience(text: str) -> list[str]:
    labeled = extract_labeled_field(text, "experience")
    if labeled:
        return [labeled]

    entries: list[str] = []
    in_section = False
    for line in text.splitlines():
        stripped = line.strip()
        if re.match(r"^experience\s*:?\s*$", stripped, re.IGNORECASE):
            in_section = True
            continue
        if in_section:
            if re.match(r"^[A-Z][a-zA-Z\s]+:?\s*$", stripped) and entries:
                break
            if stripped.startswith(("-", "•", "*")) or re.search(r"\d+\s*(year|yr|month)", stripped, re.I):
                entries.append(stripped.lstrip("-•* ").strip())

    return entries


def extract_education(text: str) -> list[str]:
    labeled = extract_labeled_field(text, "education")
    if labeled:
        return [labeled]

    entries: list[str] = []
    in_section = False
    for line in text.splitlines():
        stripped = line.strip()
        if re.match(r"^education\s*:?\s*$", stripped, re.IGNORECASE):
            in_section = True
            continue
        if in_section:
            if re.match(r"^[A-Z][a-zA-Z\s]+:?\s*$", stripped) and entries:
                break
            if stripped:
                entries.append(stripped.lstrip("-•* ").strip())

    degree_pattern = re.compile(
        r".*\b(B\.?S\.?|B\.?A\.?|M\.?S\.?|M\.?A\.?|Ph\.?D\.?|Bachelor|Master|Doctor)\b.*",
        re.IGNORECASE,
    )
    if not entries:
        entries = [line.strip() for line in text.splitlines() if degree_pattern.match(line.strip())]

    return entries


def extract_entities(text: str) -> list[dict[str, str]]:
    nlp = _get_nlp()
    doc = nlp(text)
    seen: set[tuple[str, str]] = set()
    entities: list[dict[str, str]] = []

    for ent in doc.ents:
        key = (ent.text.strip(), ent.label_)
        if key not in seen and ent.text.strip():
            seen.add(key)
            entities.append({"text": ent.text.strip(), "label": ent.label_})

    return entities


def parse_resume(text: str) -> dict[str, Any]:
    """Parse resume text and return structured fields."""
    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text),
        "experience": extract_experience(text),
        "education": extract_education(text),
        "entities": extract_entities(text),
        "raw_text": text,
    }
