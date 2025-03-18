from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import os

# Initialize SQLAlchemy with no settings (will configure later)
db = SQLAlchemy()
jwt = JWTManager()

def create_app(config=None):
    app = Flask(__name__)
    
    # Configure from object, file, or environment variable
    if config:
        app.config.from_object(config)
    else:
        # Default configuration
        app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-key-for-testing")
        app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///drumtrackkai.db")
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "jwt-dev-key")
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    
    # Simple root route
    @app.route("/")
    def home():
        return "DrumTracKAI is running!"
    
    # Register blueprints
    try:
        from .api.auth import auth_bp
        app.register_blueprint(auth_bp, url_prefix="/api/auth")
    except ImportError as e:
        app.logger.warning(f"Could not register auth blueprint: {e}")
    
    try:
        from .api.analysis import analysis_bp
        app.register_blueprint(analysis_bp, url_prefix="/api/analysis")
    except ImportError as e:
        app.logger.warning(f"Could not register analysis blueprint: {e}")
    
    try:
        from .api.youtube import youtube_bp
        app.register_blueprint(youtube_bp, url_prefix="/api/youtube")
    except ImportError as e:
        app.logger.warning(f"Could not register youtube blueprint: {e}")
    
    try:
        from .api.subscription import subscription_bp
        app.register_blueprint(subscription_bp, url_prefix="/api/subscription")
    except ImportError as e:
        app.logger.warning(f"Could not register subscription blueprint: {e}")
    
    try:
        from .api.style import style_bp
        app.register_blueprint(style_bp, url_prefix="/api/style")
    except ImportError as e:
        app.logger.warning(f"Could not register style blueprint: {e}")
    
    # Import models to ensure they're registered with SQLAlchemy
    # The order here is important for foreign key relationships
    with app.app_context():
        # Import models in the correct order (parent tables first)
        from .models.user import User  # Users table must be created before tasks
        from .models.analysis import Analysis
        
        # Create database tables for models without dependencies
        db.create_all()
        
        # Now import models with dependencies
        from .models.task import Task
        
        # Create tables for the remaining models
        db.create_all()
    
    return app
