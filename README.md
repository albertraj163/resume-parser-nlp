# Resume Parser NLP

A web demo to extract structured fields from plain-text resumes using **regex** and **spaCy** named-entity recognition.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Flask](https://img.shields.io/badge/Flask-3.x-green)

## Features

- Professional web UI with drag-and-drop file upload
- Extracts **name**, **email**, **phone**, **skills**, **experience**, and **education**
- spaCy-powered **named entity** detection
- Supports `.txt` and `.pdf` uploads
- Built-in sample resume for quick testing

## Project Structure

```
resume-parser-nlp/
├── app.py              # Flask web server
├── resume_parser.py    # Parsing logic (regex + spaCy)
├── sample_resume.txt   # Example resume
├── requirements.txt
├── templates/
│   └── index.html
└── static/
    ├── css/style.css
    └── js/app.js
```

## Quick Start

```bash
# 1. Create virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\activate         # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Install spaCy English model for better NER
python -m spacy download en_core_web_sm

# 4. Run the web app
python app.py
```

Open your browser at **http://localhost:5000**

## CLI Usage

You can still use the parser directly from Python:

```python
from resume_parser import parse_resume

with open("sample_resume.txt") as f:
    result = parse_resume(f.read())

print(result)
```

## API Endpoints

| Method | Path          | Description                    |
|--------|---------------|--------------------------------|
| GET    | `/`           | Web UI                         |
| POST   | `/api/parse`  | Parse resume (text or file)    |
| GET    | `/api/sample` | Load and parse sample resume   |

### POST `/api/parse`

Send either form field `text` or upload a `file` (`.txt` / `.pdf`).

```bash
curl -X POST http://localhost:5000/api/parse \
  -F "text=Name: Jane Doe\nEmail: jane@example.com\nSkills: Python, SQL"
```

## License

MIT
