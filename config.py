from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = os.environ.get("NIYAM_SECRET_KEY", "change-this-before-deployment")
    database_url = os.environ.get("DATABASE_URL", f"sqlite:///{BASE_DIR / 'niyam.db'}")
    # Some hosting providers expose the legacy postgres:// scheme. SQLAlchemy
    # requires the current PostgreSQL dialect name.
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+psycopg://", 1)
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REMEMBER_COOKIE_DURATION = 60 * 60 * 24 * 30
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("FLASK_ENV") == "production"
