# resume_parser.py
# Simple resume parser demo using regex and spaCy (for named entities)
import re
import spacy

DATA_PATH = "sample_resume.txt"

def extract_email(text):
    m = re.search(r'[\w\.-]+@[\w\.-]+', text)
    return m.group(0) if m else None

def main():
    text = open(DATA_PATH).read()
    email = extract_email(text)
    nlp = spacy.blank('en')
    doc = nlp(text)
    print("Extracted email:", email)
    print("\nRaw text:\n", text)

if __name__ == '__main__':
    main()
