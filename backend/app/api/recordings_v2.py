"""
Recording API endpoints - Clean, modular implementation
"""

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import logging
import os

from app.core.database import get_db
from app.core.config import settings
from app.models.database import Recording, User, ProcessingStatus
from app.services.storage import get_storage_service
from app.models.schemas import RecordingResponse, RecordingUploadResponse
from app.services.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

# Get storage service
storage = get_storage_service("local")


@router.post("/upload", response_model=RecordingUploadResponse)
async def upload_recording(
    file: UploadFile = File(...),
    title: str = Form(None),
    event_date: str = Form(None),
    event_location: str = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload audio recording
    1. Validate file
    2. Save to storage with event_date_timestamp naming
    3. Create database record
    4. Return recording ID
    """
    logger.info(f"Upload request from user {current_user.id}: {file.filename}, size: {file.size}")
    logger.info(f"Event details - title: {title}, date: {event_date}, location: {event_location}")

    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    ext = os.path.splitext(file.filename)[1].lower()
    allowed = [".wav", ".mp3", ".m4a", ".flac", ".webm"]
    if ext not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"File type {ext} not allowed. Allowed: {allowed}"
        )

    try:
        # Create filename with event name, event date and timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Sanitize event name for filename (remove special characters, replace spaces with underscore)
        if title:
            safe_title = "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in title)
            safe_title = safe_title[:50]  # Limit length
        else:
            safe_title = "recording"

        # Use event_date if provided (format: YYYY-MM-DD -> YYYYMMDD)
        if event_date:
            try:
                # Parse and format event date
                event_date_formatted = event_date.replace("-", "")
                filename = f"{safe_title}_{event_date_formatted}_{timestamp}{ext}"
            except:
                # Fallback to title_timestamp if date parsing fails
                filename = f"{safe_title}_{timestamp}{ext}"
        else:
            filename = f"{safe_title}_{timestamp}{ext}"

        logger.info(f"Generated filename: {filename}")
        file_path = storage.save_file(file.file, filename)

        # Create database record with authenticated user
        recording = Recording(
            user_id=current_user.id,
            title=title or f"Recording {timestamp}",
            file_path=file_path,
            file_size_bytes=file.size,
            status=ProcessingStatus.PENDING
        )
        db.add(recording)
        db.commit()
        db.refresh(recording)

        logger.info(f"Recording saved: ID={recording.id}, path={file_path}")

        return RecordingUploadResponse(
            recording_id=recording.id,
            upload_url=storage.get_file_url(file_path),
            message="Recording uploaded successfully"
        )

    except Exception as e:
        db.rollback()
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[RecordingResponse])
async def list_recordings(
    skip: int = 0,
    limit: int = 100,  # Increased limit to show more recordings
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List recordings for the current authenticated user"""
    recordings = db.query(Recording).filter(
        Recording.user_id == current_user.id
    ).order_by(Recording.created_at.desc()).offset(skip).limit(limit).all()  # Order by most recent first

    return [
        RecordingResponse(
            id=r.id,
            user_id=r.user_id,
            title=r.title,
            file_url=storage.get_file_url(r.file_path),
            filename=os.path.basename(r.file_path) if r.file_path else "unknown",
            file_size=r.file_size_bytes or 0,
            status=r.status,
            created_at=r.created_at,
            processed_at=r.processing_completed_at,
            transcript=r.transcript.full_text if r.transcript else None,
            duration_seconds=r.duration_seconds
        )
        for r in recordings
    ]


@router.get("/{recording_id}", response_model=RecordingResponse)
async def get_recording(recording_id: int, db: Session = Depends(get_db)):
    """Get recording by ID"""
    recording = db.query(Recording).filter(Recording.id == recording_id).first()

    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")

    return RecordingResponse(
        id=recording.id,
        user_id=recording.user_id,
        title=recording.title,
        file_url=storage.get_file_url(recording.file_path),
        filename=os.path.basename(recording.file_path) if recording.file_path else "unknown",
        file_size=recording.file_size_bytes or 0,
        status=recording.status,
        created_at=recording.created_at,
        processed_at=recording.processing_completed_at,
        transcript=recording.transcript.full_text if recording.transcript else None,
        duration_seconds=recording.duration_seconds
    )


@router.delete("/{recording_id}")
async def delete_recording(recording_id: int, db: Session = Depends(get_db)):
    """Delete recording"""
    recording = db.query(Recording).filter(Recording.id == recording_id).first()

    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")

    # Delete file from storage
    storage.delete_file(recording.file_path)

    # Delete from database (cascade will handle related records)
    db.delete(recording)
    db.commit()

    logger.info(f"Recording deleted: ID={recording_id}")
    return {"message": "Recording deleted successfully"}


@router.post("/{recording_id}/process")
async def process_recording(recording_id: int, db: Session = Depends(get_db)):
    """
    Process recording: Transcribe with Whisper
    For now runs synchronously, TODO: Queue as Celery task for production
    """
    from app.models.database import Transcript, TranscriptSegment

    recording = db.query(Recording).filter(Recording.id == recording_id).first()

    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")

    if recording.status == ProcessingStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Recording already processed")

    try:
        # Update status to processing
        recording.status = ProcessingStatus.PROCESSING
        recording.processing_started_at = datetime.utcnow()
        db.commit()

        logger.info(f"Starting transcription for recording {recording_id}")
        logger.info(f"Using STT provider: {settings.STT_PROVIDER}")

        # Get audio file path
        audio_path = storage.get_full_path(recording.file_path)

        # Transcribe based on configured provider
        if settings.STT_PROVIDER == "local_whisper":
            # Use local Whisper + pyannote diarization
            from app.services.transcription import get_transcription_service
            transcription_service = get_transcription_service(
                model_size=settings.WHISPER_MODEL_SIZE,
                enable_diarization=settings.ENABLE_DIARIZATION
            )
            result = transcription_service.transcribe(audio_path)

            # Normalize result format from local Whisper
            normalized_result = {
                "full_transcript": result.get("text", ""),
                "segments": result.get("segments", []),
                "language": result.get("language", "en"),
                "confidence": 0.95,
                "duration_seconds": result.get("duration", 0),
                "num_speakers": len(set(seg.get("speaker", "SPEAKER_00") for seg in result.get("segments", [])))
            }
        else:
            # Use cloud API (AssemblyAI or OpenAI Whisper)
            from app.services.speech_to_text import SpeechToTextService
            transcription_service = SpeechToTextService(provider=settings.STT_PROVIDER)
            normalized_result = transcription_service.transcribe(
                audio_file_path=str(audio_path),
                speaker_diarization=settings.ENABLE_DIARIZATION
            )

        # Save transcript to database
        transcript = Transcript(
            recording_id=recording_id,
            full_text=normalized_result["full_transcript"],
            language=normalized_result["language"],
            confidence_score=normalized_result.get("confidence", 0.95),
            word_count=len(normalized_result["full_transcript"].split())
        )
        db.add(transcript)
        db.flush()  # Get transcript ID

        # Save segments with speaker info
        for idx, seg in enumerate(normalized_result["segments"]):
            # Handle both local Whisper and cloud API segment formats
            speaker_id = seg.get("speaker_id") or seg.get("speaker", "SPEAKER_00")
            text = seg.get("text", "")
            start = seg.get("start_time") or seg.get("start", 0)
            end = seg.get("end_time") or seg.get("end", 0)
            conf = seg.get("confidence", 0.95)

            segment = TranscriptSegment(
                transcript_id=transcript.id,
                speaker_id=speaker_id,
                text=text,
                start_time=start,
                end_time=end,
                confidence=conf,
                sequence_number=idx
            )
            db.add(segment)

        # Update recording
        recording.status = ProcessingStatus.COMPLETED
        recording.processing_completed_at = datetime.utcnow()
        recording.duration_seconds = int(normalized_result.get("duration_seconds", 0))

        db.commit()

        logger.info(f"Processing completed for recording {recording_id}")

        return {
            "message": "Processing completed successfully",
            "recording_id": recording_id,
            "status": "completed",
            "transcript_length": len(normalized_result["full_transcript"]),
            "num_segments": len(normalized_result["segments"]),
            "num_speakers": normalized_result.get("num_speakers", 1),
            "duration": normalized_result.get("duration_seconds", 0)
        }

    except Exception as e:
        recording.status = ProcessingStatus.FAILED
        recording.error_message = str(e)
        db.commit()

        logger.error(f"Processing failed for recording {recording_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@router.get("/{recording_id}/transcript")
async def get_transcript(recording_id: int, db: Session = Depends(get_db)):
    """Get transcript with segments for a recording"""
    from app.models.database import Transcript

    recording = db.query(Recording).filter(Recording.id == recording_id).first()

    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")

    if not recording.transcript:
        raise HTTPException(status_code=404, detail="Transcript not found. Process the recording first.")

    transcript = recording.transcript

    return {
        "recording_id": recording_id,
        "full_text": transcript.full_text,
        "language": transcript.language,
        "confidence_score": transcript.confidence_score,
        "word_count": transcript.word_count,
        "segments": [
            {
                "sequence": seg.sequence_number,
                "speaker": seg.speaker_id,
                "text": seg.text,
                "start_time": seg.start_time,
                "end_time": seg.end_time,
                "confidence": seg.confidence
            }
            for seg in sorted(transcript.segments, key=lambda x: x.sequence_number)
        ]
    }


@router.get("/{recording_id}/download")
async def download_recording(recording_id: int, db: Session = Depends(get_db)):
    """Download audio file"""
    recording = db.query(Recording).filter(Recording.id == recording_id).first()

    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")

    file_path = storage.get_full_path(recording.file_path)

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        filename=f"{recording.title}.wav",
        media_type="audio/wav"
    )