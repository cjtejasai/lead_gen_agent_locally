"""
SQLAlchemy database models for Lyncsea platform
Clean, modular design with proper relationships
"""

from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Float, DateTime,
    ForeignKey, Enum as SQLEnum, JSON
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class ProcessingStatus(str, enum.Enum):
    """Recording processing status"""
    PENDING = "pending"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"


class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    recordings = relationship("Recording", back_populates="user", cascade="all, delete-orphan")
    user_profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")


class UserProfile(Base):
    """User profile for event discovery"""
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    company = Column(String(255))
    role = Column(String(255))
    location = Column(String(255))
    interests = Column(JSON)  # Array of interests
    hobbies = Column(JSON)
    looking_for = Column(JSON)
    event_preferences = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="user_profile")


class Recording(Base):
    """Audio recording model"""
    __tablename__ = "recordings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255))
    file_path = Column(String(500), nullable=False)  # Local path or S3 URL
    duration_seconds = Column(Integer)
    file_size_bytes = Column(Integer)
    status = Column(SQLEnum(ProcessingStatus, values_callable=lambda x: [e.value for e in x]), default=ProcessingStatus.PENDING)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    processing_started_at = Column(DateTime)
    processing_completed_at = Column(DateTime)
    deleted_at = Column(DateTime, nullable=True)  # Soft delete timestamp

    # Relationships
    user = relationship("User", back_populates="recordings")
    transcript = relationship("Transcript", back_populates="recording", uselist=False, cascade="all, delete-orphan")
    speakers = relationship("Speaker", back_populates="recording", cascade="all, delete-orphan")


class Transcript(Base):
    """Transcript model"""
    __tablename__ = "transcripts"

    id = Column(Integer, primary_key=True, index=True)
    recording_id = Column(Integer, ForeignKey("recordings.id"), unique=True, nullable=False)
    full_text = Column(Text, nullable=False)
    language = Column(String(10), default="en")
    confidence_score = Column(Float)
    word_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    recording = relationship("Recording", back_populates="transcript")
    segments = relationship("TranscriptSegment", back_populates="transcript", cascade="all, delete-orphan")


class TranscriptSegment(Base):
    """Individual transcript segment (with speaker)"""
    __tablename__ = "transcript_segments"

    id = Column(Integer, primary_key=True, index=True)
    transcript_id = Column(Integer, ForeignKey("transcripts.id"), nullable=False)
    speaker_id = Column(String(50))  # SPEAKER_00, SPEAKER_01, etc.
    text = Column(Text, nullable=False)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    confidence = Column(Float)
    sequence_number = Column(Integer, nullable=False)

    # Relationships
    transcript = relationship("Transcript", back_populates="segments")


class Speaker(Base):
    """Detected speaker in recording"""
    __tablename__ = "speakers"

    id = Column(Integer, primary_key=True, index=True)
    recording_id = Column(Integer, ForeignKey("recordings.id"), nullable=False)
    speaker_label = Column(String(50), nullable=False)  # SPEAKER_00, etc.
    identified_name = Column(String(255))  # Extracted from conversation
    segment_count = Column(Integer, default=0)
    total_speaking_time = Column(Float, default=0.0)

    # Relationships
    recording = relationship("Recording", back_populates="speakers")


class ProcessingJob(Base):
    """Background job tracking"""
    __tablename__ = "processing_jobs"

    id = Column(Integer, primary_key=True, index=True)
    recording_id = Column(Integer, ForeignKey("recordings.id"), nullable=False)
    job_type = Column(String(50), nullable=False)  # transcription, diarization, lead_extraction
    celery_task_id = Column(String(255), unique=True)
    status = Column(String(50), default="queued")
    progress_percentage = Column(Integer, default=0)
    error_message = Column(Text)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


class Event(Base):
    """Event discovered by AI agent"""
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    url = Column(String(1000))
    date = Column(String(255))  # Can be "Dec 15-17" or "Next Week" from agent
    location = Column(String(500))
    event_type = Column(String(100))  # conference, meetup, workshop, etc.
    relevance_score = Column(Float)  # How relevant to user's interests (0-100)
    relevance_reason = Column(Text)  # Why this event matches the user
    source = Column(String(255))  # Where the event was found
    matched_interests = Column(JSON)  # Array of user interests that matched
    exhibitors = Column(JSON)  # List of companies exhibiting at the event
    is_saved = Column(Boolean, default=False)
    is_attending = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User")


class EventDiscoveryJob(Base):
    """Track event discovery agent runs"""
    __tablename__ = "event_discovery_jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    events_found = Column(Integer, default=0)
    error_message = Column(Text)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User")


class Lead(Base):
    """Lead generated from conversation transcript"""
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    recording_id = Column(Integer, ForeignKey("recordings.id"), nullable=False)
    name = Column(String(255), nullable=False)
    company = Column(String(255))
    role = Column(String(255))
    opportunity_type = Column(String(100))  # investment, partnership, hiring, etc.
    opportunity_description = Column(Text)
    priority = Column(String(50))  # high, medium, low
    linkedin_url = Column(String(500))
    email = Column(String(255))
    company_website = Column(String(500))
    notes = Column(Text)
    status = Column(String(50), default="new")  # new, contacted, in_progress, closed
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    recording = relationship("Recording")


class LeadGenerationJob(Base):
    """Track lead generation agent runs"""
    __tablename__ = "lead_generation_jobs"

    id = Column(Integer, primary_key=True, index=True)
    recording_id = Column(Integer, ForeignKey("recordings.id"), nullable=False)
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    leads_found = Column(Integer, default=0)
    error_message = Column(Text)
    email_sent = Column(Boolean, default=False)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    recording = relationship("Recording")