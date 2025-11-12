#!/usr/bin/env python3
"""
POC: Real Speaker Detection using pyannote.audio
Industry-standard AI model for speaker diarization - works automatically!
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
import tempfile
import os
from dotenv import load_dotenv
import warnings

# Load environment variables from .env file
load_dotenv()

# Suppress the torchcodec warning - we use WAV files, not video
warnings.filterwarnings('ignore', message='.*torchcodec.*')
warnings.filterwarnings('ignore', category=UserWarning, module='pyannote.audio.core.io')

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
    import torch
    PYANNOTE_AVAILABLE = True
except ImportError:
    PYANNOTE_AVAILABLE = False

# Configuration
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_DURATION = 10  # Longer chunks for better speaker detection
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


def transcribe_with_real_diarization(model_name="base", use_hf_token=None):
    """
    Transcribe with pyannote.audio speaker diarization
    """
    global is_recording

    print(f"\nLoading Whisper model '{model_name}'...")
    model = whisper.load_model(model_name)
    print("✓ Whisper loaded")

    # Try to load pyannote pipeline
    diarization_pipeline = None
    if PYANNOTE_AVAILABLE:
        try:
            print("\nLoading speaker diarization model...")
            print("Note: First time will download ~1GB model from Hugging Face")

            # New version uses 'token' instead of 'use_auth_token'
            diarization_pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                token=use_hf_token if use_hf_token else True
            )

            print("✓ Speaker diarization loaded")
        except Exception as e:
            print(f"\n⚠️  Could not load diarization model: {e}")
            print("Will proceed without speaker detection")
            print("\nTo enable speaker detection:")
            print("1. Get token from https://huggingface.co/settings/tokens")
            print("2. Accept license at https://huggingface.co/pyannote/speaker-diarization-3.1")
            print("3. Run again with: export HF_TOKEN=your_token")

    session_file = OUTPUT_DIR / f"transcript_real_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    audio_file = AUDIO_DIR / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"

    print(f"\n📝 Transcript: {session_file}")
    print(f"🎵 Audio: {audio_file}")

    with open(session_file, 'w') as f:
        f.write(f"Recording Session with Real Speaker Diarization\n")
        f.write(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Model: Whisper {model_name}")
        if diarization_pipeline:
            f.write(f" + pyannote.audio diarization\n")
        else:
            f.write(f" (no speaker detection)\n")
        f.write("=" * 70 + "\n\n")

    audio_chunks = []
    all_audio = []
    chunk_counter = 0
    speaker_stats = {}

    print("\n" + "=" * 70)
    if diarization_pipeline:
        print("  Recording with AI speaker detection enabled!")
        print("  System will automatically identify different speakers.")
    else:
        print("  Recording without speaker detection")
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

                print(f"\n[Chunk {chunk_counter}] Processing...", end=" ")

                try:
                    # Transcribe first
                    audio_float = audio_data.astype(np.float32)
                    result = model.transcribe(audio_float, language="en", fp16=False)
                    text = result["text"].strip()

                    if text:
                        # Determine speaker if diarization available
                        speaker_label = "Unknown"

                        if diarization_pipeline:
                            try:
                                # Convert audio to torch tensor format pyannote expects
                                import torch

                                # Create waveform dict that pyannote can use directly
                                waveform = torch.from_numpy(audio_float).unsqueeze(0)  # Add channel dimension

                                # Create the audio input dict
                                audio_input = {
                                    "waveform": waveform,
                                    "sample_rate": SAMPLE_RATE
                                }

                                # Run diarization on the audio data directly
                                diarization = diarization_pipeline(audio_input)

                                # Get speaker for this audio
                                # Find most dominant speaker in this chunk
                                speaker_times = {}

                                # Check if diarization has segments
                                if hasattr(diarization, 'labels'):
                                    # New API: iterate through timeline
                                    for segment, _, label in diarization.itertracks(yield_label=True):
                                        duration = segment.end - segment.start
                                        speaker_times[label] = speaker_times.get(label, 0) + duration
                                elif hasattr(diarization, '__iter__'):
                                    # Try iterating directly
                                    for item in diarization:
                                        if hasattr(item, 'label'):
                                            speaker_times[item.label] = speaker_times.get(item.label, 0) + 1

                                if speaker_times:
                                    # Get speaker with most speaking time
                                    dominant_speaker = max(speaker_times, key=speaker_times.get)
                                    speaker_label = dominant_speaker
                            except Exception as diar_error:
                                # If diarization fails, just continue without it
                                print(f" (diarization failed: {diar_error})")
                                speaker_label = "Unknown"

                        timestamp = datetime.now().strftime('%H:%M:%S')
                        speaker_stats[speaker_label] = speaker_stats.get(speaker_label, 0) + 1

                        print(f"✓")
                        print(f"[{speaker_label}] [{timestamp}] {text}")

                        # Write to file
                        with open(session_file, 'a') as f:
                            f.write(f"[{speaker_label}] [{timestamp}]\n")
                            f.write(f"{text}\n\n")
                    else:
                        print("✗ (silence)")

                except Exception as e:
                    print(f"✗ Error: {e}")
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
    with open(session_file, 'a') as f:
        f.write("\n" + "=" * 70 + "\n")
        f.write("SESSION SUMMARY\n")
        f.write("=" * 70 + "\n\n")

        total_speakers = len([s for s in speaker_stats.keys() if s != "Unknown"])
        f.write(f"Unique Speakers Detected: {total_speakers}\n\n")

        for speaker, segments in sorted(speaker_stats.items()):
            print(f"  {speaker}: {segments} segments")
            f.write(f"{speaker}: {segments} segments\n")

    print(f"\n✓ Transcript saved: {session_file}")


def main():
    global is_recording

    print("=" * 70)
    print("  Real Speaker Detection with pyannote.audio")
    print("  Professional AI-based speaker diarization!")
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
    hf_token = None
    import os
    if 'HF_TOKEN' in os.environ:
        hf_token = os.environ['HF_TOKEN']
        print("✓ Found Hugging Face token in environment")
    elif PYANNOTE_AVAILABLE:
        print("\n💡 TIP: For speaker detection, you need a Hugging Face token:")
        print("   1. Get token: https://huggingface.co/settings/tokens")
        print("   2. Accept license: https://huggingface.co/pyannote/speaker-diarization-3.1")
        print("   3. Set token: export HF_TOKEN=your_token")
        token_input = input("\nEnter HF token now (or press Enter to skip): ").strip()
        if token_input:
            hf_token = token_input

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

    # Start transcription
    transcribe_thread = threading.Thread(
        target=transcribe_with_real_diarization,
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
    transcribe_thread.join(timeout=20)

    print("\n" + "=" * 70)
    print("  Recording completed!")
    print(f"  Check: {OUTPUT_DIR}/")
    print("=" * 70)


if __name__ == "__main__":
    main()