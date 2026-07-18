# PROJECT NIYAM

Personal discipline operating system for habits, IITM study tracking, health, weight, streaks, analytics, and CSV exports.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```

Open `http://127.0.0.1:5000`, create an account, and the system seeds all 31 requested habits. Data is stored locally in `niyam.db`.

## Deploy to Render

1. Push this folder to a private GitHub repository.
2. In Render, create a PostgreSQL database and a Python **Web Service** from that repository.
3. Use `pip install -r requirements.txt` as the build command and `gunicorn --bind 0.0.0.0:$PORT run:app` as the start command.
4. Set `NIYAM_SECRET_KEY` to a randomly generated secret, `FLASK_ENV` to `production`, and `DATABASE_URL` to the database's internal connection string. Set the health check path to `/health`.

The hosted application uses PostgreSQL when `DATABASE_URL` is present; your local application continues to use SQLite.

## Production notes

Set a strong `NIYAM_SECRET_KEY`, serve with a production WSGI server, and put the app behind HTTPS before exposing it publicly.
