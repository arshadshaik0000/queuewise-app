"""Application configuration."""

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration with sensible defaults."""

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(BASE_DIR, '..', 'queuewise.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestConfig(Config):
    """Overrides for test runs — uses in-memory SQLite."""

    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    TESTING = True
