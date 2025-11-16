from fastapi import APIRouter, HTTPException, status, Depends
from loguru import logger
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from app.models.schemas import UserResponse, UserStats
from app.models.database import User, UserProfile
from app.services.auth import get_current_user
from app.core.database import get_db

router = APIRouter()


class ProfileUpdateRequest(BaseModel):
    """Profile update request schema"""
    company: str | None = None
    role: str | None = None
    location: str | None = None
    interests: List[str] | None = None
    hobbies: List[str] | None = None
    looking_for: List[str] | None = None


@router.get("/me")
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user's profile
    """
    logger.info(f"Fetching profile for user {current_user.id}")

    # Get or create profile
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()

    if not profile:
        # Create empty profile if doesn't exist
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)

    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "profile": {
            "company": profile.company,
            "role": profile.role,
            "location": profile.location,
            "interests": profile.interests or [],
            "hobbies": profile.hobbies or [],
            "looking_for": profile.looking_for or []
        }
    }


@router.put("/me")
async def update_profile(
    profile_data: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's profile
    """
    logger.info(f"Updating profile for user {current_user.id}")

    # Get or create profile
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()

    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)

    # Update fields if provided
    if profile_data.company is not None:
        profile.company = profile_data.company
    if profile_data.role is not None:
        profile.role = profile_data.role
    if profile_data.location is not None:
        profile.location = profile_data.location
    if profile_data.interests is not None:
        profile.interests = profile_data.interests
    if profile_data.hobbies is not None:
        profile.hobbies = profile_data.hobbies
    if profile_data.looking_for is not None:
        profile.looking_for = profile_data.looking_for

    db.commit()
    db.refresh(profile)

    logger.info(f"Profile updated for user {current_user.id}")

    return {
        "message": "Profile updated successfully",
        "profile": {
            "company": profile.company,
            "role": profile.role,
            "location": profile.location,
            "interests": profile.interests or [],
            "hobbies": profile.hobbies or [],
            "looking_for": profile.looking_for or []
        }
    }


@router.get("/me/stats", response_model=UserStats)
async def get_user_stats():
    """
    Get user's statistics and activity summary
    """
    logger.info("Fetching user stats")

    # TODO: Aggregate stats from database and graph

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Stats not yet implemented"
    )


@router.get("/me/interests")
async def get_user_interests():
    """
    Get user's interest graph
    """
    logger.info("Fetching user interests")

    # TODO: Query Neo4j for user's interests and connections

    return {"interests": [], "connections": []}


@router.post("/me/interests")
async def add_user_interest(interest_data: dict):
    """
    Manually add an interest to user's profile
    """
    logger.info("Adding user interest")

    # TODO: Add interest to Neo4j graph

    return {"message": "Interest added"}
