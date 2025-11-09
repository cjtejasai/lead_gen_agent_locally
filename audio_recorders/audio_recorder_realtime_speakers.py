#!/usr/bin/env python3
"""
Real-time Audio Recording with Real-time Speaker Detection
Detects speakers as you speak using pyannote.audio
"""

import sounddevice as sd
import numpy as np
import queue
import sys
from datetime import datetime
from pathlib import Path
import threading
import wave
import ssl
import os
from dotenv import load_dotenv
import warnings
import torch

# Load environment variables
load_dotenv()

# Suppress warnings
warnings.filterwarnings('ignore', message='.*torchcodec.*')
warnings.filterwarnings('ignore', category=UserWarning, module='pyannote.audio.core.io')
warnings.filterwarnings('ignore', category=UserWarning, module='pyannote.audio.models.blocks.pooling')

# Fix SSL
ssl._create_default_https_context = ssl._create_unverified_context

# Imports
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

try:
    from pyannote.audio import Pipeline
    PYANNOTE_AVAILABLE = True
except ImportError:
    PYANNOTE_AVAILABLE = False

# Configuration
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_DURATION = 15  # Longer chunks for better speaker detection (15 seconds)
OUTPUT_DIR = Path("transcripts")
AUDIO_DIR = Path("recordings")

OUTPUT_DIR.mkdir(exist_ok=True)
AUDIO_DIR.mkdir(exist_ok=True)

audio_queue = queue.Queue()
is_recording = True


def list_audio_devices():
    """List all available audio input devices"""
    print("\n=== Available Audio Input Devices ===")
    devices = sd.query_devices()
    for idx, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            print(f"[{idx}] {device['name']}")
    print("=" * 40)
    return devices


def audio_callback(indata, frames, time, status):
    """Callback for audio stream"""
    if status:
        print(f"Audio status: {status}", file=sys.stderr)
    audio_queue.put(indata.copy())


class RealtimeSpeakerDetector:
    """
    Real-time speaker detection using pyannote.audio
    Maintains speaker history for consistency
    """
    def __init__(self, pipeline):
        self.pipeline = pipeline
        self.speaker_map = {}  # Map pyannote labels to consistent IDs
        self.next_speaker_id = 1

    def detect_speakers(self, audio_data):
        """
        Run speaker detection on audio chunk
        Returns dominant speaker label
        """
        try:
            # Check if audio has enough energy (not silence)
            energy = np.sqrt(np.mean(audio_data ** 2))
            if energy < 0.01:  # Very quiet/silence
                return "Unknown"

            # Convert to torch tensor
            waveform = torch.from_numpy(audio_data).unsqueeze(0).float()

            # Create audio input dict
            audio_input = {
                "waveform": waveform,
                "sample_rate": SAMPLE_RATE
            }

            # Suppress warnings during diarization
            import warnings
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore')

                # Run diarization
                diarization = self.pipeline(audio_input)

            # Count speaking time per speaker
            speaker_times = {}

            # Iterate through diarization segments
            try:
                for segment, _, label in diarization.itertracks(yield_label=True):
                    duration = segment.end - segment.start
                    speaker_times[label] = speaker_times.get(label, 0) + duration
            except:
                # If itertracks fails, try alternative approach
                if hasattr(diarization, 'labels') and callable(diarization.labels):
                    labels = list(diarization.labels())
                    if labels:
                        dominant_speaker_label = labels[0]
                        # Map to consistent speaker ID
                        if dominant_speaker_label not in self.speaker_map:
                            self.speaker_map[dominant_speaker_label] = f"Speaker {self.next_speaker_id}"
                            self.next_speaker_id += 1
                        return self.speaker_map[dominant_speaker_label]
                return "Unknown"

            if not speaker_times:
                return "Unknown"

            # Get dominant speaker (most speaking time)
            dominant_speaker_label = max(speaker_times, key=speaker_times.get)

            # Map to consistent speaker ID
            if dominant_speaker_label not in self.speaker_map:
                self.speaker_map[dominant_speaker_label] = f"Speaker {self.next_speaker_id}"
                self.next_speaker_id += 1

            return self.speaker_map[dominant_speaker_label]

        except Exception as e:
            # Silently fail and return Unknown
            return "Unknown"

    def get_speaker_count(self):
        """Get number of unique speakers detected"""
        return len(self.speaker_map)


def transcribe_realtime(model_name="base", hf_token=None):
    """
    Real-time transcription with real-time speaker detection
    """
    global is_recording

    print(f"\nLoading Whisper model '{model_name}'...")
    model = whisper.load_model(model_name)
    print("✓ Whisper loaded")

    # Load speaker diarization pipeline
    speaker_detector = None
    if PYANNOTE_AVAILABLE and hf_token:
        try:
            print("\nLoading speaker diarization model...")
            print("(First time will download ~1GB model)")

            pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                token=hf_token
            )

            speaker_detector = RealtimeSpeakerDetector(pipeline)
            print("✓ Speaker diarization loaded\n")

        except Exception as e:
            print(f"\n⚠️  Could not load speaker detection: {e}")
            print("Continuing without speaker detection\n")

    # Create output files
    session_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    transcript_file = OUTPUT_DIR / f"transcript_realtime_{session_time}.txt"
    audio_file = AUDIO_DIR / f"session_{session_time}.wav"

    print(f"📝 Transcript: {transcript_file}")
    print(f"🎵 Audio: {audio_file}\n")

    with open(transcript_file, 'w') as f:
        f.write(f"Real-time Recording with Speaker Detection\n")
        f.write(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Model: Whisper {model_name}")
        if speaker_detector:
            f.write(f" + pyannote.audio real-time\n")
        else:
            f.write(f"\n")
        f.write("=" * 70 + "\n\n")

    audio_chunks = []
    all_audio = []
    chunk_counter = 0
    speaker_stats = {}

    print("=" * 70)
    if speaker_detector:
        print("  🎙️  REAL-TIME RECORDING with SPEAKER DETECTION")
        print("  Detecting speakers as you speak!")
    else:
        print("  🎙️  REAL-TIME RECORDING")
        print("  (No speaker detection)")
    print("  Press Ctrl+C to stop")
    print("=" * 70 + "\n")

    while is_recording or not audio_queue.empty():
        try:
            chunk = audio_queue.get(timeout=1)
            audio_chunks.append(chunk)
            all_audio.append(chunk)

            # Process every CHUNK_DURATION seconds
            if len(audio_chunks) >= int(CHUNK_DURATION * SAMPLE_RATE / 1024):
                chunk_counter += 1
                audio_data = np.concatenate(audio_chunks).flatten()
                audio_chunks = []

                print(f"[Chunk {chunk_counter}] ", end="", flush=True)

                try:
                    # Convert to float32
                    audio_float = audio_data.astype(np.float32)

                    # Detect speaker first (if available)
                    speaker_label = "Unknown"
                    if speaker_detector:
                        print("Detecting speaker... ", end="", flush=True)
                        speaker_label = speaker_detector.detect_speakers(audio_float)

                    # Transcribe
                    print("Transcribing... ", end="", flush=True)
                    result = model.transcribe(audio_float, language="en", fp16=False)
                    text = result["text"].strip()

                    if text:
                        timestamp = datetime.now().strftime('%H:%M:%S')
                        speaker_stats[speaker_label] = speaker_stats.get(speaker_label, 0) + 1

                        print(f"✓")
                        print(f"[{speaker_label}] [{timestamp}]")
                        print(f"{text}\n")

                        # Write to file immediately
                        with open(transcript_file, 'a') as f:
                            f.write(f"[{speaker_label}] [{timestamp}]\n")
                            f.write(f"{text}\n\n")
                    else:
                        print("✗ (silence)\n")

                except Exception as e:
                    print(f"✗ Error: {e}\n")
                    import traceback
                    traceback.print_exc()

        except queue.Empty:
            continue
        except KeyboardInterrupt:
            break

    # Save audio file
    if all_audio:
        print(f"\n💾 Saving audio...")
        audio_data = np.concatenate(all_audio).flatten()
        audio_int16 = (audio_data * 32767).astype(np.int16)

        with wave.open(str(audio_file), 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(audio_int16.tobytes())

        print(f"✓ Audio saved")

    # Session summary
    print(f"\n📊 Session Summary:")
    with open(transcript_file, 'a') as f:
        f.write("\n" + "=" * 70 + "\n")
        f.write("SESSION SUMMARY\n")
        f.write("=" * 70 + "\n\n")

        if speaker_detector:
            total_speakers = speaker_detector.get_speaker_count()
            f.write(f"Unique Speakers Detected: {total_speakers}\n\n")
            print(f"  Unique speakers: {total_speakers}")

        f.write("Segments per speaker:\n")
        for speaker, segments in sorted(speaker_stats.items()):
            print(f"  {speaker}: {segments} segments")
            f.write(f"{speaker}: {segments} segments\n")

    print(f"\n✓ Transcript saved: {transcript_file}")
    print(f"✓ Audio saved: {audio_file}")


def main():
    global is_recording

    print("=" * 70)
    print("  REAL-TIME Speaker Detection")
    print("  Detects speakers as you speak!")
    print("=" * 70)

    if not WHISPER_AVAILABLE:
        print("\nERROR: Whisper not installed!")
        print("Install with: pip install openai-whisper")
        sys.exit(1)

    if not PYANNOTE_AVAILABLE:
        print("\n⚠️  pyannote.audio not installed!")
        print("Install with: pip install pyannote.audio")
        print("Continuing without speaker detection...\n")

    # Check for HF token
    hf_token = os.environ.get('HF_TOKEN')
    if hf_token:
        print("✓ Found Hugging Face token in environment")
    elif PYANNOTE_AVAILABLE:
        print("\n💡 For speaker detection, set HF_TOKEN in .env file")
        print("   Get token: https://huggingface.co/settings/tokens")
        print("   Accept license: https://huggingface.co/pyannote/speaker-diarization-3.1")

    # List devices
    devices = list_audio_devices()

    # Select device
    device_input = input("\nEnter device number (or press Enter for default): ").strip()
    device_id = int(device_input) if device_input else None

    if device_id is not None:
        print(f"\nUsing device: [{device_id}] {devices[device_id]['name']}")
    else:
        print("\nUsing default input device")

    # Model selection
    print("\nWhisper model:")
    print("  1. tiny   - Fast")
    print("  2. base   - Recommended")
    model_choice = input("Select (1/2) [default: 2]: ").strip()
    model_name = "tiny" if model_choice == "1" else "base"

    # Start transcription thread
    transcribe_thread = threading.Thread(
        target=transcribe_realtime,
        args=(model_name, hf_token),
        daemon=True
    )
    transcribe_thread.start()

    try:
        with sd.InputStream(
            device=device_id,
            channels=CHANNELS,
            samplerate=SAMPLE_RATE,
            callback=audio_callback,
            blocksize=1024
        ):
            while is_recording:
                sd.sleep(1000)

    except KeyboardInterrupt:
        print("\n\nStopping recording...")
        is_recording = False
    except Exception as e:
        print(f"\nError: {e}")
        is_recording = False

    print("\nFinishing transcription...")
    transcribe_thread.join(timeout=30)

    print("\n" + "=" * 70)
    print("  Recording completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()