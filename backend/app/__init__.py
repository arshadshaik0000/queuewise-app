"""Flask application factory for QueueWise."""

import os

from flask import Flask, send_from_directory
from flask_cors import CORS

from app.config import Config
from app.database import db
# Import all models so db.create_all() registers every table
from app.models.queue_event import QueueEvent  # noqa: F401


def create_app(config_class=Config):
    """Create and configure the Flask application.

    Uses the application factory pattern so tests can create
    isolated app instances with different configurations.
    In production, serves the React frontend static files.
    """
    static_dir = os.path.join(os.path.dirname(__file__), '..', 'static')
    app = Flask(__name__, static_folder=static_dir, static_url_path='')
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    CORS(app)

    # Register request tracing + API versioning middleware
    from app.logging_utils import register_request_tracing
    register_request_tracing(app)

    # Register blueprints
    from app.routes.queue_routes import queue_bp
    app.register_blueprint(queue_bp)

    # Serve React frontend in production (catch-all for client-side routing)
    @app.route('/')
    @app.route('/<path:path>')
    def serve_frontend(path=''):
        """Serve static files or fall back to index.html for SPA routing."""
        if path and os.path.isfile(os.path.join(static_dir, path)):
            return send_from_directory(static_dir, path)
        index_path = os.path.join(static_dir, 'index.html')
        if os.path.isfile(index_path):
            return send_from_directory(static_dir, 'index.html')
        return 'Frontend not built. Run: cd frontend && npm run build', 404

    # Create database tables
    with app.app_context():
        db.create_all()

    return app
