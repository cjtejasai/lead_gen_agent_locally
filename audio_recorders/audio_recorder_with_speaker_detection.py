#!/usr/bin/env python3
"""
Final POC: Audio Recording with Post-Processing Speaker Detection
Records in real-time, transcribes, then identifies speakers at the end
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
    import torch
    PYANNOTE_AVAILABLE = True
except ImportError:
    PYANNOTE_AVAILABLE = False

# Configuration
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_DURATION = 8  # Transcribe every 8 seconds
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


def transcribe_and_record(model_name="base"):
    """
    Record and transcribe in real-time
    Returns list of (timestamp, text) tuples and audio data
    """
    global is_recording

    print(f"\nLoading Whisper model '{model_name}'...")
    model = whisper.load_model(model_name)
    print("✓ Whisper loaded\n")

    audio_chunks = []
    all_audio = []
    transcripts = []  # Store (start_time, end_time, text) tuples
    chunk_counter = 0
    start_time = datetime.now()

    print("=" * 70)
    print("  Recording started! Speak naturally.")
    print("  Press Ctrl+C to stop and process speakers.")
    print("=" * 70 + "\n")

    while is_recording or not audio_queue.empty():
        try:
            chunk = audio_queue.get(timeout=1)
            audio_chunks.append(chunk)
            all_audio.append(chunk)

            # Transcribe every CHUNK_DURATION seconds
            if len(audio_chunks) >= int(CHUNK_DURATION * SAMPLE_RATE / 1024):
                chunk_counter += 1
                audio_data = np.concatenate(audio_chunks).flatten()
                audio_chunks = []

                print(f"[Chunk {chunk_counter}] Transcribing...", end=" ")

                try:
                    # Transcribe
                    audio_float = audio_data.astype(np.float32)
                    result = model.transcribe(audio_float, language="en", fp16=False)
                    text = result["text"].strip()

                    if text:
                        # Calculate time in recording
                        elapsed = (datetime.now() - start_time).total_seconds()
                        chunk_start = elapsed - CHUNK_DURATION
                        chunk_end = elapsed

                        transcripts.append((chunk_start, chunk_end, text))

                        timestamp = datetime.now().strftime('%H:%M:%S')
                        print(f"✓")
                        print(f"[{timestamp}] {text}\n")
                    else:
                        print("✗ (silence)\n")

                except Exception as e:
                    print(f"✗ Error: {e}\n")

        except queue.Empty:
            continue
        except KeyboardInterrupt:
            break

    # Return transcripts and full audio
    full_audio = np.concatenate(all_audio).flatten() if all_audio else np.array([])
    return transcripts, full_audio


def add_speakers_to_transcript(audio_file, transcripts, hf_token=None):
    """
    Run speaker diarization on the full audio and match to transcripts
    """
    if not PYANNOTE_AVAILABLE:
        print("\n⚠️  pyannote.audio not available, cannot detect speakers")
        return [(start, end, "Unknown", text) for start, end, text in transcripts]

    print("\n" + "=" * 70)
    print("  Running speaker detection on full recording...")
    print("  This may take a minute...")
    print("=" * 70 + "\n")

    try:
        # Load diarization pipeline
        pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            token=hf_token if hf_token else True
        )

        # Load the WAV file manually and convert to tensor
        import wave
        import torch

        with wave.open(str(audio_file), 'rb') as wf:
            # Read audio data
            frames = wf.readframes(wf.getnframes())
            # Convert to numpy array
            audio_data = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
            # Convert to torch tensor
            waveform = torch.from_numpy(audio_data).unsqueeze(0)

        # Create audio input dict for pyannote
        audio_input = {
            "waveform": waveform,
            "sample_rate": SAMPLE_RATE
        }

        # Suppress warnings during diarization
        import warnings
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore')
            # Run diarization on the audio tensor
            diarize_output = pipeline(audio_input)

        # Extract the actual Annotation from DiarizeOutput
        # In pyannote 4.0+, pipeline returns DiarizeOutput with .speaker_diarization attribute
        if hasattr(diarize_output, 'speaker_diarization'):
            diarization = diarize_output.speaker_diarization
        else:
            diarization = diarize_output

        print("✓ Speaker detection complete!\n")

        # Match speakers to transcript segments
        results = []
        for start, end, text in transcripts:
            # Find which speaker was talking during this time
            segment_mid = (start + end) / 2
            speaker = "Unknown"

            # Check each diarization segment
            for segment, _, label in diarization.itertracks(yield_label=True):
                if segment.start <= segment_mid <= segment.end:
                    speaker = label
                    break

            results.append((start, end, speaker, text))

        # Count speakers
        speakers = set(s for _, _, s, _ in results if s != "Unknown")
        print(f"✓ Detected {len(speakers)} unique speaker(s): {', '.join(sorted(speakers))}\n")

        return results

    except Exception as e:
        print(f"\n⚠️  Speaker detection failed: {e}")
        print("Continuing without speaker labels\n")
        return [(start, end, "Unknown", text) for start, end, text in transcripts]


def main():
    global is_recording

    print("=" * 70)
    print("  Audio Recording with Smart Speaker Detection")
    print("  Transcribes live, identifies speakers at the end")
    print("=" * 70)

    if not WHISPER_AVAILABLE:
        print("\nERROR: Whisper not installed!")
        print("Install with: pip install openai-whisper")
        sys.exit(1)

    # Check for HF token
    hf_token = os.environ.get('HF_TOKEN')
    if hf_token:
        print("✓ Found Hugging Face token in environment")
    elif PYANNOTE_AVAILABLE:
        print("\n💡 For speaker detection, add HF_TOKEN to .env file")
        print("   See: https://huggingface.co/settings/tokens")

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

    # Create output files
    session_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    audio_file = AUDIO_DIR / f"session_{session_time}.wav"
    transcript_file = OUTPUT_DIR / f"transcript_{session_time}.txt"

    # Start recording thread
    transcripts = []
    full_audio = None

    def record_thread():
        nonlocal transcripts, full_audio
        transcripts, full_audio = transcribe_and_record(model_name)

    thread = threading.Thread(target=record_thread, daemon=True)
    thread.start()

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

    print("Finishing transcription...")
    thread.join(timeout=15)

    if full_audio is None or len(full_audio) == 0:
        print("\n⚠️  No audio recorded")
        return

    # Save audio file
    print(f"\n💾 Saving audio to: {audio_file}")
    audio_int16 = (full_audio * 32767).astype(np.int16)
    with wave.open(str(audio_file), 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio_int16.tobytes())
    print("✓ Audio saved")

    # Run speaker detection
    final_transcripts = add_speakers_to_transcript(audio_file, transcripts, hf_token)

    # Save final transcript with speakers
    print(f"💾 Saving transcript to: {transcript_file}")
    with open(transcript_file, 'w') as f:
        f.write(f"Recording Session with Speaker Detection\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Model: Whisper {model_name} + pyannote diarization\n")
        f.write(f"Duration: {len(full_audio) / SAMPLE_RATE:.1f} seconds\n")
        f.write("=" * 70 + "\n\n")

        for start, end, speaker, text in final_transcripts:
            time_str = f"{int(start//60):02d}:{int(start%60):02d}"
            f.write(f"[{speaker}] [{time_str}]\n")
            f.write(f"{text}\n\n")

        # Summary
        f.write("\n" + "=" * 70 + "\n")
        f.write("SESSION SUMMARY\n")
        f.write("=" * 70 + "\n\n")

        speakers = {}
        for _, _, speaker, _ in final_transcripts:
            speakers[speaker] = speakers.get(speaker, 0) + 1

        f.write(f"Total segments: {len(final_transcripts)}\n")
        f.write(f"Unique speakers: {len([s for s in speakers.keys() if s != 'Unknown'])}\n\n")

        for speaker, count in sorted(speakers.items()):
            f.write(f"{speaker}: {count} segments\n")

    print("✓ Transcript saved\n")

    print("=" * 70)
    print("  Recording completed successfully!")
    print(f"  Audio: {audio_file}")
    print(f"  Transcript: {transcript_file}")
    print("=" * 70)


if __name__ == "__main__":
    main()