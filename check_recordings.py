#!/usr/bin/env python3
"""
Diagnostic script to check recent recordings and their processing status
"""
import sys
sys.path.insert(0, '/home/ec2-user/lead_gen_agent_locally/backend')

from app.core.database import SessionLocal
from app.models.database import Recording, Transcript, Lead, LeadGenerationJob

def main():
    db = SessionLocal()

    print("\n" + "="*80)
    print("LYNCSEA RECORDING DIAGNOSTICS")
    print("="*80)

    # Get latest 5 recordings
    recordings = db.query(Recording).order_by(Recording.created_at.desc()).limit(5).all()

    if not recordings:
        print("\n❌ No recordings found in database")
        return

    print(f"\nFound {len(recordings)} recent recordings:\n")

    for i, rec in enumerate(recordings, 1):
        print(f"\n{'─'*80}")
        print(f"#{i} Recording ID: {rec.id}")
        print(f"    Title: {rec.title}")
        print(f"    Status: {rec.status}")
        print(f"    Created: {rec.created_at}")
        print(f"    File: {rec.file_path}")

        if rec.error_message:
            print(f"    ❌ Error: {rec.error_message}")

        # Check transcript
        if rec.transcript:
            trans_len = len(rec.transcript.full_text)
            print(f"    ✅ Transcript: {trans_len} characters")
            print(f"       Language: {rec.transcript.language}")
            print(f"       Segments: {len(rec.transcript.segments)}")
            if trans_len > 0:
                preview = rec.transcript.full_text[:150].replace('\n', ' ')
                print(f"       Preview: {preview}...")
            else:
                print(f"       ⚠️  WARNING: Transcript exists but is EMPTY!")
        else:
            print("    ❌ NO TRANSCRIPT")

        # Check leads
        leads = db.query(Lead).filter(Lead.recording_id == rec.id).all()
        if leads:
            print(f"    ✅ Leads: {len(leads)} found")
            for lead in leads[:3]:  # Show first 3
                print(f"       - {lead.name} ({lead.company or 'No company'})")
        else:
            print("    ❌ NO LEADS")

        # Check lead generation job
        job = db.query(LeadGenerationJob).filter(
            LeadGenerationJob.recording_id == rec.id
        ).order_by(LeadGenerationJob.created_at.desc()).first()

        if job:
            print(f"    Lead Job Status: {job.status}")
            if job.error_message:
                print(f"       ❌ Job Error: {job.error_message}")
            if job.email_sent:
                print(f"       ✅ Email sent")
        else:
            print("    ⚠️  No lead generation job")

    print(f"\n{'='*80}\n")
    db.close()

if __name__ == "__main__":
    main()