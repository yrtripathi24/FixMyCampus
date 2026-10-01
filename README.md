# FixMyCampus

FixMyCampus is a Flask application for reporting and managing physical problems around a college campus. Its core feature will be deterministic incident deduplication: multiple reports about the same real-world problem can be recognized and grouped without AI or LLMs.

## Current checkpoint: database and core data model

The project contains the Flask application factory, a basic landing page, and SQLite persistence for incidents and reports. Reporting workflows and duplicate detection will be added in later checkpoints.

Initialize the development database with:

```text
flask --app run.py init-db
```

## Local setup

```text
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
python run.py
```

Then open `http://127.0.0.1:5000/`.

Run the tests with:

```text
pytest
```

## Technology

- Python and Flask
- HTML, CSS, and vanilla JavaScript
- SQLite (planned)
- pytest
