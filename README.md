# SkillSync AI

**An Intelligent Platform for Skill Gap Analysis and Personalized Learning**

Final-year B.Tech major project. SkillSync AI analyzes a student's resume, compares their skills against current industry demand (sourced from live job postings), identifies gaps, and generates a personalized 8-week learning roadmap with curated resource recommendations.

---

## Project Status

Being built incrementally, sprint by sprint, following Agile. Current status: **Sprint 0 — Backend Foundation** (in progress).

Sprint 0 delivers a runnable backend skeleton: project structure, configuration, database models, and a health-check endpoint. **No business logic (auth, resume parsing, skill extraction, job collection, recommendations) is implemented yet** — that begins in Sprint 1 onward.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Database | SQLite, SQLAlchemy, Flask-Migrate (Alembic) |
| Frontend | React.js *(separate app, not in this repo)* |
| AI / ML | spaCy, Sentence Transformers, scikit-learn, pandas, numpy *(added in later sprints)* |
| Job Data | Apify API *(added in a later sprint, behind a provider abstraction)* |

---

## Project Structure

```
skillsync-ai-backend/
├── app/
│   ├── __init__.py          # Application factory
│   ├── config.py            # Environment-based configuration classes
│   ├── extensions.py        # Unbound Flask extension instances (db, migrate, cors)
│   ├── models/               # SQLAlchemy models (9 tables — see Database Schema)
│   ├── routes/                # Flask blueprints
│   ├── services/              # Business logic (empty — Sprint 1+)
│   ├── repositories/          # Data access layer (empty — Sprint 1+)
│   ├── ai/                    # NLP / matching logic (empty — later sprints)
│   ├── utils/                  # Shared helpers (API response format, error handlers, logging)
│   └── seeds/                  # Database seed scripts
├── migrations/                 # Alembic migration history
├── logs/                        # Runtime log output (gitignored, dir tracked via .gitkeep)
├── tests/                        # Test suite (empty — later sprint)
├── .env.example                   # Template for required environment variables
├── requirements.txt
└── run.py                          # Development server entry point
```

---

## Database Schema

Nine normalized tables: `users`, `resumes`, `skills`, `jobs`, `resume_skills`, `job_skills`, `recommendations`, `analyses`, `learning_roadmaps`. Full column-level design (purpose, types, keys, indexes) is documented as docstrings in each file under `app/models/`.

---

## Local Setup

### Prerequisites
- Python 3.11+
- pip

### Steps

1. **Clone the repository and enter the project folder:**
   ```bash
   git clone <repo-url>
   cd skillsync-ai-backend
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate      # macOS/Linux
   venv\Scripts\activate         # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` if you need non-default values (e.g. a different `SECRET_KEY`). Local defaults work out of the box for development.

5. **Apply database migrations** *(once the initial migration is generated later in Sprint 0)*:
   ```bash
   flask db upgrade
   ```

6. **Run the development server:**
   ```bash
   python run.py
   ```

7. **Verify it's running:**
   ```bash
   curl http://localhost:5000/api/health
   ```
   Expected response:
   ```json
   {
     "success": true,
     "data": {
       "status": "healthy",
       "project": "SkillSync AI Backend",
       "version": "1.0.0"
     },
     "message": "Request successful"
   }
   ```

---

## Development Notes

- **Application Factory pattern**: the app is created via `create_app(env_name)` in `app/__init__.py`, not as a bare module-level object — this supports different configs for development/testing/production.
- **Layered architecture**: routes → services → repositories → models, with `ai/` and `utils/` as supporting packages. No business logic belongs in routes or models.
- **Standardized API responses**: every endpoint returns `{"success": bool, "data"/"errors": ..., "message": str}` via `app/utils/api_response.py`.
- **Scope constraints**: this project deliberately avoids microservices, Docker/Kubernetes, message queues, OAuth, and cloud infrastructure — it's designed to run as a single Flask app suitable for an academic project.

---

## License

Academic project — final-year B.Tech coursework.
