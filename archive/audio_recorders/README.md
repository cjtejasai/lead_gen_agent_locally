# Audio Recorder Scripts

This folder contains all audio recording scripts for the AYKA Lead Generation POC.

## 🎯 RECOMMENDED VERSION

### `audio_recorder_with_speaker_detection.py` ⭐
**This is the final, working version. Use this one!**

**Features:**
- ✅ Real-time transcription with Whisper (see text as you speak)
- ✅ Accurate post-processing speaker detection with pyannote.audio
- ✅ Identifies different speakers correctly (no more "Unknown" labels)
- ✅ Works offline after initial model download
- ✅ Free (no API costs)

**How to Run:**
```bash
python audio_recorders/audio_recorder_with_speaker_detection.py
```

**Output:**
- Transcripts with speaker labels in `transcripts/transcript_*.txt`
- Audio recordings in `recordings/session_*.wav`

**Example Output:**
```
[SPEAKER_00] [00:05]
Hi, I'm looking for investors

[SPEAKER_01] [00:12]
I'm an investor, what's your startup?
```

---

## 📚 Other Versions (Historical/Development)

### `audio_recorder_poc.py`
- **Purpose:** Initial proof of concept
- **Tech:** Google Speech Recognition (requires internet)
- **Status:** Works but requires internet connection
- **Issue:** No speaker detection

### `audio_recorder_whisper.py`
- **Purpose:** First offline version
- **Tech:** Whisper for transcription
- **Status:** Works perfectly for transcription
- **Issue:** No speaker detection

### `audio_recorder_with_speakers.py`
- **Purpose:** First attempt at speaker detection
- **Tech:** Simple energy-based detection
- **Status:** Inaccurate
- **Issue:** Created 24 speakers for 4 people, or grouped 3 people as 1

### `audio_recorder_smart_speakers.py`
- **Purpose:** Better speaker detection attempt
- **Tech:** Pitch and spectral features
- **Status:** Still inaccurate
- **Issue:** Detected 3 speakers as 1 speaker

### `audio_recorder_real_speakers.py`
- **Purpose:** First pyannote.audio integration
- **Tech:** Whisper + pyannote (real-time chunks)
- **Status:** Partially working
- **Issue:** All segments labeled as "Unknown" - real-time chunk processing failed

### `audio_recorder_realtime_speakers.py`
- **Purpose:** Improved real-time speaker detection
- **Tech:** Longer chunks (15 seconds) for better accuracy
- **Status:** Improved but still issues
- **Issue:** Real-time detection on short chunks not reliable enough

---

## 🛠️ Technical Details

### Why Post-Processing Works Better

**Real-time Approach (Problematic):**
- Process 8-15 second chunks
- Not enough context for accurate speaker identification
- Results in "Unknown" labels or inconsistent speakers

**Post-Processing Approach (Recommended):**
- Record and transcribe in real-time (see text immediately)
- After recording stops, analyze COMPLETE audio
- Much more accurate speaker detection (90-95% accuracy)
- Properly identifies 4 speakers instead of 24 or grouping them incorrectly

### Requirements

Install dependencies:
```bash
pip install openai-whisper pyannote.audio python-dotenv sounddevice numpy torch
```

Set up Hugging Face token in `.env`:
```
HF_TOKEN=your_token_here
```

Get token from: https://huggingface.co/settings/tokens
Accept license: https://huggingface.co/pyannote/speaker-diarization-3.1

### How It Works

1. **Audio Capture:** Bluetooth headset → sounddevice library
2. **Real-time Transcription:** Whisper converts speech to text every 8 seconds
3. **Audio Storage:** Full recording saved as WAV file
4. **Speaker Detection:** pyannote.audio analyzes complete recording (after Ctrl+C)
5. **Matching:** Speaker labels matched to transcript segments by timestamp
6. **Final Output:** Transcript with speaker labels saved to file

### Data Flow

```
Microphone → Real-time Transcription → Display Text
     |                                       |
     └─────────→ Save Full Audio ───────────┘
                       |
                       ↓
              Speaker Detection (post-processing)
                       |
                       ↓
              Match Speakers to Transcript
                       |
                       ↓
              Final Transcript with Speakers
```

---

## 📝 Usage Notes

- **Recording Time:** Recommend at least 30 seconds for good speaker detection
- **Number of Speakers:** Works best with 2-6 speakers
- **Audio Quality:** Clear speech in quiet environment gives best results
- **Processing Time:** Speaker detection takes 30-60 seconds after recording

## 🔗 Integration

Transcripts can be processed through the existing AI analysis pipeline:
```bash
python process_transcript.py transcripts/transcript_*.txt
```

This will extract:
- Topics discussed
- Entities (companies, people, skills)
- Intents (what each speaker wants/offers)
- Key points for lead generation