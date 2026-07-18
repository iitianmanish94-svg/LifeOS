from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = os.environ.get(
        "NIYAM_SECRET_KEY",
        "change-this-before-deployment"
    )

    # Default: SQLite for local development
    database_url = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'niyam.db'}"
    )

    # Render / Heroku legacy URL
    if database_url.startswith("postgres://"):
        database_url = database_url.replace(
            "postgres://",
            "postgresql+psycopg://",
            1,
        )

    # Render Internal Database URL
    elif database_url.startswith("postgresql://"):
        database_url = database_url.replace(
            "postgresql://",
            "postgresql+psycopg://",
            1,
        )

    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    REMEMBER_COOKIE_DURATION = 60 * 60 * 24 * 30
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = (
        os.environ.get("FLASK_ENV") == "production"
    )