"""
Recording API endpoints - Clean, modular implementation
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import logging
import os

from app.core.database import get_db
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
    title: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload audio recording
    1. Validate file
    2. Save to storage
    3. Create database record
    4. Return recording ID
    """
    logger.info(f"Upload request from user {current_user.id}: {file.filename}, size: {file.size}")

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
        # Save file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recording_{timestamp}{ext}"
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
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List recordings for the current authenticated user"""
    recordings = db.query(Recording).filter(
        Recording.user_id == current_user.id
    ).offset(skip).limit(limit).all()

    return [
        RecordingResponse(
            id=r.id,
            user_id=r.user_id,
            title=r.title,
            file_url=storage.get_file_url(r.file_path),
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
    from app.services.transcription import get_transcription_service

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

        # Get audio file path
        audio_path = storage.get_full_path(recording.file_path)

        # Transcribe with Whisper
        transcription_service = get_transcription_service(model_size="base")
        result = transcription_service.transcribe(audio_path)

        # Save transcript to database
        transcript = Transcript(
            recording_id=recording_id,
            full_text=result["text"],
            language=result["language"],
            confidence_score=0.95,  # Whisper doesn't provide overall confidence
            word_count=len(result["text"].split())
        )
        db.add(transcript)
        db.flush()  # Get transcript ID

        # Save segments
        for idx, seg in enumerate(result["segments"]):
            segment = TranscriptSegment(
                transcript_id=transcript.id,
                speaker_id="SPEAKER_00",  # No diarization yet
                text=seg["text"],
                start_time=seg["start"],
                end_time=seg["end"],
                confidence=1.0 - seg.get("confidence", 0.0),
                sequence_number=idx
            )
            db.add(segment)

        # Update recording
        recording.status = ProcessingStatus.COMPLETED
        recording.processing_completed_at = datetime.utcnow()
        recording.duration_seconds = int(result["duration"])

        db.commit()

        logger.info(f"Processing completed for recording {recording_id}")

        return {
            "message": "Processing completed successfully",
            "recording_id": recording_id,
            "status": "completed",
            "transcript_length": len(result["text"]),
            "num_segments": len(result["segments"]),
            "duration": result["duration"]
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