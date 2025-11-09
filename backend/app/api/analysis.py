from fastapi import APIRouter, HTTPException, status
from loguru import logger

from app.models.schemas import AnalysisResponse

router = APIRouter()


@router.get("/{recording_id}", response_model=AnalysisResponse)
async def get_analysis(recording_id: int):
    """
    Get AI analysis results for a recording

    Returns:
    - Extracted entities (people, companies, locations)
    - Identified interests and topics
    - User intents (investment, partnership, etc.)
    - Pain points and offerings
    - Overall sentiment and summary
    """
    logger.info(f"Fetching analysis for recording: {recording_id}")

    # TODO: Retrieve analysis from database

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Analysis for recording {recording_id} not found"
    )


@router.post("/{recording_id}/regenerate", status_code=status.HTTP_202_ACCEPTED)
async def regenerate_analysis(recording_id: int):
    """
    Regenerate analysis for a recording using latest LLM models
    """
    logger.info(f"Regenerating analysis for recording: {recording_id}")

    # TODO: Queue analysis regeneration job

    return {"message": "Analysis regeneration queued", "recording_id": recording_id}
