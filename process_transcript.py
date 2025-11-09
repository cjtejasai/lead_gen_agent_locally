#!/usr/bin/env python3
"""
Process a transcript file through the AI analysis pipeline

This demonstrates how to integrate the POC with your existing backend agents.

Usage:
    python process_transcript.py transcripts/transcript_20240108_143022.txt
"""

import sys
from pathlib import Path
from datetime import datetime
import json

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

try:
    from app.agents.orchestrator import AgentOrchestrator
    AGENTS_AVAILABLE = True
except ImportError as e:
    AGENTS_AVAILABLE = False
    print(f"Warning: Could not import agents: {e}")
    print("Make sure backend dependencies are installed.")


def extract_text_from_transcript(file_path: Path) -> str:
    """
    Extract spoken text from transcript file, removing timestamps

    Args:
        file_path: Path to transcript file

    Returns:
        Clean transcript text
    """
    with open(file_path, 'r') as f:
        content = f.read()

    # Extract lines with timestamps like "[14:30:25] spoken text"
    lines = content.split('\n')
    text_parts = []

    for line in lines:
        # Look for pattern [HH:MM:SS] text
        if line.startswith('[') and '] ' in line:
            try:
                # Extract text after timestamp
                text = line.split('] ', 1)[1]
                text_parts.append(text)
            except IndexError:
                continue

    return ' '.join(text_parts)


def analyze_transcript(transcript_path: str, user_category: str = "general"):
    """
    Analyze a transcript file using the AI pipeline

    Args:
        transcript_path: Path to transcript file
        user_category: User category (ceo_investor, student, general)
    """
    transcript_file = Path(transcript_path)

    if not transcript_file.exists():
        print(f"Error: File not found: {transcript_path}")
        return

    print("=" * 70)
    print(f"  Processing Transcript: {transcript_file.name}")
    print("=" * 70)

    # Extract text
    print("\n📄 Extracting text from transcript...")
    transcript_text = extract_text_from_transcript(transcript_file)

    if not transcript_text.strip():
        print("❌ No text found in transcript!")
        return

    print(f"✓ Extracted {len(transcript_text)} characters")
    print(f"\nPreview:\n{transcript_text[:200]}...\n")

    if not AGENTS_AVAILABLE:
        print("\n⚠️  AI agents not available (dependencies not installed)")
        print("   Saving extracted text only...\n")

        # Save extracted text
        output_file = Path("processed") / f"{transcript_file.stem}_extracted.txt"
        output_file.parent.mkdir(exist_ok=True)

        with open(output_file, 'w') as f:
            f.write(transcript_text)

        print(f"✓ Saved to: {output_file}")
        return

    # Run through AI pipeline
    print("🤖 Running AI analysis pipeline...")
    print(f"   User category: {user_category}\n")

    orchestrator = AgentOrchestrator()

    try:
        results = orchestrator.analyze_recording(
            transcript=transcript_text,
            user_category=user_category,
            parallel=True
        )

        print("=" * 70)
        print("  ANALYSIS RESULTS")
        print("=" * 70)

        # Display results
        print("\n📊 Content Analysis:")
        content_analysis = results.get("content_analysis", {})
        if content_analysis.get("success"):
            ca_results = content_analysis.get("results", {})

            # Topics
            topics = ca_results.get("topics", [])
            if topics:
                print("\n  Topics Discussed:")
                for i, topic in enumerate(topics[:5], 1):
                    print(f"    {i}. {topic.get('topic', 'N/A')} "
                          f"(relevance: {topic.get('relevance', 0):.2f})")

            # Key points
            key_points = ca_results.get("key_points", [])
            if key_points:
                print("\n  Key Points:")
                for i, point in enumerate(key_points[:3], 1):
                    print(f"    {i}. {point}")

        # Entities
        print("\n🏢 Extracted Entities:")
        entities_data = results.get("entities", {})
        if entities_data.get("success"):
            entities = entities_data.get("results", {}).get("entities", [])

            # Group by type
            entity_groups = {}
            for entity in entities:
                ent_type = entity.get("type", "OTHER")
                if ent_type not in entity_groups:
                    entity_groups[ent_type] = []
                entity_groups[ent_type].append(entity.get("value"))

            for ent_type, values in entity_groups.items():
                print(f"\n  {ent_type}:")
                for value in values[:5]:
                    print(f"    • {value}")

        # Intents
        print("\n🎯 User Intents:")
        intents_data = results.get("intents", {})
        if intents_data.get("success"):
            intent_results = intents_data.get("results", {})

            looking_for = intent_results.get("looking_for", [])
            if looking_for:
                print("\n  Looking For:")
                for intent in looking_for[:5]:
                    print(f"    • {intent.get('intent_type', 'N/A')} "
                          f"(confidence: {intent.get('confidence', 0):.2f})")

            offering = intent_results.get("offering", [])
            if offering:
                print("\n  Can Offer:")
                for intent in offering[:5]:
                    print(f"    • {intent.get('intent_type', 'N/A')} "
                          f"(confidence: {intent.get('confidence', 0):.2f})")

        # Metadata
        print("\n📈 Processing Stats:")
        metadata = results.get("metadata", {})
        print(f"  User Category: {metadata.get('user_category', 'N/A')}")
        print(f"  Transcript Length: {metadata.get('transcript_length', 0)} chars")
        print(f"  Processing Time: {metadata.get('total_processing_time', 0):.2f}s")

        # Generate summary
        print("\n📝 Summary:")
        summary = orchestrator.generate_summary(results)
        print(f"  {summary}")

        # Save results
        output_dir = Path("processed")
        output_dir.mkdir(exist_ok=True)

        # Save JSON results
        json_file = output_dir / f"{transcript_file.stem}_analysis.json"
        with open(json_file, 'w') as f:
            json.dump(results, f, indent=2)

        # Save text summary
        summary_file = output_dir / f"{transcript_file.stem}_summary.txt"
        with open(summary_file, 'w') as f:
            f.write(f"Analysis Summary\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Source: {transcript_file.name}\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"{summary}\n\n")
            f.write("See {}_analysis.json for detailed results.\n".format(transcript_file.stem))

        print("\n" + "=" * 70)
        print("  OUTPUT FILES")
        print("=" * 70)
        print(f"\n  📄 Full results: {json_file}")
        print(f"  📝 Summary: {summary_file}")
        print("\n" + "=" * 70)

    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()


def main():
    if len(sys.argv) < 2:
        print("Usage: python process_transcript.py <transcript_file> [user_category]")
        print("\nExample:")
        print("  python process_transcript.py transcripts/transcript_20240108_143022.txt")
        print("  python process_transcript.py transcripts/transcript_20240108_143022.txt student")
        print("\nUser categories: general, ceo_investor, student")
        sys.exit(1)

    transcript_path = sys.argv[1]
    user_category = sys.argv[2] if len(sys.argv) > 2 else "general"

    analyze_transcript(transcript_path, user_category)


if __name__ == "__main__":
    main()