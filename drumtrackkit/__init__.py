from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import os

# Initialize SQLAlchemy with no settings (will configure later)
db = SQLAlchemy()
jwt = JWTManager()

"""
drumtrackkit package initialization.
"""
from flask import Flask
from flask_cors import CORS


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    CORS(app)

    # Configure the app
    app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this to a secure key
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Add a simple route for the root URL
    @app.route('/')
    def index():
        return "DrumTracKAI is running! API endpoints are available."

    # Import and register blueprints
    try:
        from drumtrackkit.api import auth_bp
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
    except ImportError:
        pass  # Skip if not available

    try:
        from drumtrackkit.api import youtube_bp
        app.register_blueprint(youtube_bp, url_prefix='/api/youtube')
    except ImportError:
        pass  # Skip if not available

    # Initialize database
    try:
        from drumtrackkit.models import db
        db.init_app(app)
        with app.app_context():
            db.create_all()
    except ImportError:
        pass  # Skip if not available

    # Return the configured app
    return app