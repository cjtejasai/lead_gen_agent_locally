from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional
from loguru import logger

from app.models.schemas import (
    MatchResponse,
    MatchFeedResponse,
    MeetingScheduleRequest,
    MeetingScheduleResponse,
    UserCategory,
)

router = APIRouter()


@router.get("/feed", response_model=MatchFeedResponse)
async def get_match_feed(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category_filter: Optional[List[UserCategory]] = Query(None),
    min_score: float = Query(0.0, ge=0, le=100),
):
    """
    Get personalized feed of potential matches

    Filters:
    - category_filter: Filter by matched user category
    - min_score: Minimum match score threshold
    """
    logger.info(f"Fetching match feed: page={page}, page_size={page_size}")

    # TODO: Implement match retrieval from Neo4j
    # - Get user's interests and needs
    # - Run matching algorithm
    # - Score and rank matches
    # - Return paginated results

    return MatchFeedResponse(
        matches=[],
        total=0,
        page=page,
        page_size=page_size,
    )


@router.get("/{match_id}", response_model=MatchResponse)
async def get_match_details(match_id: int):
    """
    Get detailed information about a specific match
    """
    logger.info(f"Fetching match details: {match_id}")

    # TODO: Retrieve match from database

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Match {match_id} not found"
    )


@router.post("/{match_id}/accept", status_code=status.HTTP_200_OK)
async def accept_match(match_id: int):
    """
    Mark a match as accepted (interested in connecting)
    """
    logger.info(f"Accepting match: {match_id}")

    # TODO: Update match status in graph database

    return {"message": "Match accepted", "match_id": match_id}


@router.post("/{match_id}/dismiss", status_code=status.HTTP_200_OK)
async def dismiss_match(match_id: int):
    """
    Dismiss a match (not interested)
    """
    logger.info(f"Dismissing match: {match_id}")

    # TODO: Update match status

    return {"message": "Match dismissed", "match_id": match_id}


@router.post("/{match_id}/schedule", response_model=MeetingScheduleResponse)
async def schedule_meeting(match_id: int, request: MeetingScheduleRequest):
    """
    Schedule a meeting with a match via calendar integration
    """
    logger.info(f"Scheduling meeting for match: {match_id}")

    # TODO: Integrate with Google Calendar API
    # - Check availability
    # - Create calendar event
    # - Send invites
    # - Generate meeting link

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Calendar integration not yet implemented"
    )


@router.get("/", response_model=List[MatchResponse])
async def list_matches(
    status_filter: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 20,
):
    """
    List all matches with optional status filtering
    """
    logger.info(f"Listing matches with status={status_filter}")

    # TODO: Query matches from database

    return []


@router.post("/refresh", status_code=status.HTTP_202_ACCEPTED)
async def refresh_matches():
    """
    Trigger a refresh of potential matches based on latest data
    """
    logger.info("Refreshing matches")

    # TODO: Queue matching job

    return {"message": "Match refresh queued"}
