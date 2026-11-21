
import re
from pathlib import Path

SKILL_TERMS = [
    "Python", "Java", "JavaScript", "TypeScript",
    "C++", "C#", "HTML", "CSS", "Flask", "Django",
    "FastAPI", "React", "Node.js", "SQL", "SQLite",
    "PostgreSQL", "MySQL", "MongoDB", "Git", "GitHub",
    "Machine Learning", "Deep Learning", "NLP",
    "Natural Language Processing", "Pandas", "NumPy",
    "scikit-learn", "TensorFlow", "Keras", "PyTorch",
    "Data Structures", "Algorithms", "REST API",
    "Docker", "AWS", "Excel", "Arduino IDE"
]

EDUCATION_TERMS = [
    "Ph.D", "Doctorate", "Master of", "M.Tech",
    "M.E.", "MCA", "MBA", "B.Tech", "B.E.",
    "B.Sc", "BCA", "Bachelor of", "Intermediate",
    "12th", "HSC", "Diploma", "SSC", "10th",
    "High School"
]


def extract_text(path: Path) -> str:
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        import pdfplumber

        chunks = []
        with pdfplumber.open(str(path)) as pdf:
            for page in pdf.pages:
                chunks.append(page.extract_text() or "")

        return "\n".join(chunks)

    if suffix == ".docx":
        from docx import Document

        doc = Document(str(path))
        chunks = [p.text for p in doc.paragraphs if p.text.strip()]

        for table in doc.tables:
            for row in table.rows:
                chunks.append(" | ".join(cell.text for cell in row.cells))

        return "\n".join(chunks)

    raise ValueError("Unsupported file type. Please upload PDF or DOCX.")


def extract_name(text: str) -> str:
    ignored = {
        "resume", "curriculum vitae", "profile summary",
        "professional summary", "contact", "personal details"
    }

    for line in text.splitlines()[:15]:
        line = re.sub(r"\s+", " ", line).strip(" |-\t")

        # Use the first clean line, before contact/location details.
        line = re.split(r"\s+[—–|]\s+", line)[0].strip()

        if (
            2 <= len(line) <= 45
            and 2 <= len(line.split()) <= 4
            and re.fullmatch(r"[A-Za-z]+(?:[ '-][A-Za-z]+)*", line)
            and line.lower() not in ignored
        ):
            return line

    return ""

def extract_skills(text: str) -> list:
    # Split joined words such as DataStructures into Data Structures.
    normalized = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", text)
    normalized = re.sub(r"\s+", " ", normalized)

    lower = normalized.lower()
    found_skills = []

    for skill in SKILL_TERMS:
        if skill == "C":
            continue

        pattern = (
            r"(?<![a-z0-9])"
            + re.escape(skill.lower())
            + r"(?![a-z0-9])"
        )

        if re.search(pattern, lower):
            found_skills.append(skill)

    # Handle C in phrases like "BasicCandPython".
    if re.search(r"basic\s*c(?:and)?\s*python", lower):
        found_skills.append("C")

    return found_skills

def parse_resume(path: Path) -> dict:
    text = extract_text(path)

    if not text.strip():
        raise ValueError(
            "No selectable text found. This may be a scanned PDF; "
            "OCR is not included in this version."
        )

    email_match = re.search(
        r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
        text,
        re.I
    )

    phone_match = re.search(
        r"(?<!\w)(?:\+?\d{1,3}[\s.-]?)?"
        r"(?:\(\d{3,5}\)[\s.-]?)?\d{5,10}(?!\w)",
        text
    )

    education = []
    normalized = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", text)
    lower = normalized.lower()

    for term in EDUCATION_TERMS:
        if term == "B.Tech":
            if re.search(r"(?<![a-z0-9])b\.?\s*tech(?=in|[^a-z0-9]|$)", lower):
                education.append(term)
            continue

        pattern = (
            r"(?<![a-z0-9])"
            + re.escape(term.lower())
            + r"(?![a-z0-9])"
        )

        if re.search(pattern, lower):
            education.append(term)

    return {
        "name": extract_name(text),
        "email": email_match.group(0) if email_match else "",
        "phone": phone_match.group(0).strip() if phone_match else "",
        "skills": extract_skills(text),
        "education": education,
        "text": text
    }
