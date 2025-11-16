"""
Recording API endpoints - Clean, modular implementation
"""

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status, BackgroundTasks
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

# Get storage service from settings (local or s3)
storage = get_storage_service(settings.STORAGE_TYPE)


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
        file_path = storage.save_file(file.file, filename, user_id=current_user.id)

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
    """List recordings for the current authenticated user (excluding soft-deleted)"""
    recordings = db.query(Recording).filter(
        Recording.user_id == current_user.id,
        Recording.deleted_at.is_(None)  # Exclude soft-deleted recordings
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
    """
    Smart delete: Soft delete for processed recordings, hard delete for unprocessed
    - If recording has leads/transcripts → Soft delete (restorable)
    - If recording is unprocessed → Hard delete (permanent)
    """
    from app.models.database import Lead, LeadGenerationJob, Transcript, TranscriptSegment

    recording = db.query(Recording).filter(Recording.id == recording_id).first()

    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")

    try:
        # Check if recording has processed data
        has_leads = db.query(Lead).filter(Lead.recording_id == recording_id).count() > 0
        has_transcript = recording.transcript is not None

        if has_leads or has_transcript:
            # SOFT DELETE - Recording has valuable processed data
            recording.deleted_at = datetime.utcnow()
            db.commit()

            logger.info(f"Recording soft-deleted: ID={recording_id} (has processed data, restorable)")
            return {
                "message": "Recording archived (soft deleted)",
                "type": "soft_delete",
                "restorable": True,
                "reason": "Recording has processed data (leads/transcripts)"
            }
        else:
            # HARD DELETE - Unprocessed recording, safe to permanently delete

            # 1. Delete lead generation jobs (if any)
            db.query(LeadGenerationJob).filter(LeadGenerationJob.recording_id == recording_id).delete()

            # 2. Delete file from storage
            storage.delete_file(recording.file_path)

            # 3. Delete recording from database
            db.delete(recording)
            db.commit()

            logger.info(f"Recording hard-deleted: ID={recording_id} (no processed data)")
            return {
                "message": "Recording permanently deleted",
                "type": "hard_delete",
                "restorable": False,
                "reason": "Recording had no processed data"
            }

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete recording {recording_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete recording: {str(e)}")


def trigger_lead_generation(recording_id: int, user_email: str, db_session):
    """Background task to generate leads after transcription"""
    from app.services.lead_generation import get_lead_generation_service
    try:
        logger.info(f"Starting lead generation for recording {recording_id}")
        service = get_lead_generation_service()
        result = service.generate_leads_from_transcript(recording_id, user_email, db_session)

        # Update recording status to COMPLETED after lead generation
        recording = db_session.query(Recording).filter(Recording.id == recording_id).first()
        if recording:
            recording.status = ProcessingStatus.COMPLETED
            db_session.commit()
            logger.info(f"Lead generation completed for recording {recording_id}, status updated to COMPLETED")
    except Exception as e:
        logger.error(f"Lead generation failed for recording {recording_id}: {e}")
        # Update recording status to COMPLETED even if lead generation fails (transcript is still available)
        recording = db_session.query(Recording).filter(Recording.id == recording_id).first()
        if recording:
            recording.status = ProcessingStatus.COMPLETED
            db_session.commit()


@router.post("/{recording_id}/process")
async def process_recording(
    recording_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Process recording: Transcribe with Whisper and generate leads
    Runs transcription synchronously, then triggers lead generation in background
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

        # Handle S3 vs local storage
        if settings.STORAGE_TYPE == "s3":
            # For S3 storage, we need to handle differently based on STT provider
            if settings.STT_PROVIDER == "assemblyai":
                # AssemblyAI can transcribe from URL directly
                from app.services.speech_to_text import SpeechToTextService
                transcription_service = SpeechToTextService(provider=settings.STT_PROVIDER)
                audio_url = storage.get_file_url(recording.file_path, expiration=7200)  # 2 hour presigned URL
                logger.info(f"Transcribing from S3 presigned URL (AssemblyAI)")
                normalized_result = transcription_service.transcribe_from_url(
                    audio_url=audio_url,
                    speaker_diarization=settings.ENABLE_DIARIZATION
                )
            else:
                # For Whisper (OpenAI or local), download file to temp location first
                import tempfile
                import requests

                logger.info(f"Downloading S3 file to temporary location for {settings.STT_PROVIDER}")
                audio_url = storage.get_file_url(recording.file_path, expiration=7200)

                # Download to temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(recording.file_path)[1]) as tmp_file:
                    response = requests.get(audio_url, stream=True)
                    response.raise_for_status()
                    for chunk in response.iter_content(chunk_size=8192):
                        tmp_file.write(chunk)
                    temp_audio_path = tmp_file.name

                try:
                    if settings.STT_PROVIDER == "local_whisper":
                        from app.services.transcription import get_transcription_service
                        transcription_service = get_transcription_service(
                            model_size=settings.WHISPER_MODEL_SIZE,
                            enable_diarization=settings.ENABLE_DIARIZATION
                        )
                        result = transcription_service.transcribe(temp_audio_path)

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
                        # OpenAI Whisper API
                        from app.services.speech_to_text import SpeechToTextService
                        transcription_service = SpeechToTextService(provider=settings.STT_PROVIDER)
                        normalized_result = transcription_service.transcribe(
                            audio_file_path=temp_audio_path,
                            speaker_diarization=settings.ENABLE_DIARIZATION
                        )
                finally:
                    # Clean up temp file
                    if os.path.exists(temp_audio_path):
                        os.remove(temp_audio_path)
                        logger.info(f"Deleted temporary audio file: {temp_audio_path}")
        else:
            # Local storage - use file path directly
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
        recording.status = ProcessingStatus.ANALYZING  # Set to analyzing before lead generation
        recording.processing_completed_at = datetime.utcnow()
        recording.duration_seconds = int(normalized_result.get("duration_seconds", 0))

        db.commit()

        logger.info(f"Transcription completed for recording {recording_id}, starting lead generation...")

        # Trigger lead generation in background using FastAPI background tasks
        background_tasks.add_task(trigger_lead_generation, recording_id, current_user.email, db)

        return {
            "message": "Transcription completed, lead generation in progress",
            "recording_id": recording_id,
            "status": "analyzing",
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


@router.get("/{recording_id}/status")
async def get_recording_status(
    recording_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current processing status of a recording"""
    from app.models.database import LeadGenerationJob

    recording = db.query(Recording).filter(
        Recording.id == recording_id,
        Recording.user_id == current_user.id
    ).first()

    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")

    # Check lead generation job status
    lead_job = db.query(LeadGenerationJob).filter(
        LeadGenerationJob.recording_id == recording_id
    ).order_by(LeadGenerationJob.created_at.desc()).first()

    return {
        "recording_id": recording_id,
        "status": recording.status.value,
        "has_transcript": recording.transcript is not None,
        "has_leads": lead_job is not None and lead_job.status == "completed",
        "leads_count": lead_job.leads_found if lead_job else 0,
        "lead_job_status": lead_job.status if lead_job else None,
        "processing_started_at": recording.processing_started_at,
        "processing_completed_at": recording.processing_completed_at
    }


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