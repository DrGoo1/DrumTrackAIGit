"""
DrumTracKAI v4/v5 Advanced Dependencies
Database connections, authentication, and service dependencies
"""

import os
from fastapi import Depends, HTTPException, Request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .models import Base
import jwt
from typing import Optional, Dict, Any

# Database Configuration
DB_URL = os.getenv('DB_URL', 'sqlite:///./drumtrackai.db')
engine = create_engine(DB_URL, future=True, echo=False)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Ensure tables exist on import (simple bootstrap; swap to Alembic later)
Base.metadata.create_all(engine)

def get_db():
    """Database dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "drumtrackai-secret-key-change-in-production")
ALGORITHM = "HS256"

def decode_token(token: str) -> Dict[str, Any]:
    """Decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(request: Request) -> Dict[str, Any]:
    """Extract current user from JWT token"""
    # Try to get token from Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        return decode_token(token)
    
    # Fallback: mock user for development
    return {
        "user_id": "dev_user_001",
        "email": "dev@drumtrackai.com",
        "name": "Development User",
        "tier": "pro",
        "is_admin": True
    }

def get_current_user_optional(request: Request) -> Optional[Dict[str, Any]]:
    """Get current user, but don't require authentication"""
    try:
        return get_current_user(request)
    except HTTPException:
        return None

def require_admin(request: Request) -> Dict[str, Any]:
    """Require admin privileges"""
    user = get_current_user(request)
    if not user.get('is_admin'):
        raise HTTPException(status_code=403, detail='Admin privileges required')
    return user

def require_tier(min_tier: str):
    """Require minimum tier level"""
    tier_levels = {"basic": 1, "advanced": 2, "pro": 3}
    
    def _require_tier(request: Request) -> Dict[str, Any]:
        user = get_current_user(request)
        user_tier = user.get('tier', 'basic')
        
        if tier_levels.get(user_tier, 0) < tier_levels.get(min_tier, 0):
            raise HTTPException(
                status_code=403, 
                detail=f'Tier {min_tier} or higher required. Current tier: {user_tier}'
            )
        return user
    
    return _require_tier

# Service Dependencies
class ServiceContainer:
    """Container for service dependencies"""
    
    def __init__(self):
        self._services = {}
    
    def register(self, name: str, service):
        """Register a service"""
        self._services[name] = service
    
    def get(self, name: str):
        """Get a service"""
        return self._services.get(name)

# Global service container
services = ServiceContainer()

def get_service(name: str):
    """Dependency to get a service"""
    def _get_service():
        service = services.get(name)
        if not service:
            raise HTTPException(status_code=500, detail=f"Service {name} not available")
        return service
    return _get_service

# Specific service getters
def get_current_user():
    """Get current authenticated user - using dev auth shim"""
    try:
        from .auth import get_current_user as auth_get_current_user
        return auth_get_current_user()
    except ImportError:
        # Fallback to basic implementation
        return {"user_id": "test_user", "tier": "professional", "is_admin": True}

def get_audio_engine():
    """Get audio engine service"""
    return services.get('audio_engine')

def get_export_service():
    """Get export service"""
    return services.get('export_service')

def get_groove_analyzer():
    """Get groove analyzer service"""
    return services.get('groove_analyzer')

def get_reference_loops_service():
    """Get reference loops service"""
    return services.get('reference_loops')

# Usage tracking dependencies
def track_usage(endpoint: str, tier: str):
    """Track API usage for rate limiting"""
    # TODO: Implement usage tracking
    pass

def check_rate_limit(user_id: str, endpoint: str) -> bool:
    """Check if user has exceeded rate limits"""
    # TODO: Implement rate limiting
    return True
