# FixMyCampus

FixMyCampus is a simple campus issue-reporting application. Students report physical problems such as broken lights, leaks, damaged furniture, and cleanliness issues. Reports represent individual submissions; incidents represent the real-world problems those reports describe.

The main technical feature is deterministic incident deduplication. Similar reports are scored using explainable rules rather than AI or LLMs.

## Screenshots and demo views

The application includes these views for a demo or presentation:

- Landing page: `/`
- Student report form: `/report`
- Public incident dashboard: `/incidents`
- Incident detail with reports and photo evidence: `/incidents/<id>`
- Maintenance dashboard: `/admin/incidents`
- Analytics dashboard: `/analytics`

Run the application locally and capture screenshots from these routes when preparing a presentation.

## Architecture

```text
Browser
   |
   v
Flask routes
   |
   +----------> Report service
   |                  |
   |                  v
   |           Duplicate detector
   |                  |
   +----------> Admin and analytics services
                      |
                      v
                 Repositories
                      |
                      v
                    SQLite
```

Routes handle HTTP concerns. Services contain validation, duplicate scoring, priority calculation, workflow transitions, demo data, and analytics. Repositories contain SQLite access.

## Technology stack

- Python 3
- Flask
- SQLite
- HTML5 and CSS3
- Vanilla JavaScript
- pytest

No frontend framework, AI API, embedding model, or external analytics framework is required.

## Local setup

```text
python -m venv .venv
.venv\\Scripts\\activate
python -m pip install -r requirements.txt
```

Initialize the database:

```text
flask --app run.py init-db
```

Start the development server:

```text
python run.py
```

Open `http://127.0.0.1:5000/`.

## Demo data

After initializing the database, seed five realistic incidents and their reports:

```text
flask --app run.py seed-demo
```

The command is idempotent. Running it again does not create duplicate demo incidents. The streetlight example intentionally contains three different reports attached to one incident so the deduplication concept can be demonstrated.

## Running tests

```text
pytest
```

The suite covers repository relationships, validation, duplicate scoring and confirmation, structured locations, priority scoring, status transitions, uploads, analytics, demo data, accessibility-related page behavior, and security edge cases.

## Duplicate-detection algorithm

When a new report is submitted, the system compares it with existing `OPEN` incidents. It calculates four independent scores:

| Signal | Maximum |
| --- | ---: |
| Category match | 30 |
| Structured location match | 30 |
| Text token similarity | 25 |
| Time proximity | 15 |
| Total | 100 |

Text is lowercased, punctuation is removed, a small stop-word list is ignored, and token sets are compared using Jaccard similarity:

```text
intersection(tokens_a, tokens_b)
---------------------------------
union(tokens_a, tokens_b)
```

Time scores are 15 points for less than one hour, 12 for less than six hours, 8 for less than 24 hours, 4 for less than 72 hours, and 0 afterwards. A score of 70 or higher produces a possible-match confirmation. The user must confirm the match; the system never merges automatically.

## Database structure

```text
locations
  id, campus, building, floor, area

incidents
  id, title, category, location, location_id, status, priority,
  created_at, updated_at, transition timestamps

reports
  id, incident_id, description, category, location,
  location_id, location_detail, photo_filename, created_at
```

An incident can have many reports. A report may temporarily have no incident while duplicate matching is awaiting user confirmation.

## Priority system

Priority is explainable rather than objectively perfect. Its score combines report count, category severity, and unresolved age. The result is classified as `LOW`, `MEDIUM`, or `HIGH`, and is recalculated when reports are attached.

## Security and reliability notes

- SQL uses parameterized queries.
- Jinja auto-escaping protects rendered user text.
- Uploads use size limits, image signatures, generated filenames, and a controlled serving directory.
- Production requires `FIXMYCAMPUS_SECRET_KEY`.
- Debug mode is opt-in with `FIXMYCAMPUS_DEBUG=1`.
- The initial admin area is intentionally unauthenticated and is suitable only for this prototype.

## Deployment preparation

The application exposes a WSGI entry point in `wsgi.py` and a health check at `/health`.

On a Linux host or platform with persistent storage:

```text
pip install -r requirements.txt
export FIXMYCAMPUS_ENV=production
export FIXMYCAMPUS_SECRET_KEY="use-a-long-random-secret"
export FIXMYCAMPUS_DATABASE="/persistent-data/fixmycampus.sqlite"
export FIXMYCAMPUS_UPLOAD_FOLDER="/persistent-data/uploads"
flask --app wsgi.py init-db
gunicorn --bind 0.0.0.0:${PORT:-8000} wsgi:app
```

The SQLite database and upload directory must be mounted on persistent storage. An ephemeral filesystem will lose incidents and photo evidence when the service restarts. Flask serves the versioned static assets, while the WSGI server handles application requests.

Before publishing, verify `/`, `/health`, `/report`, `/incidents`, `/admin/incidents`, `/analytics`, duplicate confirmation, and photo evidence. No live application URL is included because deployment depends on the chosen hosting provider and persistent-volume configuration.

## Limitations and future improvements

Current limitations include free-text fallback for legacy locations, simple token similarity, no authentication or role system, SQLite as the database, and no background processing. Future work could add secure authentication, richer location matching, audit logs, notifications, production deployment, stronger image handling, and more advanced analytics.

The project deliberately uses deterministic logic first so its important behavior remains easy to inspect, test, and explain.
