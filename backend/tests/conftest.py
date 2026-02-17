"""Shared test fixtures for QueueWise backend tests."""

import pytest

from app import create_app
from app.config import TestConfig
from app.database import db as _db


@pytest.fixture()
def app():
    """Create a fresh Flask app with an in-memory database for each test."""
    application = create_app(TestConfig)
    yield application


@pytest.fixture()
def client(app):
    """A Flask test client for making HTTP requests."""
    return app.test_client()


@pytest.fixture()
def db(app):
    """Provide a database session scoped to each test.

    Tables are created before each test and dropped after,
    so every test starts with a clean slate.
    """
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.rollback()
        _db.drop_all()
