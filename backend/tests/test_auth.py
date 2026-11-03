"""Phase 3 Verification Tests — Database, Authentication, and RBAC."""
import uuid
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    _MEMORY_USERS,
)


@pytest.fixture(autouse=True)
def clear_memory_users():
    """Clear in-memory user registry between test cases to ensure test isolation."""
    _MEMORY_USERS.clear()


@pytest.fixture
def client():
    return TestClient(app)


def test_password_hashing():
    """Verify bcrypt hashes passwords properly and verifies correctly."""
    pwd = "SecurePassword123!"
    hashed = hash_password(pwd)
    assert hashed != pwd
    assert verify_password(pwd, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_jwt_token_cycle():
    """Verify JWT access token generation and decoding."""
    payload = {"sub": "u-12345", "role": "MANAGER", "email": "manager@example.com"}
    token = create_access_token(payload)
    assert isinstance(token, str)
    decoded = decode_access_token(token)
    assert decoded["sub"] == "u-12345"
    assert decoded["role"] == "MANAGER"


def test_register_and_login_flow(client):
    """Test full registration and login cycle."""
    email = f"emp-{uuid.uuid4().hex[:6]}@example.com"
    pwd = "P@ssword12345"

    # Register
    reg_res = client.post("/api/v1/auth/register", json={
        "email": email,
        "password": pwd,
        "full_name": "Test Employee",
        "department": "Engineering"
    })
    assert reg_res.status_code == 201
    data = reg_res.json()
    assert data["email"] == email
    assert data["role"] == "EMPLOYEE"
    assert "user_id" in data

    # Attempt Duplicate Registration -> should fail with 400
    dup_res = client.post("/api/v1/auth/register", json={
        "email": email,
        "password": pwd,
        "full_name": "Another Person"
    })
    assert dup_res.status_code == 400

    # Login
    login_res = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": pwd
    })
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

    token = token_data["access_token"]

    # Access /me with token
    me_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["email"] == email
    assert me_data["role"] == "EMPLOYEE"


def test_login_invalid_password(client):
    """Verify login with incorrect password returns 401."""
    email = f"emp-{uuid.uuid4().hex[:6]}@example.com"
    client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "CorrectPassword123",
        "full_name": "Test Employee"
    })
    res = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": "WrongPassword999"
    })
    assert res.status_code == 401


def test_unauthenticated_access_denied(client):
    """Verify protected endpoints reject requests without tokens."""
    res = client.get("/api/v1/auth/me")
    assert res.status_code == 401


def test_public_registration_cannot_escalate_to_admin(client):
    """Verify that a client attempting to pass role=ADMIN in registration is forced to EMPLOYEE."""
    email = f"hacker-{uuid.uuid4().hex[:6]}@example.com"
    res = client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "Password12345",
        "full_name": "Malicious User",
        "role": "ADMIN"
    })
    assert res.status_code == 201
    assert res.json()["role"] == "EMPLOYEE"
