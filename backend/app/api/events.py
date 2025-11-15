"""
Events API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime

from app.core.database import get_db
from app.models.database import User, Event
from app.services.auth import get_current_user
from app.services.event_discovery import EventDiscoveryService
from pydantic import BaseModel

router = APIRouter()


class EventResponse(BaseModel):
    """Event response schema"""
    id: int
    title: str
    description: str | None
    url: str | None
    date: str | None
    location: str | None
    event_type: str | None
    relevance_score: float | None
    relevance_reason: str | None
    source: str | None
    matched_interests: List[str] | None
    exhibitors: Dict[str, Any] | None
    is_saved: bool
    is_attending: bool
    created_at: datetime

    class Config:
        from_attributes = True


class DiscoveryJobResponse(BaseModel):
    """Discovery job response"""
    success: bool
    job_id: int | None = None
    events_found: int | None = None
    message: str
    error: str | None = None


@router.post("/discover", response_model=DiscoveryJobResponse)
async def discover_events(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Trigger event discovery for the current user
    Runs in background and saves events to database
    """
    service = EventDiscoveryService(db)

    # Run in background
    background_tasks.add_task(service.run_for_user, current_user.id)

    return DiscoveryJobResponse(
        success=True,
        message="Event discovery started in background",
        job_id=None
    )


@router.get("/", response_model=List[EventResponse])
async def list_events(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List events for the current user"""
    events = db.query(Event).filter(
        Event.user_id == current_user.id
    ).order_by(
        Event.relevance_score.desc(),
        Event.created_at.desc()
    ).offset(skip).limit(limit).all()

    return events


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific event"""
    event = db.query(Event).filter(
        Event.id == event_id,
        Event.user_id == current_user.id
    ).first()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    return event


@router.patch("/{event_id}/save")
async def save_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark event as saved"""
    event = db.query(Event).filter(
        Event.id == event_id,
        Event.user_id == current_user.id
    ).first()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    event.is_saved = True
    event.updated_at = datetime.utcnow()
    db.commit()

    return {"message": "Event saved"}


@router.patch("/{event_id}/attend")
async def attend_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark event as attending"""
    event = db.query(Event).filter(
        Event.id == event_id,
        Event.user_id == current_user.id
    ).first()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    event.is_attending = True
    event.updated_at = datetime.utcnow()
    db.commit()

    return {"message": "Marked as attending"}


@router.delete("/{event_id}")
async def delete_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an event"""
    event = db.query(Event).filter(
        Event.id == event_id,
        Event.user_id == current_user.id
    ).first()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    db.delete(event)
    db.commit()

    return {"message": "Event deleted"}