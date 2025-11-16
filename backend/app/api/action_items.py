"""
Action Items API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from app.core.database import get_db
from app.models.database import ActionItem, Recording, User
from app.services.auth import get_current_user
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()


# Pydantic schemas
class ActionItemResponse(BaseModel):
    id: int
    recording_id: int
    recording_title: str
    action: str
    deadline: Optional[datetime]
    deadline_type: str
    priority: str
    action_type: str
    quote: Optional[str]
    mentioned_by: Optional[str]
    speaker_name: Optional[str]
    timestamp_seconds: Optional[float]
    contact_email: Optional[str]
    contact_company: Optional[str]
    status: str
    completed_at: Optional[datetime]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ActionItemUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    deadline: Optional[datetime] = None


class ActionItemStats(BaseModel):
    total: int
    pending: int
    in_progress: int
    completed: int
    cancelled: int
    high_priority: int
    medium_priority: int
    low_priority: int
    overdue: int
    due_today: int
    due_this_week: int


@router.get("/", response_model=List[ActionItemResponse])
async def list_action_items(
    status: Optional[str] = Query(None, description="Filter by status: pending, in_progress, completed, cancelled"),
    priority: Optional[str] = Query(None, description="Filter by priority: high, medium, low"),
    recording_id: Optional[int] = Query(None, description="Filter by recording ID"),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all action items for the current user with optional filters
    """
    # Build query - join with recordings to filter by user
    query = db.query(ActionItem).join(Recording).filter(
        Recording.user_id == current_user.id
    )

    # Apply filters
    if status:
        query = query.filter(ActionItem.status == status)

    if priority:
        query = query.filter(ActionItem.priority == priority)

    if recording_id:
        query = query.filter(ActionItem.recording_id == recording_id)

    # Order by deadline (nulls last) and created_at
    query = query.order_by(
        ActionItem.deadline.asc().nullslast(),
        ActionItem.created_at.desc()
    )

    action_items = query.offset(skip).limit(limit).all()

    # Build response with recording titles
    results = []
    for item in action_items:
        recording = db.query(Recording).filter(Recording.id == item.recording_id).first()
        results.append(ActionItemResponse(
            id=item.id,
            recording_id=item.recording_id,
            recording_title=recording.title if recording else "Unknown",
            action=item.action,
            deadline=item.deadline,
            deadline_type=item.deadline_type,
            priority=item.priority,
            action_type=item.action_type,
            quote=item.quote,
            mentioned_by=item.mentioned_by,
            speaker_name=item.speaker_name,
            timestamp_seconds=item.timestamp_seconds,
            contact_email=item.contact_email,
            contact_company=item.contact_company,
            status=item.status,
            completed_at=item.completed_at,
            notes=item.notes,
            created_at=item.created_at
        ))

    return results


@router.get("/stats", response_model=ActionItemStats)
async def get_action_item_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get statistics about action items for the current user
    """
    # Get all action items for user
    action_items = db.query(ActionItem).join(Recording).filter(
        Recording.user_id == current_user.id
    ).all()

    now = datetime.utcnow()
    today_end = now.replace(hour=23, minute=59, second=59)
    week_end = now + timedelta(days=7)

    stats = ActionItemStats(
        total=len(action_items),
        pending=sum(1 for item in action_items if item.status == "pending"),
        in_progress=sum(1 for item in action_items if item.status == "in_progress"),
        completed=sum(1 for item in action_items if item.status == "completed"),
        cancelled=sum(1 for item in action_items if item.status == "cancelled"),
        high_priority=sum(1 for item in action_items if item.priority == "high"),
        medium_priority=sum(1 for item in action_items if item.priority == "medium"),
        low_priority=sum(1 for item in action_items if item.priority == "low"),
        overdue=sum(1 for item in action_items if item.deadline and item.deadline < now and item.status not in ["completed", "cancelled"]),
        due_today=sum(1 for item in action_items if item.deadline and item.deadline <= today_end and item.deadline >= now and item.status not in ["completed", "cancelled"]),
        due_this_week=sum(1 for item in action_items if item.deadline and item.deadline <= week_end and item.deadline >= now and item.status not in ["completed", "cancelled"])
    )

    return stats


@router.get("/{action_item_id}", response_model=ActionItemResponse)
async def get_action_item(
    action_item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific action item by ID
    """
    action_item = db.query(ActionItem).join(Recording).filter(
        ActionItem.id == action_item_id,
        Recording.user_id == current_user.id
    ).first()

    if not action_item:
        raise HTTPException(status_code=404, detail="Action item not found")

    recording = db.query(Recording).filter(Recording.id == action_item.recording_id).first()

    return ActionItemResponse(
        id=action_item.id,
        recording_id=action_item.recording_id,
        recording_title=recording.title if recording else "Unknown",
        action=action_item.action,
        deadline=action_item.deadline,
        deadline_type=action_item.deadline_type,
        priority=action_item.priority,
        action_type=action_item.action_type,
        quote=action_item.quote,
        mentioned_by=action_item.mentioned_by,
        speaker_name=action_item.speaker_name,
        timestamp_seconds=action_item.timestamp_seconds,
        contact_email=action_item.contact_email,
        contact_company=action_item.contact_company,
        status=action_item.status,
        completed_at=action_item.completed_at,
        notes=action_item.notes,
        created_at=action_item.created_at
    )


@router.patch("/{action_item_id}")
async def update_action_item(
    action_item_id: int,
    update: ActionItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an action item (status, notes, deadline)
    """
    action_item = db.query(ActionItem).join(Recording).filter(
        ActionItem.id == action_item_id,
        Recording.user_id == current_user.id
    ).first()

    if not action_item:
        raise HTTPException(status_code=404, detail="Action item not found")

    # Update fields
    if update.status is not None:
        action_item.status = update.status

        # Auto-set completed_at when marked as completed
        if update.status == "completed" and not action_item.completed_at:
            action_item.completed_at = datetime.utcnow()

        # Clear completed_at if status changed from completed
        if update.status != "completed" and action_item.completed_at:
            action_item.completed_at = None

    if update.notes is not None:
        action_item.notes = update.notes

    if update.deadline is not None:
        action_item.deadline = update.deadline

    action_item.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(action_item)

    logger.info(f"Action item {action_item_id} updated by user {current_user.id}")

    return {
        "message": "Action item updated successfully",
        "action_item_id": action_item_id,
        "status": action_item.status
    }


@router.delete("/{action_item_id}")
async def delete_action_item(
    action_item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete an action item
    """
    action_item = db.query(ActionItem).join(Recording).filter(
        ActionItem.id == action_item_id,
        Recording.user_id == current_user.id
    ).first()

    if not action_item:
        raise HTTPException(status_code=404, detail="Action item not found")

    db.delete(action_item)
    db.commit()

    logger.info(f"Action item {action_item_id} deleted by user {current_user.id}")

    return {
        "message": "Action item deleted successfully",
        "action_item_id": action_item_id
    }