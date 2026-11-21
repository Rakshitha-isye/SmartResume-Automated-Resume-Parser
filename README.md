# SmartResume — Automated Resume Parser

A Flask web application that accepts PDF/DOCX resumes, extracts basic candidate information, stores profiles in a database, and supports candidate search.

## Features
- Upload PDF and DOCX resumes (8 MB maximum)
- Extract email, phone number, likely name, skills and education keywords
- Store candidate records and extracted text
- Dashboard and searchable candidate list
- Candidate detail page, source resume download and delete
- SQLite by default; PostgreSQL can be configured through `DATABASE_URL`

## Requirements
- Python 3.10 or newer recommended
- Windows, macOS or Linux

## Run locally (Windows PowerShell)

```powershell
cd SmartResume
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python -m spacy download en_core_web_sm
python app.py
```

Open http://127.0.0.1:5000

If PowerShell blocks activation, run `venv\Scripts\activate.bat` from Command Prompt, or use `venv\Scripts\python.exe app.py` after installing packages into the virtual environment.

## PostgreSQL configuration (optional)

Create a PostgreSQL database, then edit `.env`:

```env
SECRET_KEY=use-a-long-random-secret
DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/smartresume
```

Restart the app. Tables are created automatically on startup.

## Notes and limitations
- This starter version extracts text from text-based PDFs and DOCX files. Scanned/image-only PDFs need OCR, which is not included.
- Name, skills and education extraction use heuristics and may need manual correction. Resume formats vary.
- This is an educational internship project, not a production hiring or automated decision system.
- Do not upload real candidate personal data without permission. Store only data you are authorized to process.
- Before public deployment, set a strong secret key, use HTTPS, restrict access, configure persistent file storage and a production database, and add privacy/retention controls.
- Debug mode is disabled by default.
