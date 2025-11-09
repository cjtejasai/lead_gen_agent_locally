from fastapi import APIRouter, HTTPException, status
from loguru import logger

from app.models.schemas import UserResponse, UserStats

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user():
    """
    Get current authenticated user's profile
    """
    logger.info("Fetching current user profile")

    # TODO: Get user from auth token

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated"
    )


@router.put("/me", response_model=UserResponse)
async def update_profile(user_data: dict):
    """
    Update current user's profile
    """
    logger.info("Updating user profile")

    # TODO: Update user in database

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Profile update not yet implemented"
    )


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
