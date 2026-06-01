"""Flask web application for the Resume Parser NLP demo."""

import os
from pathlib import Path

from flask import Flask, jsonify, render_template, request

from resume_parser import parse_resume

BASE_DIR = Path(__file__).resolve().parent
SAMPLE_RESUME = BASE_DIR / "sample_resume.txt"

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # 2 MB


def _read_upload(file_storage) -> str:
    filename = (file_storage.filename or "").lower()
    raw = file_storage.read()

    if filename.endswith(".pdf"):
        try:
            from pypdf import PdfReader
            import io

            reader = PdfReader(io.BytesIO(raw))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception as exc:
            raise ValueError(f"Could not read PDF: {exc}") from exc

    for encoding in ("utf-8", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue

    raise ValueError("Unsupported file encoding. Please upload a UTF-8 text file.")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/parse", methods=["POST"])
def api_parse():
    text = request.form.get("text", "").strip()

    if "file" in request.files and request.files["file"].filename:
        try:
            text = _read_upload(request.files["file"])
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

    if not text:
        return jsonify({"error": "Please paste resume text or upload a file."}), 400

    try:
        result = parse_resume(text)
        return jsonify(result)
    except Exception as exc:
        return jsonify({"error": f"Parsing failed: {exc}"}), 500


@app.route("/api/sample")
def api_sample():
    if not SAMPLE_RESUME.exists():
        return jsonify({"error": "Sample resume not found."}), 404
    text = SAMPLE_RESUME.read_text(encoding="utf-8")
    return jsonify({"text": text, "result": parse_resume(text)})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
