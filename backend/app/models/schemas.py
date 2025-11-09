from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class UserCategory(str, Enum):
    """User categories for matching"""
    CEO_INVESTOR = "ceo_investor"
    STUDENT = "student"
    GENERAL = "general"


class ProcessingStatus(str, Enum):
    """Recording processing status"""
    PENDING = "pending"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"


class IntentType(str, Enum):
    """Types of user intentions"""
    INVESTMENT = "investment"
    PARTNERSHIP = "partnership"
    HIRING = "hiring"
    LEARNING = "learning"
    MENTORSHIP = "mentorship"
    COLLABORATION = "collaboration"
    NETWORKING = "networking"
    SELLING = "selling"
    BUYING = "buying"
    OTHER = "other"


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    category: UserCategory
    company: Optional[str] = None
    title: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


# Recording Schemas
class RecordingBase(BaseModel):
    title: str
    event_name: Optional[str] = None
    event_date: Optional[datetime] = None
    event_location: Optional[str] = None
    duration_seconds: Optional[int] = None


class RecordingCreate(RecordingBase):
    pass


class RecordingResponse(RecordingBase):
    id: int
    user_id: int
    file_url: str
    file_size: int
    status: ProcessingStatus
    created_at: datetime
    processed_at: Optional[datetime] = None
    transcript: Optional[str] = None

    class Config:
        from_attributes = True


class RecordingUploadResponse(BaseModel):
    recording_id: int
    upload_url: str
    message: str


# Transcript Schemas
class SpeakerSegment(BaseModel):
    speaker_id: str
    text: str
    start_time: float
    end_time: float
    confidence: float


class TranscriptResponse(BaseModel):
    recording_id: int
    full_transcript: str
    segments: List[SpeakerSegment]
    num_speakers: int
    language: str
    confidence: float


# Analysis Schemas
class ExtractedEntity(BaseModel):
    type: str  # person, company, location, etc.
    value: str
    confidence: float
    context: Optional[str] = None


class ExtractedInterest(BaseModel):
    topic: str
    category: str
    relevance_score: float
    mentions: int


class ExtractedIntent(BaseModel):
    intent_type: IntentType
    description: str
    confidence: float
    supporting_evidence: List[str]


class AnalysisResponse(BaseModel):
    recording_id: int
    entities: List[ExtractedEntity]
    interests: List[ExtractedInterest]
    intents: List[ExtractedIntent]
    key_topics: List[str]
    pain_points: List[str]
    offerings: List[str]
    sentiment: str  # positive, neutral, negative
    summary: str
    processed_at: datetime


# Graph Node Schemas (for Neo4j)
class PersonNode(BaseModel):
    name: str
    category: UserCategory
    company: Optional[str] = None
    title: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class InterestNode(BaseModel):
    topic: str
    domain: str
    description: Optional[str] = None


class NeedNode(BaseModel):
    need_type: IntentType
    description: str
    urgency: str  # high, medium, low


class OfferingNode(BaseModel):
    offering_type: str
    description: str
    value_proposition: Optional[str] = None


# Match Schemas
class MatchScore(BaseModel):
    total_score: float = Field(..., ge=0, le=100)
    interest_overlap: float = Field(..., ge=0, le=100)
    complementary_needs: float = Field(..., ge=0, le=100)
    category_fit: float = Field(..., ge=0, le=100)
    context_relevance: float = Field(..., ge=0, le=100)


class MatchResponse(BaseModel):
    id: int
    user_id: int
    matched_user_id: int
    matched_user_name: str
    matched_user_category: UserCategory
    matched_user_company: Optional[str]
    score: MatchScore
    reason: str
    common_interests: List[str]
    complementary_areas: List[str]
    suggested_topics: List[str]
    confidence: float
    created_at: datetime
    status: str  # new, contacted, scheduled, completed, dismissed


class MatchFeedResponse(BaseModel):
    matches: List[MatchResponse]
    total: int
    page: int
    page_size: int


# Calendar Integration Schemas
class MeetingScheduleRequest(BaseModel):
    match_id: int
    title: str
    description: Optional[str] = None
    duration_minutes: int = 30
    proposed_times: List[datetime]


class MeetingScheduleResponse(BaseModel):
    meeting_id: str
    match_id: int
    calendar_event_id: str
    meeting_link: str
    scheduled_time: datetime
    status: str  # scheduled, completed, cancelled


# Dashboard Analytics Schemas
class UserStats(BaseModel):
    total_recordings: int
    total_processing_time: int  # in seconds
    total_matches: int
    matches_by_category: Dict[str, int]
    top_interests: List[Dict[str, Any]]
    recent_activity: List[Dict[str, Any]]


# Agent Response Schemas (for LLM agents)
class AgentAnalysisResponse(BaseModel):
    agent_name: str
    analysis_type: str
    results: Dict[str, Any]
    confidence: float
    processing_time: float
    model_used: str


# Error Schemas
class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
