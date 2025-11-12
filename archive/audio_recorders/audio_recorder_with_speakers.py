#!/usr/bin/env python3
"""
POC: Audio Recording with Speaker Diarization
Detects WHO is speaking (Speaker 1, Speaker 2, etc.)
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
CHUNK_DURATION = 10  # Process every 10 seconds for better speaker detection
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


def simple_speaker_detection(audio_data, threshold=0.02):
    """
    Simple speaker change detection based on volume/energy changes
    This is a basic approach - not as good as ML models but works offline

    Returns: estimated number of speaker changes
    """
    # Split audio into small segments
    segment_length = SAMPLE_RATE // 4  # 250ms segments
    num_segments = len(audio_data) // segment_length

    energies = []
    for i in range(num_segments):
        segment = audio_data[i*segment_length:(i+1)*segment_length]
        energy = np.sqrt(np.mean(segment**2))
        energies.append(energy)

    if not energies:
        return 1

    # Detect significant energy changes (potential speaker changes)
    energies = np.array(energies)
    mean_energy = np.mean(energies)

    # Normalize
    if mean_energy > 0:
        energies = energies / mean_energy

    # Count changes
    changes = 0
    for i in range(1, len(energies)):
        if abs(energies[i] - energies[i-1]) > threshold:
            changes += 1

    # Estimate speakers (rough heuristic)
    estimated_speakers = min(1 + changes // 3, 4)  # Cap at 4 speakers

    return estimated_speakers


def transcribe_with_speakers(model_name="base"):
    """
    Transcribe audio with basic speaker detection
    """
    global is_recording

    print(f"\nLoading Whisper model '{model_name}'...")
    model = whisper.load_model(model_name)
    print("Model loaded! ✓")

    session_file = OUTPUT_DIR / f"transcript_speakers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    audio_file = AUDIO_DIR / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"

    print(f"Transcript will be saved to: {session_file}")
    print(f"Audio will be saved to: {audio_file}")

    with open(session_file, 'w') as f:
        f.write(f"Recording Session with Speaker Detection\n")
        f.write(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Model: Whisper {model_name}\n")
        f.write("=" * 70 + "\n\n")

    audio_chunks = []
    all_audio = []  # Store all audio for final save
    chunk_counter = 0
    current_speaker = 1

    print("\n" + "=" * 70)
    print("  Recording started! Speaker detection enabled.")
    print("  Speak clearly. Pause between speakers for better detection.")
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
                    # Detect potential speaker changes
                    num_speakers = simple_speaker_detection(audio_data)

                    # Transcribe
                    audio_float = audio_data.astype(np.float32)
                    result = model.transcribe(audio_float, language="en", fp16=False)
                    text = result["text"].strip()

                    if text:
                        # Simple speaker assignment (alternates if multiple detected)
                        if num_speakers > 1:
                            # Alternate speaker for chunks with multiple speakers
                            current_speaker = (current_speaker % 2) + 1

                        timestamp = datetime.now().strftime('%H:%M:%S')
                        print(f"✓")

                        # Display with speaker label
                        speaker_label = f"[Speaker {current_speaker}]" if num_speakers > 1 else "[Single Speaker]"
                        print(f"{speaker_label} [{timestamp}] {text}")

                        # Write to file with speaker info
                        with open(session_file, 'a') as f:
                            f.write(f"{speaker_label} [{timestamp}]\n")
                            f.write(f"{text}\n")
                            if num_speakers > 1:
                                f.write(f"(Detected {num_speakers} potential speakers in this segment)\n")
                            f.write("\n")
                    else:
                        print("✗ (silence)")

                except Exception as e:
                    print(f"✗ Error: {e}")

        except queue.Empty:
            continue
        except KeyboardInterrupt:
            break

    # Save audio file
    if all_audio:
        print(f"\nSaving audio recording...")
        audio_data = np.concatenate(all_audio).flatten()
        audio_int16 = (audio_data * 32767).astype(np.int16)

        with wave.open(str(audio_file), 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(audio_int16.tobytes())

        print(f"✓ Audio saved: {audio_file}")

    print(f"✓ Transcript saved: {session_file}")


def main():
    global is_recording

    print("=" * 70)
    print("  Audio Recording with Speaker Detection POC")
    print("=" * 70)

    if not WHISPER_AVAILABLE:
        print("\nERROR: Whisper not installed!")
        print("Install with: pip install openai-whisper")
        sys.exit(1)

    if PYANNOTE_AVAILABLE:
        print("\n✓ Advanced speaker detection available (pyannote)")
    else:
        print("\n⚠ Using basic speaker detection (install pyannote.audio for better results)")
        print("  pip install pyannote.audio")

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
        target=transcribe_with_speakers,
        args=(model_name,),
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
    transcribe_thread.join(timeout=15)

    print("\n" + "=" * 70)
    print("  Recording completed!")
    print(f"  Transcript: {OUTPUT_DIR}/")
    print(f"  Audio: {AUDIO_DIR}/")
    print("=" * 70)


if __name__ == "__main__":
    main()