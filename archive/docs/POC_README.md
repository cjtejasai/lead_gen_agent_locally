# Audio Recording POC - Quick Start Guide

## Overview
Simple proof-of-concept to record audio from your Bluetooth headset and transcribe it to text in real-time.

## Two Options Available

### Option 1: Google Speech Recognition (Easiest)
- **File**: `audio_recorder_poc.py`
- **Pros**: Easy setup, no model download, works instantly
- **Cons**: Requires internet connection
- **Best for**: Quick testing

### Option 2: Whisper (Best Quality, Offline)
- **File**: `audio_recorder_whisper.py`
- **Pros**: Works offline, better accuracy, privacy-friendly
- **Cons**: Requires model download (~140MB for base model), slower
- **Best for**: Production use, offline scenarios

## Quick Setup

### 1. Install Dependencies

```bash
# Install POC requirements
pip install -r poc_requirements.txt

# For Whisper option, also install ffmpeg:
# macOS:
brew install ffmpeg

# Linux:
sudo apt install ffmpeg
```

### 2. Connect Your Bluetooth Headset

1. Pair your Boat headset with your laptop via Bluetooth
2. Make sure it's connected and set as an input device
3. Test it by opening System Preferences > Sound > Input and speaking

### 3. Run the POC

**Option A: Google Speech Recognition (Easy)**
```bash
python audio_recorder_poc.py
```

**Option B: Whisper (Better Quality)**
```bash
python audio_recorder_whisper.py
```

### 4. Follow the Prompts

1. The script will list all available audio devices
2. Select your Bluetooth headset number (or press Enter for default)
3. For Whisper: Select model size (recommend "base" for testing)
4. Start speaking!
5. Press Ctrl+C to stop

## Output

### Transcripts
All transcripts are saved in the `transcripts/` directory with timestamps:
```
transcripts/
  transcript_20240108_143022.txt
  transcript_whisper_20240108_143530.txt
```

### Format
```
Recording Session: 2024-01-08 14:30:22
============================================================

[14:30:25] Hello, this is a test of the recording system.
[14:30:32] I'm speaking into my Bluetooth headset.
[14:30:40] The transcription is working pretty well!
```

## Troubleshooting

### Can't see your Bluetooth headset?
1. Check Bluetooth settings - make sure headset is connected
2. Try System Preferences > Sound > Input - is your headset listed?
3. Run the script again - sometimes it takes a moment after connection

### No audio input detected?
```bash
# Test your audio devices
python -c "import sounddevice as sd; print(sd.query_devices())"
```

### Import errors?
```bash
# Make sure you're in the right directory
cd /Users/cjtejasai/PycharmProjects/ayka_lead_gen

# Install dependencies
pip install sounddevice soundfile numpy SpeechRecognition

# For Whisper version:
pip install openai-whisper
```

### Whisper model download failing?
The first time you run Whisper, it downloads the model (~140MB for base).
If it fails:
```bash
# Pre-download the model
python -c "import whisper; whisper.load_model('base')"
```

## Next Steps - Processing Pipeline

Once you have transcripts, you can process them with your existing backend:

```python
# Example: Process transcript with your agents
from backend.app.agents.orchestrator import AgentOrchestrator

# Read transcript
with open('transcripts/transcript_20240108_143022.txt', 'r') as f:
    transcript = f.read()

# Analyze with your multi-agent system
orchestrator = AgentOrchestrator()
results = orchestrator.analyze_recording(transcript, user_category="general")

print(results)
```

## Performance Tips

### For Real-time Use:
- Use `audio_recorder_poc.py` (Google) - faster response
- Or use Whisper "tiny" model for speed

### For Accuracy:
- Use Whisper "base" or "small" model
- Speak clearly and avoid background noise
- Keep microphone close (3-4 inches)

### Battery Optimization:
- Use Google option (less CPU)
- Or use Whisper "tiny" model

## What's Being Created

```
ayka_lead_gen/
├── audio_recorder_poc.py          # Google Speech Recognition version
├── audio_recorder_whisper.py      # Whisper (local) version
├── poc_requirements.txt           # Dependencies
├── transcripts/                   # Output transcripts
│   └── transcript_*.txt
└── recordings/                    # (Optional) Raw audio files
    └── recording_*.wav
```

## Demo Usage

```bash
# 1. Start recording
python audio_recorder_whisper.py

# 2. Select your headset
# Example output:
# === Available Audio Input Devices ===
# [0] MacBook Pro Microphone
# [1] Boat Headset
# [2] External USB Mic
# =====================================
# Enter device number: 1

# 3. Select model (for Whisper)
# Select model (1/2/3) [default: 2]: 2

# 4. Start speaking!
# [14:30:25] ✓
# [14:30:25] Hello, I'm testing the recording system.

# 5. Press Ctrl+C when done
```

## Integration with Main Platform

This POC creates the foundation for your main platform. The transcripts can be fed into:

1. **Content Analyzer Agent** - Extract topics and key points
2. **Entity Extractor** - Identify companies, people, technologies
3. **Intent Classifier** - Understand what user is looking for
4. **Graph Matcher** - Find relevant connections in Neo4j

See `backend/app/agents/` for the full pipeline implementation.

## License
Part of the Ayka Lead Generation Platform