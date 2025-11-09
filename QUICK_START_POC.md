# 🎤 Audio Recording POC - Quick Start

## What You Have Now

Three Python scripts ready to use:

1. **`test_audio_devices.py`** - Check if your Bluetooth headset is detected
2. **`audio_recorder_poc.py`** - Record & transcribe using Google (easy, requires internet)
3. **`audio_recorder_whisper.py`** - Record & transcribe using Whisper (offline, better quality)

## Step-by-Step Guide

### 1️⃣ Connect Your Boat Headset

```bash
# On macOS:
# 1. Turn on your Boat headset
# 2. Go to System Settings > Bluetooth
# 3. Click "Connect" next to your Boat headset
# 4. Wait for "Connected" status
```

### 2️⃣ Check if Headset is Detected

```bash
python test_audio_devices.py
```

**Expected output:**
```
📱 INPUT DEVICES (Microphones/Headsets):

[0] MacBook Air Microphone
    Channels: 1
    Sample Rate: 48000.0 Hz

[1] Boat Headset                    👈 Your headset should appear here
    👉 This looks like a Bluetooth device!
    Channels: 1
    Sample Rate: 48000.0 Hz
```

**If your headset is NOT listed:**
- Check Bluetooth connection (System Settings > Bluetooth)
- Make sure headset is not connected to another device (phone, etc.)
- Try disconnecting and reconnecting
- Check System Settings > Sound > Input - is your headset listed there?

### 3️⃣ Run the POC (Choose One)

#### Option A: Google Speech Recognition (Easiest)

```bash
python audio_recorder_poc.py
```

**Pros:**
- Works instantly
- No model download
- Fast response

**Cons:**
- Requires internet
- Less accurate with accents

#### Option B: Whisper (Recommended)

```bash
# First time only - install Whisper and ffmpeg
pip install openai-whisper
brew install ffmpeg  # macOS

# Run the script
python audio_recorder_whisper.py
```

**Pros:**
- Works offline
- Better accuracy
- Privacy-friendly (no data sent online)

**Cons:**
- ~140MB model download (first time only)
- Slightly slower

### 4️⃣ Using the Script

```bash
$ python audio_recorder_poc.py

=== Available Audio Input Devices ===
[0] MacBook Air Microphone
[1] Boat Headset
====================================

Enter device number (or press Enter for default): 1    👈 Enter your headset number

============================================================
  Recording started! Speak into your headset.
  Press Ctrl+C to stop recording.
============================================================

[14:30:25] ✓
[14:30:25] Hello, I'm testing the recording system.

[14:30:32] ✓
[14:30:32] This is working really well!

^C                                                        👈 Press Ctrl+C to stop

Stopping recording...
Session transcript saved to: transcripts/transcript_20240108_143022.txt
```

## Output Files

All transcripts are saved in `transcripts/` directory:

```bash
$ ls transcripts/
transcript_20240108_143022.txt
transcript_whisper_20240108_143530.txt
```

**Sample transcript:**
```
Recording Session: 2024-01-08 14:30:22
============================================================

[14:30:25] Hello, I'm testing the recording system.
[14:30:32] This is working really well!
[14:30:45] I can use this for my lead generation platform.
```

## Troubleshooting

### "No module named sounddevice"
```bash
pip install sounddevice soundfile numpy SpeechRecognition
```

### Whisper not working
```bash
# Install Whisper
pip install openai-whisper

# Install ffmpeg (required by Whisper)
# macOS:
brew install ffmpeg

# Linux:
sudo apt install ffmpeg
```

### "Error: PortAudio library not found"
This happens on some systems. Fix:

```bash
# macOS:
brew install portaudio

# Linux:
sudo apt install portaudio19-dev python3-pyaudio
```

### Audio is choppy or cutting out
- Try using a shorter chunk duration
- Close other audio applications
- Check if your Bluetooth connection is stable

## Next Steps - Integration

Once you have transcripts, integrate with your existing backend:

```python
# Example: Process transcript with your AI agents
from backend.app.agents.orchestrator import AgentOrchestrator

# Read the transcript
with open('transcripts/transcript_20240108_143022.txt', 'r') as f:
    content = f.read()

# Extract just the spoken text (remove timestamps)
lines = content.split('\n')
transcript = ' '.join([
    line.split('] ', 1)[1]
    for line in lines
    if line.startswith('[') and '] ' in line
])

# Run through your AI pipeline
orchestrator = AgentOrchestrator()
results = orchestrator.analyze_recording(
    transcript=transcript,
    user_category="general"
)

# Results will contain:
# - Content analysis (topics, key points)
# - Extracted entities (companies, people, skills)
# - User intents (what they're looking for/offering)
print(results)
```

## Performance Tips

**For Best Accuracy:**
- Speak clearly and at a moderate pace
- Keep microphone 3-4 inches from mouth
- Use in a quiet environment
- Use Whisper "base" or "small" model

**For Speed:**
- Use Google option (audio_recorder_poc.py)
- Or use Whisper "tiny" model
- Reduce CHUNK_DURATION in the script

**For Battery Life:**
- Use Google option (less CPU intensive)
- Or use Whisper "tiny" model

## Files Created

```
ayka_lead_gen/
├── test_audio_devices.py         # Test script
├── audio_recorder_poc.py          # Google STT version
├── audio_recorder_whisper.py      # Whisper version
├── poc_requirements.txt           # Dependencies
├── POC_README.md                  # Detailed docs
├── QUICK_START_POC.md            # This file
├── transcripts/                   # Output folder (created automatically)
│   └── transcript_*.txt
└── recordings/                    # Optional audio files (created automatically)
    └── recording_*.wav
```

## Ready to Test!

1. Connect your Boat headset
2. Run: `python test_audio_devices.py` (verify headset detected)
3. Run: `python audio_recorder_poc.py` (start recording)
4. Speak into your headset
5. Press Ctrl+C to stop
6. Check `transcripts/` folder for output

**That's it!** You now have a working POC that records from your Bluetooth headset and transcribes to text.

---

## What This Enables

This POC is the foundation for your full platform:

1. ✅ **Audio Capture** - Record conversations at events
2. ✅ **Speech-to-Text** - Convert to readable text
3. 🔄 **Next: AI Analysis** - Extract insights, interests, intents
4. 🔄 **Next: Graph Matching** - Find relevant connections
5. 🔄 **Next: Lead Generation** - Identify opportunities

You're ready to build the full pipeline! 🚀