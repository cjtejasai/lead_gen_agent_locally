"""
Dashboard API endpoints - Real statistics for the dashboard
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Dict, Any
import logging

from app.core.database import get_db
from app.models.database import Recording, Lead, Event, ActionItem, User
from app.services.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get dashboard statistics for the current user
    Returns real data for:
    - Total recordings
    - Active matches (leads)
    - Interests tracked (events)
    - Connections made (completed action items)
    """
    # Total recordings (excluding soft-deleted)
    total_recordings = db.query(Recording).filter(
        Recording.user_id == current_user.id,
        Recording.deleted_at.is_(None)
    ).count()

    # Recordings this week
    week_ago = datetime.utcnow() - timedelta(days=7)
    recordings_this_week = db.query(Recording).filter(
        Recording.user_id == current_user.id,
        Recording.created_at >= week_ago,
        Recording.deleted_at.is_(None)
    ).count()

    # Active matches (leads with status: new or in_progress)
    active_leads = db.query(Lead).join(Recording).filter(
        Recording.user_id == current_user.id,
        Lead.status.in_(["new", "in_progress", "contacted"])
    ).count()

    # New leads this week
    new_leads_this_week = db.query(Lead).join(Recording).filter(
        Recording.user_id == current_user.id,
        Lead.created_at >= week_ago
    ).count()

    # Events found
    total_events = db.query(Event).filter(
        Event.user_id == current_user.id
    ).count()

    # New events this week
    new_events_this_week = db.query(Event).filter(
        Event.user_id == current_user.id,
        Event.created_at >= week_ago
    ).count()

    # Completed action items (connections made)
    completed_actions = db.query(ActionItem).join(Recording).filter(
        Recording.user_id == current_user.id,
        ActionItem.status == "completed"
    ).count()

    # Action items completed this week
    actions_completed_this_week = db.query(ActionItem).join(Recording).filter(
        Recording.user_id == current_user.id,
        ActionItem.status == "completed",
        ActionItem.completed_at >= week_ago
    ).count()

    return {
        "recordings": {
            "total": total_recordings,
            "this_week": recordings_this_week,
            "change": f"+{recordings_this_week} this week"
        },
        "leads": {
            "total": active_leads,
            "this_week": new_leads_this_week,
            "change": f"+{new_leads_this_week} new"
        },
        "events": {
            "total": total_events,
            "this_week": new_events_this_week,
            "change": f"+{new_events_this_week} new"
        },
        "connections": {
            "total": completed_actions,
            "this_week": actions_completed_this_week,
            "change": f"+{actions_completed_this_week} this week"
        }
    }


@router.get("/activity")
async def get_recent_activity(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get recent activity for the dashboard
    Shows recent recordings, leads generated, events found, etc.
    """
    activities = []

    # Recent recordings processed
    recent_recordings = db.query(Recording).filter(
        Recording.user_id == current_user.id,
        Recording.status == "completed",
        Recording.deleted_at.is_(None)
    ).order_by(Recording.processing_completed_at.desc()).limit(3).all()

    for rec in recent_recordings:
        # Count leads for this recording
        leads_count = db.query(Lead).filter(Lead.recording_id == rec.id).count()

        if leads_count > 0:
            activities.append({
                "id": f"recording_{rec.id}",
                "agent": "Lakshya",
                "icon": "💼",
                "action": f"Found {leads_count} new lead{'s' if leads_count != 1 else ''}",
                "target": f"from {rec.title}",
                "time": _format_time_ago(rec.processing_completed_at),
                "color": "text-orange-600",
                "timestamp": rec.processing_completed_at.isoformat() if rec.processing_completed_at else None
            })
        else:
            activities.append({
                "id": f"recording_processed_{rec.id}",
                "agent": "Dhwani",
                "icon": "🎙️",
                "action": "Processed recording",
                "target": rec.title,
                "time": _format_time_ago(rec.processing_completed_at),
                "color": "text-purple-600",
                "timestamp": rec.processing_completed_at.isoformat() if rec.processing_completed_at else None
            })

    # Recent events discovered
    recent_events = db.query(Event).filter(
        Event.user_id == current_user.id
    ).order_by(Event.created_at.desc()).limit(2).all()

    for event in recent_events:
        activities.append({
            "id": f"event_{event.id}",
            "agent": "Arya",
            "icon": "🎯",
            "action": "Discovered event",
            "target": event.title,
            "time": _format_time_ago(event.created_at),
            "color": "text-blue-600",
            "timestamp": event.created_at.isoformat()
        })

    # Recent action items completed
    recent_actions = db.query(ActionItem).join(Recording).filter(
        Recording.user_id == current_user.id,
        ActionItem.status == "completed"
    ).order_by(ActionItem.completed_at.desc()).limit(2).all()

    for action in recent_actions:
        activities.append({
            "id": f"action_{action.id}",
            "agent": "You",
            "icon": "✅",
            "action": "Completed action",
            "target": action.action[:50] + "..." if len(action.action) > 50 else action.action,
            "time": _format_time_ago(action.completed_at),
            "color": "text-green-600",
            "timestamp": action.completed_at.isoformat() if action.completed_at else None
        })

    # Sort all activities by timestamp (most recent first)
    activities.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

    return activities[:limit]


def _format_time_ago(dt: datetime) -> str:
    """Format datetime as 'X ago' string"""
    if not dt:
        return "unknown"

    now = datetime.utcnow()
    diff = now - dt

    if diff.days > 0:
        if diff.days == 1:
            return "1 day ago"
        return f"{diff.days} days ago"

    hours = diff.seconds // 3600
    if hours > 0:
        if hours == 1:
            return "1 hour ago"
        return f"{hours} hours ago"

    minutes = diff.seconds // 60
    if minutes > 0:
        if minutes == 1:
            return "1 minute ago"
        return f"{minutes} minutes ago"

    return "just now"