# AYKA Lead Generation - Audio Recording POC

## 📁 Project Structure

```
ayka_lead_gen/
├── audio_recorders/                    # All audio recording scripts
│   ├── README.md                       # Documentation for all versions
│   ├── audio_recorder_with_speaker_detection.py  ⭐ RECOMMENDED
│   ├── audio_recorder_poc.py           # Initial POC (Google Speech)
│   ├── audio_recorder_whisper.py       # Whisper only (no speakers)
│   ├── audio_recorder_with_speakers.py # Energy-based detection
│   ├── audio_recorder_smart_speakers.py # Pitch/spectral features
│   ├── audio_recorder_real_speakers.py # pyannote real-time (buggy)
│   └── audio_recorder_realtime_speakers.py # Improved real-time
│
├── record_audio.py → audio_recorders/audio_recorder_with_speaker_detection.py
│                                       # Symlink for easy access
│
├── transcripts/                        # Generated transcripts
│   └── transcript_YYYYMMDD_HHMMSS.txt
│
├── recordings/                         # Audio files
│   └── session_YYYYMMDD_HHMMSS.wav
│
├── .env                                # Environment variables (HF_TOKEN)
├── poc_requirements.txt                # Python dependencies
└── DATA_FLOW_EXPLAINED.md             # Technical documentation
```

## 🚀 Quick Start

### Run the Recommended Version

**Option 1 - Using the symlink:**
```bash
python record_audio.py
```

**Option 2 - Direct path:**
```bash
python audio_recorders/audio_recorder_with_speaker_detection.py
```

### What You'll Get

1. **During Recording:**
   - Real-time transcription displayed in terminal
   - See text appear every 8 seconds as you speak

2. **After Recording (Ctrl+C):**
   - Speaker detection runs on full audio (~30 seconds)
   - Final transcript with speaker labels saved

3. **Output Files:**
   - `transcripts/transcript_YYYYMMDD_HHMMSS.txt` - Text with speaker labels
   - `recordings/session_YYYYMMDD_HHMMSS.wav` - Audio recording

## 📋 Example Output

```
Recording Session with Speaker Detection
Date: 2025-11-08 20:32:31
Model: Whisper base + pyannote diarization
Duration: 67.2 seconds
======================================================================

[SPEAKER_00] [00:05]
Hi, I'm looking for investors

[SPEAKER_01] [00:12]
I'm an investor, what's your startup?

[SPEAKER_00] [00:20]
We're building AI tools

======================================================================
SESSION SUMMARY
======================================================================

Total segments: 8
Unique speakers: 2

SPEAKER_00: 4 segments
SPEAKER_01: 4 segments
```

## 🔧 Technical Stack

- **Whisper:** Speech-to-text transcription (OpenAI)
- **pyannote.audio:** Speaker diarization (Hugging Face)
- **sounddevice:** Audio capture from Bluetooth headset
- **Python 3.13**

## 📝 Next Steps

1. **Record Audio:** Use `record_audio.py`
2. **Process Transcript:** Run through AI analysis pipeline
   ```bash
   python process_transcript.py transcripts/transcript_*.txt
   ```
3. **Extract Insights:** Get topics, entities, intents for lead generation

## 🎯 Use Case

Record conversations at networking events, automatically:
- Transcribe what everyone says
- Identify different speakers
- Process for lead generation insights
- Find potential matches in your network
