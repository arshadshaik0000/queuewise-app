"""Shared SQLAlchemy instance.

This module exists so every layer can import `db` without circular imports.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
