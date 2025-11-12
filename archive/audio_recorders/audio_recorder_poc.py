#!/usr/bin/env python3
"""
Simple POC: Real-time Audio Recording and Speech-to-Text
Records audio from your Bluetooth headset and transcribes it to a file
"""

import sounddevice as sd
import numpy as np
import queue
import sys
import json
from datetime import datetime
from pathlib import Path
import threading
import wave

# Speech recognition imports
try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False
    print("SpeechRecognition not available. Install with: pip install SpeechRecognition")

# Configuration
SAMPLE_RATE = 16000  # 16kHz is standard for speech
CHANNELS = 1  # Mono audio
CHUNK_DURATION = 3  # Process audio every 3 seconds
OUTPUT_DIR = Path("transcripts")
AUDIO_DIR = Path("recordings")

# Create output directories
OUTPUT_DIR.mkdir(exist_ok=True)
AUDIO_DIR.mkdir(exist_ok=True)

# Queue for audio chunks
audio_queue = queue.Queue()
transcript_queue = queue.Queue()

# Global flag for stopping
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
    """Callback function for audio stream"""
    if status:
        print(f"Audio status: {status}", file=sys.stderr)
    # Put audio data in queue for processing
    audio_queue.put(indata.copy())


def transcribe_worker():
    """Worker thread that processes audio chunks and transcribes them"""
    global is_recording

    if not SR_AVAILABLE:
        print("Speech recognition not available!")
        return

    recognizer = sr.Recognizer()
    session_file = OUTPUT_DIR / f"transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    print(f"\nTranscript will be saved to: {session_file}")

    with open(session_file, 'w') as f:
        f.write(f"Recording Session: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n\n")

    audio_chunks = []
    chunk_counter = 0

    while is_recording or not audio_queue.empty():
        try:
            # Collect audio chunks for processing
            chunk = audio_queue.get(timeout=1)
            audio_chunks.append(chunk)

            # Process every few seconds
            if len(audio_chunks) >= int(CHUNK_DURATION * SAMPLE_RATE / 1024):
                chunk_counter += 1
                audio_data = np.concatenate(audio_chunks)
                audio_chunks = []

                # Convert to int16 for speech recognition
                audio_int16 = (audio_data * 32767).astype(np.int16)
                audio_bytes = audio_int16.tobytes()

                # Create AudioData object for speech recognition
                audio_segment = sr.AudioData(audio_bytes, SAMPLE_RATE, 2)

                try:
                    # Transcribe using Google Speech Recognition (free, no API key needed)
                    print(f"\n[Chunk {chunk_counter}] Transcribing...", end=" ")
                    text = recognizer.recognize_google(audio_segment)

                    timestamp = datetime.now().strftime('%H:%M:%S')
                    print(f"✓")
                    print(f"[{timestamp}] {text}")

                    # Write to file
                    with open(session_file, 'a') as f:
                        f.write(f"[{timestamp}] {text}\n")

                    # Also send to queue for further processing
                    transcript_queue.put({
                        'timestamp': timestamp,
                        'text': text,
                        'chunk': chunk_counter
                    })

                except sr.UnknownValueError:
                    print("✗ (unclear audio)")
                except sr.RequestError as e:
                    print(f"✗ Error: {e}")
                except Exception as e:
                    print(f"✗ Error: {e}")

        except queue.Empty:
            continue
        except KeyboardInterrupt:
            break

    print(f"\nSession transcript saved to: {session_file}")


def save_audio_worker():
    """Optional worker to save raw audio to WAV file"""
    global is_recording

    audio_file = AUDIO_DIR / f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"

    all_audio = []

    while is_recording:
        try:
            chunk = audio_queue.get(timeout=0.5)
            all_audio.append(chunk)
        except queue.Empty:
            continue

    if all_audio:
        print(f"\nSaving audio recording to: {audio_file}")
        audio_data = np.concatenate(all_audio)

        # Save as WAV
        with wave.open(str(audio_file), 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(SAMPLE_RATE)
            audio_int16 = (audio_data * 32767).astype(np.int16)
            wf.writeframes(audio_int16.tobytes())

        print(f"Audio saved: {audio_file}")


def main():
    global is_recording

    print("=" * 60)
    print("  Audio Recording & Speech-to-Text POC")
    print("=" * 60)

    # List available devices
    devices = list_audio_devices()

    # Ask user to select device
    print("\nYour Bluetooth headset should appear in the list above.")
    print("If not visible, make sure it's connected and paired.")
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

    # Start transcription worker thread
    transcribe_thread = threading.Thread(target=transcribe_worker, daemon=True)
    transcribe_thread.start()

    print("\n" + "=" * 60)
    print("  Recording started! Speak into your headset.")
    print("  Press Ctrl+C to stop recording.")
    print("=" * 60 + "\n")

    try:
        # Start audio stream
        with sd.InputStream(
            device=device_id,
            channels=CHANNELS,
            samplerate=SAMPLE_RATE,
            callback=audio_callback,
            blocksize=1024
        ):
            # Keep recording until interrupted
            while is_recording:
                sd.sleep(1000)

    except KeyboardInterrupt:
        print("\n\nStopping recording...")
        is_recording = False
    except Exception as e:
        print(f"\nError: {e}")
        is_recording = False

    # Wait for transcription to finish
    print("Finishing transcription...")
    transcribe_thread.join(timeout=10)

    print("\n" + "=" * 60)
    print("  Recording session completed!")
    print(f"  Transcripts saved in: {OUTPUT_DIR}/")
    print("=" * 60)


if __name__ == "__main__":
    if not SR_AVAILABLE:
        print("\nERROR: SpeechRecognition not installed!")
        print("Install it with: pip install SpeechRecognition")
        sys.exit(1)

    main()