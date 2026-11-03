"""Authentication API routes under /api/v1/auth."""
from fastapi import APIRouter, HTTPException, Depends, status
from backend.app.models.user import UserCreate, UserLogin, UserResponse
from backend.app.services.auth_service import register_user, authenticate_user, create_access_token
from backend.app.middleware.auth_middleware import get_current_user
from backend.app.database.mongodb import mongo_manager

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate):
    """Register a new user account (defaults strictly to EMPLOYEE role)."""
    db = mongo_manager.get_db()
    try:
        user = register_user(db, user_in)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login")
def login(credentials: UserLogin):
    """Authenticate with email and password to receive JWT token."""
    db = mongo_manager.get_db()
    user = authenticate_user(db, credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    token = create_access_token({
        "sub": user.user_id,
        "email": user.email,
        "role": user.role.value,
        "name": user.full_name
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user.model_dump()
    }


@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    """Retrieve profile of the currently authenticated principal."""
    return current_user


@router.post("/logout")
def logout(current_user: dict = Depends(get_current_user)):
    """Acknowledge logout."""
    return {"message": "Successfully logged out"}
