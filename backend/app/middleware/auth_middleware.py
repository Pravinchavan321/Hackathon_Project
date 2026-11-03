"""Authentication & RBAC Middleware dependencies for FastAPI."""
from typing import List, Optional
from fastapi import Depends, HTTPException, Header, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.app.services.auth_service import decode_access_token
from backend.app.models.user import UserRole
from backend.app.config import get_settings

settings = get_settings()
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    x_role: Optional[str] = Header(None, alias="X-Role"),
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
) -> dict:
    """Extract authenticated principal.
    Supports JWT Bearer authentication, with secure dev/demo fallback via X-Role header in development.
    """
    # 1. Check JWT token first
    if credentials and credentials.credentials:
        payload = decode_access_token(credentials.credentials)
        if payload and "sub" in payload:
            return {
                "user_id": payload["sub"],
                "email": payload.get("email", ""),
                "role": payload.get("role", UserRole.EMPLOYEE.value),
            }
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. In dev/test mode, allow simulated principal headers for testing flexibility
    if settings.APP_ENV in ["development", "testing"] and x_role:
        role_val = x_role.upper()
        if role_val in [r.value for r in UserRole]:
            return {
                "user_id": x_user_id or "u-dev-test",
                "email": "dev@agentshield.ai",
                "role": role_val,
            }

    # If no valid token found
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing or invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def require_role(allowed_roles: List[UserRole]):
    """Enforce that authenticated user possesses one of the allowed roles."""
    async def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        user_role = current_user.get("role")
        if not user_role or user_role not in [r.value for r in allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: Action requires one of {[r.value for r in allowed_roles]} roles",
            )
        return current_user
    return role_checker


# Role shortcut dependencies
require_admin = require_role([UserRole.ADMIN])
require_manager_or_admin = require_role([UserRole.MANAGER, UserRole.ADMIN])
