"""
Leads API endpoints for Lakshya (Lead Generation)
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.core.database import get_db
from app.models.database import User, Lead, Recording
from app.services.auth import get_current_user
from app.services.lead_generation import get_lead_generation_service
from pydantic import BaseModel

router = APIRouter()


class LeadResponse(BaseModel):
    """Lead response schema"""
    id: int
    recording_id: int
    name: str
    company: str | None
    role: str | None
    opportunity_type: str | None
    opportunity_description: str | None
    priority: str | None
    linkedin_url: str | None
    email: str | None
    company_website: str | None
    notes: str | None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GenerateLeadsRequest(BaseModel):
    """Request to generate leads from a recording"""
    recording_id: int
    recipient_email: str | None = None


class GenerateLeadsResponse(BaseModel):
    """Response from lead generation"""
    success: bool
    job_id: int | None = None
    recording_id: int | None = None
    leads_count: int | None = None
    message: str
    error: str | None = None


@router.post("/generate", response_model=GenerateLeadsResponse)
async def generate_leads(
    request: GenerateLeadsRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate leads from a recording's transcript
    Runs in background and saves leads to database
    """
    # Verify recording belongs to user
    recording = db.query(Recording).filter(
        Recording.id == request.recording_id,
        Recording.user_id == current_user.id
    ).first()

    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")

    if not recording.transcript:
        raise HTTPException(status_code=400, detail="Recording has no transcript. Process it first.")

    # Use user's email if not provided
    recipient_email = request.recipient_email or current_user.email

    # Get lead generation service
    service = get_lead_generation_service()

    # Run in background
    background_tasks.add_task(
        service.generate_leads_from_transcript,
        request.recording_id,
        recipient_email,
        db
    )

    return GenerateLeadsResponse(
        success=True,
        recording_id=request.recording_id,
        message="Lead generation started in background. You will receive an email when complete."
    )


@router.get("/recording/{recording_id}", response_model=List[LeadResponse])
async def list_leads_for_recording(
    recording_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List leads for a specific recording"""
    # Verify recording belongs to user
    recording = db.query(Recording).filter(
        Recording.id == recording_id,
        Recording.user_id == current_user.id
    ).first()

    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")

    leads = db.query(Lead).filter(
        Lead.recording_id == recording_id
    ).order_by(
        Lead.created_at.desc()
    ).all()

    return leads


@router.get("/", response_model=List[LeadResponse])
async def list_all_leads(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all leads for the current user across all recordings"""
    # Get user's recordings
    recording_ids = db.query(Recording.id).filter(
        Recording.user_id == current_user.id
    ).all()

    recording_ids = [r[0] for r in recording_ids]

    leads = db.query(Lead).filter(
        Lead.recording_id.in_(recording_ids)
    ).order_by(
        Lead.created_at.desc()
    ).offset(skip).limit(limit).all()

    return leads


@router.patch("/{lead_id}/status")
async def update_lead_status(
    lead_id: int,
    status: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update lead status (new, contacted, in_progress, closed)"""
    # Get lead and verify user owns the recording
    lead = db.query(Lead).join(Recording).filter(
        Lead.id == lead_id,
        Recording.user_id == current_user.id
    ).first()

    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    lead.status = status
    lead.updated_at = datetime.utcnow()
    db.commit()

    return {"message": f"Lead status updated to {status}"}


@router.delete("/{lead_id}")
async def delete_lead(
    lead_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a lead"""
    # Get lead and verify user owns the recording
    lead = db.query(Lead).join(Recording).filter(
        Lead.id == lead_id,
        Recording.user_id == current_user.id
    ).first()

    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    db.delete(lead)
    db.commit()

    return {"message": "Lead deleted"}