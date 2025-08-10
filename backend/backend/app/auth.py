import os, time
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer(auto_error=False)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    DEV-ONLY shim: if no Authorization header, return a mock 'pro' user.
    Replace with your real auth import in prod.
    """
    if credentials and credentials.credentials:
        # In your real app, verify JWT and return payload
        return {"user_id": "jwt-user", "email":"user@example.com", "tier":"professional", "is_admin": False}
    # No header: return a friendly dev user
    return {"user_id":"dev-user", "email":"dev@local", "tier":"professional", "is_admin": True}
