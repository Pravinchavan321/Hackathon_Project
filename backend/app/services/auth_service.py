"""Authentication and Identity Service for AgentShield AI.
Implements bcrypt password hashing, JWT token issuance/verification, and RBAC utilities.
"""
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import bcrypt
import jwt
from backend.app.config import get_settings
from backend.app.models.user import UserCreate, UserResponse, UserRole, UserStatus
from backend.app.database import collections

settings = get_settings()

# In-memory user cache for tests & offline fallback
_MEMORY_USERS: Dict[str, Dict[str, Any]] = {}


def hash_password(password: str) -> str:
    """Hash plaintext password with bcrypt (12 rounds)."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against bcrypt hash."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generate signed JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm="HS256")


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and validate JWT access token."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.PyJWTError:
        return None


def register_user(db, user_in: UserCreate) -> UserResponse:
    """Register a new user account. Public registration forces EMPLOYEE role."""
    email_clean = user_in.email.lower().strip()

    # Check existence
    existing = None
    if db is not None:
        existing = db[collections.USERS].find_one({"email": email_clean})
    else:
        existing = _MEMORY_USERS.get(email_clean)

    if existing:
        raise ValueError("An account with this email address already exists.")

    user_id = "u-" + uuid.uuid4().hex[:8]
    hashed_pwd = hash_password(user_in.password)
    now = datetime.utcnow()

    # Public registration can only create EMPLOYEE
    assigned_role = user_in.role if user_in.role == UserRole.EMPLOYEE else UserRole.EMPLOYEE

    doc = {
        "user_id": user_id,
        "email": email_clean,
        "password_hash": hashed_pwd,
        "full_name": user_in.full_name,
        "role": assigned_role.value,
        "status": UserStatus.ACTIVE.value,
        "department": user_in.department or "General",
        "created_at": now,
        "updated_at": now,
    }

    if db is not None:
        db[collections.USERS].insert_one(doc)
    _MEMORY_USERS[email_clean] = doc

    return UserResponse(
        user_id=user_id,
        email=email_clean,
        full_name=user_in.full_name,
        department=user_in.department or "General",
        role=assigned_role,
        status=UserStatus.ACTIVE,
        created_at=now,
    )


def authenticate_user(db, email: str, password: str) -> Optional[UserResponse]:
    """Authenticate credentials and return user profile if valid."""
    email_clean = email.lower().strip()
    user_doc = None
    if db is not None:
        user_doc = db[collections.USERS].find_one({"email": email_clean})
    if not user_doc:
        user_doc = _MEMORY_USERS.get(email_clean)

    if not user_doc:
        return None

    if not verify_password(password, user_doc["password_hash"]):
        return None

    return UserResponse(
        user_id=user_doc["user_id"],
        email=user_doc["email"],
        full_name=user_doc["full_name"],
        department=user_doc.get("department", "General"),
        role=UserRole(user_doc["role"]),
        status=UserStatus(user_doc["status"]),
        created_at=user_doc["created_at"],
    )


def seed_admin_user(db) -> UserResponse:
    """Seed default administrator if none exists."""
    admin_email = "admin@agentshield.ai"
    existing = None
    if db is not None:
        existing = db[collections.USERS].find_one({"email": admin_email})
    else:
        existing = _MEMORY_USERS.get(admin_email)

    if existing:
        return UserResponse(
            user_id=existing["user_id"],
            email=existing["email"],
            full_name=existing["full_name"],
            department=existing.get("department", "Security"),
            role=UserRole(existing["role"]),
            status=UserStatus(existing["status"]),
            created_at=existing["created_at"],
        )

    user_id = "u-admin001"
    now = datetime.utcnow()
    doc = {
        "user_id": user_id,
        "email": admin_email,
        "password_hash": hash_password("Admin@Shield2026"),
        "full_name": "AgentShield Administrator",
        "role": UserRole.ADMIN.value,
        "status": UserStatus.ACTIVE.value,
        "department": "Security & Governance",
        "created_at": now,
        "updated_at": now,
    }

    if db is not None:
        db[collections.USERS].insert_one(doc)
    _MEMORY_USERS[admin_email] = doc

    return UserResponse(
        user_id=user_id,
        email=admin_email,
        full_name="AgentShield Administrator",
        department="Security & Governance",
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
        created_at=now,
    )
