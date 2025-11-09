# How Audio Recording & Storage Works

## Current System Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      YOUR MICROPHONE/HEADSET                     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Real-time audio stream
                             │ (16kHz, mono)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   AUDIO CALLBACK (Every ~1ms)                    │
│  File: audio_recorder_whisper.py:56                             │
│  - Captures small chunks of audio                               │
│  - Puts them in a queue                                         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Queued audio chunks
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AUDIO QUEUE (In Memory)                       │
│  - Temporary storage                                            │
│  - Holds audio until processed                                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Every 5 seconds
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              TRANSCRIPTION WORKER THREAD                         │
│  File: audio_recorder_whisper.py:63                             │
│                                                                  │
│  1. Collect 5 seconds of audio chunks                           │
│  2. Convert to float32 format                                   │
│  3. Send to Whisper model                                       │
│  4. Get back transcribed text                                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Transcribed text
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    IMMEDIATE FILE WRITE                          │
│  File: audio_recorder_whisper.py:120                            │
│  Location: transcripts/transcript_whisper_YYYYMMDD_HHMMSS.txt   │
│                                                                  │
│  Format:                                                        │
│  [18:33:03] Hi, how are you?                                    │
│  [18:33:10] This is what I said next.                           │
│                                                                  │
│  ✓ WRITTEN TO DISK IMMEDIATELY (not buffered)                   │
└─────────────────────────────────────────────────────────────────┘
```

## Storage Details

### Where Data is Stored

1. **Transcripts** → `transcripts/transcript_whisper_YYYYMMDD_HHMMSS.txt`
   - Plain text file
   - One line per transcribed chunk
   - Includes timestamp
   - Written immediately (line 120 in audio_recorder_whisper.py)

2. **Raw Audio** (optional) → `recordings/session_YYYYMMDD_HHMMSS.wav`
   - Only saved in speaker detection version
   - Full WAV file
   - 16kHz, mono, 16-bit
   - Saved at end of session

### When Data is Written

```python
# From audio_recorder_whisper.py lines 92-137

while is_recording:
    # 1. Collect audio for 5 seconds
    chunk = audio_queue.get(timeout=1)
    audio_chunks.append(chunk)

    # 2. Every 5 seconds, process
    if len(audio_chunks) >= int(CHUNK_DURATION * SAMPLE_RATE / 1024):
        audio_data = np.concatenate(audio_chunks)

        # 3. Transcribe
        result = model.transcribe(audio_float, language="en")
        text = result["text"].strip()

        # 4. WRITE TO FILE IMMEDIATELY
        with open(session_file, 'a') as f:  # 'a' = append mode
            f.write(f"[{timestamp}] {text}\n")
        # ✓ Data is now on disk! Safe even if program crashes
```

## Problem: No Speaker Detection

### Current System (All Speakers Mixed)

```
Recording:
Person 1: "Hi, I'm looking for investors"
Person 2: "I'm an investor, what's your startup?"
Person 1: "We're building AI tools"

Current Output:
[18:33:03] Hi, I'm looking for investors
[18:33:10] I'm an investor, what's your startup?
[18:33:15] We're building AI tools

❌ NO IDEA who said what!
```

### With Speaker Detection (New Script)

```
Recording:
Person 1: "Hi, I'm looking for investors"
Person 2: "I'm an investor, what's your startup?"
Person 1: "We're building AI tools"

New Output:
[Speaker 1] [18:33:03]
Hi, I'm looking for investors

[Speaker 2] [18:33:10]
I'm an investor, what's your startup?

[Speaker 1] [18:33:15]
We're building AI tools

✓ Knows who said what!
```

## How Speaker Detection Works

### Method 1: Simple Energy-Based (Current Implementation)

```python
def simple_speaker_detection(audio_data):
    # Split into 250ms segments
    # Measure volume/energy of each segment
    # Detect sudden changes → potential speaker change

    energies = [volume_of(segment) for segment in segments]

    # Big change in volume = different speaker
    if abs(energies[i] - energies[i-1]) > threshold:
        speaker_changed = True
```

**Pros**: Works offline, fast, no extra dependencies
**Cons**: Not very accurate, confused by volume changes

### Method 2: ML-Based Diarization (Better, but requires pyannote.audio)

```bash
# Install advanced speaker detection
pip install pyannote.audio

# Then run
python audio_recorder_with_speakers.py
```

Uses AI to detect:
- Voice characteristics
- Speaking patterns
- Unique voice features
- Accurate speaker labels

## File Structure

```
ayka_lead_gen/
├── transcripts/                          # Text transcripts
│   ├── transcript_whisper_20251108_183303.txt
│   └── transcript_speakers_20251108_184521.txt
│
├── recordings/                           # Audio files
│   └── session_20251108_184521.wav
│
└── processed/                            # After AI analysis
    ├── transcript_20251108_183303_analysis.json
    └── transcript_20251108_183303_summary.txt
```

## Complete Data Pipeline

```
1. CAPTURE
   Bluetooth Headset → audio_recorder_with_speakers.py
   Output: transcripts/transcript_speakers_YYYYMMDD_HHMMSS.txt

2. TRANSCRIBE (Real-time, every 5-10 seconds)
   Audio → Whisper → Text with [Speaker N] labels
   Output: Text file with timestamps

3. ANALYZE (After recording, run manually)
   python process_transcript.py transcripts/transcript_speakers_*.txt
   Output: processed/transcript_*_analysis.json

   Extracts:
   - Topics discussed
   - Entities (companies, people, skills)
   - Intents (what each speaker wants/offers)
   - Key points

4. MATCH (Future: integrate with Neo4j)
   Analysis → Graph Database → Find relevant connections
   Output: Potential leads, matches

5. ACTION
   Schedule meetings, send intros, etc.
```

## Usage Examples

### Basic Recording (No Speaker Detection)
```bash
python audio_recorder_whisper.py
# Output: transcripts/transcript_whisper_*.txt
```

### With Speaker Detection
```bash
python audio_recorder_with_speakers.py
# Output:
#   - transcripts/transcript_speakers_*.txt
#   - recordings/session_*.wav
```

### Process After Recording
```bash
python process_transcript.py transcripts/transcript_speakers_20251108_184521.txt
# Output: processed/transcript_*_analysis.json
```

## Understanding the Files

### Transcript File Format
```
Recording Session with Speaker Detection
Started: 2025-11-08 18:33:03
Model: Whisper base
======================================================================

[Speaker 1] [18:33:05]
Hi, I'm looking for investment opportunities in AI startups.

[Speaker 2] [18:33:12]
Great! I'm building an AI-powered lead generation platform.
(Detected 2 potential speakers in this segment)

[Speaker 1] [18:33:20]
Tell me more about your tech stack.
```

### Analysis JSON Format
```json
{
  "content_analysis": {
    "topics": [
      {"topic": "AI startups", "relevance": 0.95},
      {"topic": "Investment", "relevance": 0.88}
    ],
    "key_points": [
      "Looking for investment opportunities",
      "Building AI lead generation platform"
    ]
  },
  "entities": {
    "entities": [
      {"type": "SKILL", "value": "AI"},
      {"type": "INTENT", "value": "investment"}
    ]
  },
  "intents": {
    "looking_for": [
      {"intent_type": "investment", "confidence": 0.92}
    ],
    "offering": [
      {"intent_type": "AI platform", "confidence": 0.85}
    ]
  }
}
```

## Performance & Storage

### File Sizes
- Transcript (1 hour): ~10-50 KB (text only)
- Audio (1 hour): ~115 MB (WAV format, 16kHz mono)
- Analysis JSON: ~5-20 KB

### Processing Speed
- Transcription: ~5-10 seconds per chunk (real-time capable)
- Speaker detection: Adds ~1-2 seconds
- AI analysis: ~10-30 seconds for full transcript

### Disk Space (for 10 events, 2 hours each)
- Transcripts: ~1 MB
- Audio files: ~2.3 GB
- Analysis: ~200 KB

**Total**: ~2.3 GB for 20 hours of recordings