#!/usr/bin/env python3
"""
POC: Real-time Audio Recording with Whisper (Local, Offline)
Uses OpenAI's Whisper model running locally - no internet required!
"""

import sounddevice as sd
import numpy as np
import queue
import sys
from datetime import datetime
from pathlib import Path
import threading
import tempfile
import wave
import ssl
import certifi

# Fix SSL certificate verification for downloading Whisper models
ssl._create_default_https_context = ssl._create_unverified_context

# Whisper imports
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    print("Whisper not available. Install with: pip install openai-whisper")

# Configuration
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_DURATION = 5  # Process every 5 seconds (Whisper works better with longer chunks)
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
            print(f"    Channels: {device['max_input_channels']}, Sample Rate: {device['default_samplerate']}")
    print("=" * 40)
    return devices


def audio_callback(indata, frames, time, status):
    """Callback for audio stream"""
    if status:
        print(f"Audio status: {status}", file=sys.stderr)
    audio_queue.put(indata.copy())


def transcribe_worker_whisper(model_name="base"):
    """
    Worker thread using Whisper for transcription
    Models: tiny, base, small, medium, large
    - tiny: fastest, lowest quality
    - base: good balance (recommended for POC)
    - small: better quality, slower
    """
    global is_recording

    if not WHISPER_AVAILABLE:
        print("Whisper not available!")
        return

    print(f"\nLoading Whisper model '{model_name}'... (this may take a minute)")
    model = whisper.load_model(model_name)
    print("Model loaded! ✓")

    session_file = OUTPUT_DIR / f"transcript_whisper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    print(f"Transcript will be saved to: {session_file}")

    with open(session_file, 'w') as f:
        f.write(f"Recording Session: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Model: Whisper {model_name}\n")
        f.write("=" * 60 + "\n\n")

    audio_chunks = []
    chunk_counter = 0

    while is_recording or not audio_queue.empty():
        try:
            chunk = audio_queue.get(timeout=1)
            audio_chunks.append(chunk)

            # Process accumulated audio
            if len(audio_chunks) >= int(CHUNK_DURATION * SAMPLE_RATE / 1024):
                chunk_counter += 1
                audio_data = np.concatenate(audio_chunks).flatten()
                audio_chunks = []

                print(f"\n[Chunk {chunk_counter}] Transcribing with Whisper...", end=" ")

                try:
                    # Whisper expects float32 audio normalized to [-1, 1]
                    audio_float = audio_data.astype(np.float32)

                    # Transcribe
                    result = model.transcribe(audio_float, language="en", fp16=False)
                    text = result["text"].strip()

                    if text:
                        timestamp = datetime.now().strftime('%H:%M:%S')
                        print(f"✓")
                        print(f"[{timestamp}] {text}")

                        # Write to file
                        with open(session_file, 'a') as f:
                            f.write(f"[{timestamp}] {text}\n")

                            # Also write detected language confidence if available
                            if "language" in result:
                                f.write(f"    (Language: {result['language']}, "
                                       f"Confidence: {result.get('language_probability', 0):.2f})\n")
                    else:
                        print("✗ (no speech detected)")

                except Exception as e:
                    print(f"✗ Error: {e}")

        except queue.Empty:
            continue
        except KeyboardInterrupt:
            break

    print(f"\nSession transcript saved to: {session_file}")


def main():
    global is_recording

    print("=" * 60)
    print("  Audio Recording & Whisper Speech-to-Text POC")
    print("  (Offline, No Internet Required)")
    print("=" * 60)

    if not WHISPER_AVAILABLE:
        print("\nERROR: Whisper not installed!")
        print("Install with: pip install openai-whisper")
        print("\nNote: Whisper also requires ffmpeg:")
        print("  macOS: brew install ffmpeg")
        print("  Linux: sudo apt install ffmpeg")
        sys.exit(1)

    # List devices
    devices = list_audio_devices()

    # Select device
    device_input = input("\nEnter device number (or press Enter for default): ").strip()
    device_id = None

    if device_input:
        try:
            device_id = int(device_input)
            device_name = devices[device_id]['name']
            print(f"\nUsing device: [{device_id}] {device_name}")
        except (ValueError, IndexError):
            print("Invalid device number. Using default device.")

    if device_id is None:
        print("\nUsing default input device")

    # Ask for model selection
    print("\nWhisper model options:")
    print("  1. tiny   - Fastest, lowest quality")
    print("  2. base   - Good balance (RECOMMENDED)")
    print("  3. small  - Better quality, slower")
    model_choice = input("Select model (1/2/3) [default: 2]: ").strip()

    model_map = {"1": "tiny", "2": "base", "3": "small"}
    model_name = model_map.get(model_choice, "base")

    # Start transcription worker
    transcribe_thread = threading.Thread(
        target=transcribe_worker_whisper,
        args=(model_name,),
        daemon=True
    )
    transcribe_thread.start()

    print("\n" + "=" * 60)
    print("  Recording started! Speak into your headset.")
    print("  Press Ctrl+C to stop recording.")
    print("=" * 60 + "\n")

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

    print("Finishing transcription...")
    transcribe_thread.join(timeout=15)

    print("\n" + "=" * 60)
    print("  Recording session completed!")
    print(f"  Transcripts saved in: {OUTPUT_DIR}/")
    print("=" * 60)


if __name__ == "__main__":
    main()