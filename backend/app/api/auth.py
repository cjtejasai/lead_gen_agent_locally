"""
Authentication API endpoints - Signup, Login, Profile
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import timedelta
import logging

from app.core.database import get_db
from app.models.database import User, UserProfile
from app.models.schemas import (
    UserSignup, UserLogin, Token, UserResponse,
    UserProfileUpdate
)
from app.services.auth import (
    get_password_hash, verify_password, create_access_token,
    get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserSignup, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Register a new user and trigger event discovery
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        full_name=user_data.full_name,
        is_active=True
    )

    db.add(new_user)
    db.flush()  # Get user ID

    # Create user profile with interests
    user_profile = UserProfile(
        user_id=new_user.id,
        location=user_data.location,
        interests=user_data.interests,
        looking_for=user_data.looking_for
    )

    db.add(user_profile)
    db.commit()
    db.refresh(new_user)

    logger.info(f"New user registered: {new_user.email}")

    # Trigger event discovery in background
    from app.services.event_discovery import EventDiscoveryService
    discovery_service = EventDiscoveryService(db)
    background_tasks.add_task(discovery_service.run_for_user, new_user.id)
    logger.info(f"Event discovery scheduled for user {new_user.id}")

    # Create access token
    access_token = create_access_token(
        data={"sub": new_user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=new_user.id,
            email=new_user.email,
            full_name=new_user.full_name,
            category="general",  # Default category
            created_at=new_user.created_at,
            is_active=new_user.is_active
        )
    )


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login user and return JWT token
    """
    # Find user
    user = db.query(User).filter(User.email == credentials.email).first()

    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )

    # Create access token
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    logger.info(f"User logged in: {user.email}")

    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            category="general",
            created_at=user.created_at,
            is_active=user.is_active
        )
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    Get current user's profile
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        category="general",
        created_at=current_user.created_at,
        is_active=current_user.is_active
    )


@router.put("/profile", response_model=dict)
async def update_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user profile
    """
    # Get or create user profile
    user_profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user.id
    ).first()

    if not user_profile:
        user_profile = UserProfile(user_id=current_user.id)
        db.add(user_profile)

    # Update fields
    if profile_data.full_name:
        current_user.full_name = profile_data.full_name

    if profile_data.company:
        user_profile.company = profile_data.company

    if profile_data.role:
        user_profile.role = profile_data.role

    if profile_data.location:
        user_profile.location = profile_data.location

    if profile_data.interests is not None:
        user_profile.interests = profile_data.interests

    if profile_data.hobbies is not None:
        user_profile.hobbies = profile_data.hobbies

    if profile_data.looking_for is not None:
        user_profile.looking_for = profile_data.looking_for

    db.commit()

    logger.info(f"Profile updated for user: {current_user.email}")

    return {"message": "Profile updated successfully"}


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout user (client should delete token)
    """
    logger.info(f"User logged out: {current_user.email}")
    return {"message": "Successfully logged out"}