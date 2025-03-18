import os
from datetime import timedelta


class Config:
    """Base configuration class"""

    # Application settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')  # Change in production
    DEBUG = False
    TESTING = False

    # JWT settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'dev-jwt-key')  # Change in production
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # Database settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///drumtrackkai.db')

    # File storage settings
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    AUDIO_DOWNLOAD_DIR = os.environ.get('AUDIO_DOWNLOAD_DIR', os.path.join(UPLOAD_FOLDER, 'audio'))
    RESULTS_DIR = os.environ.get('RESULTS_DIR', 'results')
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MB

    # YouTube API settings
    YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY', '')

    # Task service settings
    MAX_WORKER_THREADS = int(os.environ.get('MAX_WORKER_THREADS', '4'))
    TASK_RETENTION_DAYS = int(os.environ.get('TASK_RETENTION_DAYS', '30'))

    # Rate limiting
    RATELIMIT_DEFAULT = "100/hour"
    RATELIMIT_STRATEGY = "fixed-window"
    RATELIMIT_STORAGE_URL = "memory://"

    # Subscription settings
    FREE_TIER_CREDITS = int(os.environ.get('FREE_TIER_CREDITS', '3'))

    # Stripe settings
    STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY', '')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', '')
    STRIPE_PRICE_INDIVIDUAL = os.environ.get('STRIPE_PRICE_INDIVIDUAL', '')
    STRIPE_PRICE_PROFESSIONAL = os.environ.get('STRIPE_PRICE_PROFESSIONAL', '')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///drumtrackkai_dev.db')
    # Enable more detailed logging
    LOGGING_LEVEL = 'DEBUG'
    # Shorter token expiration for testing
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    # Disable rate limiting for tests
    RATELIMIT_ENABLED = False
    # Use test directories
    UPLOAD_FOLDER = 'test_uploads'
    AUDIO_DOWNLOAD_DIR = os.path.join('test_uploads', 'audio')
    RESULTS_DIR = 'test_results'


class ProductionConfig(Config):
    """Production configuration"""
    # Ensure all these are set in environment variables
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    # Production-specific settings
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'max_overflow': 20,
        'pool_recycle': 300
    }

    # Rate limiting with Redis in production
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

    # More workers in production
    MAX_WORKER_THREADS = int(os.environ.get('MAX_WORKER_THREADS', '8'))

    # SSL settings
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True


def get_config():
    """Get the appropriate configuration based on environment"""
    env = os.environ.get('FLASK_ENV', 'development')

    if env == 'production':
        return ProductionConfig
    elif env == 'testing':
        return TestingConfig
    else:
        return DevelopmentConfig