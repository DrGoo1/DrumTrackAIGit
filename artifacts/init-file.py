import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Import configuration
from drumtrackkit.config import get_config

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address)


def create_app(config_class=None):
    """Create and configure the Flask application"""
    app = Flask(__name__)

    # Load configuration
    if config_class is None:
        config_class = get_config()
    app.config.from_object(config_class)

    # Configure logging
    configure_logging(app)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    limiter.init_app(app)

    # Ensure upload directories exist
    with app.app_context():
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(app.config['AUDIO_DOWNLOAD_DIR'], exist_ok=True)
        os.makedirs(app.config['RESULTS_DIR'], exist_ok=True)

    # Register error handlers
    from drumtrackkit.utils.error_handler import register_error_handlers
    register_error_handlers(app)

    # Register blueprints
    from drumtrackkit.api.auth import auth_bp
    from drumtrackkit.api.analysis import analysis_bp
    from drumtrackkit.api.youtube import youtube_bp
    from drumtrackkit.api.subscription import subscription_bp
    from drumtrackkit.api.style import style_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(analysis_bp, url_prefix='/api/analyze')
    app.register_blueprint(youtube_bp, url_prefix='/api/youtube')
    app.register_blueprint(subscription_bp, url_prefix='/api/subscription')
    app.register_blueprint(style_bp, url_prefix='/api/style')

    # Initialize database tables
    @app.before_first_request
    def create_tables():
        db.create_all()

    # Initialize the task service
    from drumtrackkit.services.task_service import TaskService
    app.task_service = TaskService()

    # Add health check endpoint
    @app.route('/health')
    def health_check():
        return {"status": "ok", "version": "1.0.0"}, 200

    return app


def configure_logging(app):
    """Configure application logging"""
    # Set log level based on configuration
    log_level = getattr(logging, app.config.get('LOGGING_LEVEL', 'INFO'))

    # Basic console handler for all environments
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)

    # App logger configuration
    app_logger = logging.getLogger('drumtrackkai')
    app_logger.setLevel(log_level)

    # Add file handler in production
    if not app.config.get('DEBUG', False):
        # Ensure log directory exists
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(log_dir, exist_ok=True)

        # Create rotating file handler
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, 'drumtrackkai.log'),
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=10
        )
        file_handler.setLevel(log_level)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)

        # Add file handler to loggers
        root_logger.addHandler(file_handler)

    # Reduce noise from third-party libraries
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy').setLevel(logging.WARNING)

    return app_logger