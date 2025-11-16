"""
Lead Generation Service - Lakshya Agent Integration
Processes transcripts to extract leads and opportunities
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.models.database import Recording, Transcript, Lead, LeadGenerationJob

# Import the Lyncsea Crew from lyncsea_agents module
# Since we run from backend/, we don't need 'backend.' prefix
from lyncsea_agents.lead_generator import LyncseaCrew

logger = logging.getLogger(__name__)


class LeadGenerationService:
    """Service for generating leads from transcripts using Lakshya agent"""

    def __init__(self):
        self.crew = LyncseaCrew()

    def generate_leads_from_transcript(
        self,
        recording_id: int,
        recipient_email: str,
        db: Session
    ) -> Dict[str, Any]:
        """
        Generate leads from a recording's transcript

        Args:
            recording_id: ID of the recording
            recipient_email: Email to send lead report to
            db: Database session

        Returns:
            Dictionary with lead generation results
        """
        # Get recording and transcript
        recording = db.query(Recording).filter(Recording.id == recording_id).first()
        if not recording:
            raise ValueError(f"Recording {recording_id} not found")

        if not recording.transcript:
            raise ValueError(f"Recording {recording_id} has no transcript. Process it first.")

        transcript = recording.transcript

        # Create temporary transcript file for the crew
        temp_dir = Path("temp_transcripts")
        temp_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        transcript_file = temp_dir / f"transcript_{recording_id}_{timestamp}.txt"

        # Write full transcript with speaker labels
        with open(transcript_file, 'w') as f:
            f.write(f"Recording: {recording.title}\n")
            f.write(f"Date: {recording.created_at}\n")
            f.write(f"Duration: {recording.duration_seconds}s\n")
            f.write("\n" + "="*80 + "\n\n")

            # Write segments with speakers
            for seg in sorted(transcript.segments, key=lambda x: x.sequence_number):
                f.write(f"[{seg.speaker_id}] ({seg.start_time:.1f}s - {seg.end_time:.1f}s):\n")
                f.write(f"{seg.text}\n\n")

        # Create job record
        job = LeadGenerationJob(
            recording_id=recording_id,
            status="running",
            started_at=datetime.utcnow()
        )
        db.add(job)
        db.commit()
        db.refresh(job)

        logger.info(f"Running Lakshya for recording {recording_id}, job {job.id}")

        try:
            # Run the Lyncsea Crew
            result = self.crew.run(
                transcript_file=str(transcript_file),
                recipient_email=recipient_email
            )

            # Parse the leads data that was saved
            # Leads are now in data/leads/ directory
            project_root = Path(__file__).parent.parent.parent.parent
            leads_dir = project_root / "data" / "leads"
            latest_leads_file = max(leads_dir.glob("leads_*.json"), key=os.path.getctime)

            with open(latest_leads_file, 'r') as f:
                leads_data = json.load(f)

            # Upload JSON to S3 (if S3 storage is enabled)
            from app.services.storage import get_storage_service
            from app.core.config import settings
            if settings.STORAGE_TYPE == "s3":
                # Get user_id from recording
                recording = db.query(Recording).filter(Recording.id == recording_id).first()
                if recording:
                    storage = get_storage_service("s3")
                    filename = f"leads_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
                    with open(latest_leads_file, 'rb') as f:
                        s3_path = storage.save_file(f, filename, user_id=recording.user_id, data_type="leads")
                    logger.info(f"Leads JSON uploaded to S3: {s3_path}")

                    # Delete local file after S3 upload
                    os.remove(latest_leads_file)
                    logger.info(f"Local leads file deleted: {latest_leads_file}")

            # Clear old leads for this recording
            db.query(Lead).filter(Lead.recording_id == recording_id).delete()

            # Save leads to database with new schema
            for lead_item in leads_data.get("leads", []):
                lead = Lead(
                    recording_id=recording_id,
                    name=lead_item.get("name", "Unknown"),
                    company=lead_item.get("company"),
                    role=lead_item.get("role"),
                    opportunity_type=lead_item.get("opportunity_type", lead_item.get("type")),
                    opportunity_description=lead_item.get("opportunity", ""),
                    priority=lead_item.get("priority", "medium"),
                    linkedin_url=lead_item.get("linkedin"),
                    email=lead_item.get("email"),
                    company_website=lead_item.get("website"),
                    notes="",
                    status="new"
                )
                db.add(lead)

            db.commit()

            # Update job
            job.status = "completed"
            job.leads_found = len(leads_data.get("leads", []))
            job.email_sent = True
            job.completed_at = datetime.utcnow()
            db.commit()

            # Clean up temp file
            transcript_file.unlink()

            logger.info(f"Lead generation completed for recording {recording_id}. Found {job.leads_found} leads")

            return {
                "success": True,
                "job_id": job.id,
                "recording_id": recording_id,
                "leads_count": job.leads_found,
                "opportunities_count": len(leads_data.get("opportunities", [])),
                "email_sent_to": recipient_email,
                "message": f"Found {job.leads_found} leads and sent email report"
            }

        except Exception as e:
            logger.error(f"Lead generation failed: {e}", exc_info=True)

            # Update job as failed
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            db.commit()

            # Clean up temp file
            if transcript_file.exists():
                transcript_file.unlink()

            return {
                "success": False,
                "job_id": job.id,
                "error": str(e),
                "message": "Lead generation failed"
            }


def get_lead_generation_service() -> LeadGenerationService:
    """Get lead generation service instance"""
    return LeadGenerationService()