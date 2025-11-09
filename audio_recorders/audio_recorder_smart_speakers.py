#!/usr/bin/env python3
"""
POC: Audio Recording with Smart Speaker Detection
Uses audio features (pitch, energy, spectral features) to distinguish speakers
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
from collections import deque

# Fix SSL
ssl._create_default_https_context = ssl._create_unverified_context

# Imports
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    print("Whisper not available. Install with: pip install openai-whisper")

# Configuration
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_DURATION = 8  # Process every 8 seconds
OUTPUT_DIR = Path("transcripts")
AUDIO_DIR = Path("recordings")

OUTPUT_DIR.mkdir(exist_ok=True)
AUDIO_DIR.mkdir(exist_ok=True)

audio_queue = queue.Queue()
is_recording = True


class SpeakerTracker:
    """
    Track speakers based on voice characteristics
    Uses pitch and spectral centroid to distinguish voices
    """
    def __init__(self):
        self.speaker_profiles = []  # List of (pitch_mean, spectral_mean) tuples
        self.speaker_history = deque(maxlen=5)  # Last 5 speaker IDs

    def extract_features(self, audio_data):
        """Extract pitch and spectral features from audio"""
        if len(audio_data) == 0:
            return None, None

        # Calculate pitch (fundamental frequency) using autocorrelation
        # Higher pitch typically = different speaker
        autocorr = np.correlate(audio_data, audio_data, mode='full')
        autocorr = autocorr[len(autocorr)//2:]

        # Find peaks in autocorrelation
        if len(autocorr) > 100:
            # Look for fundamental frequency between 80-400 Hz (typical speech)
            min_period = int(SAMPLE_RATE / 400)  # 400 Hz
            max_period = int(SAMPLE_RATE / 80)   # 80 Hz

            if max_period < len(autocorr):
                autocorr_slice = autocorr[min_period:max_period]
                if len(autocorr_slice) > 0:
                    peak_idx = np.argmax(autocorr_slice)
                    fundamental_freq = SAMPLE_RATE / (peak_idx + min_period)
                else:
                    fundamental_freq = 150  # Default
            else:
                fundamental_freq = 150
        else:
            fundamental_freq = 150

        # Calculate spectral centroid (brightness of sound)
        # Different speakers have different spectral characteristics
        fft = np.fft.rfft(audio_data)
        magnitude = np.abs(fft)
        freqs = np.fft.rfftfreq(len(audio_data), 1/SAMPLE_RATE)

        if np.sum(magnitude) > 0:
            spectral_centroid = np.sum(freqs * magnitude) / np.sum(magnitude)
        else:
            spectral_centroid = 1000

        return fundamental_freq, spectral_centroid

    def identify_speaker(self, audio_data):
        """
        Identify which speaker is talking based on voice features
        Returns speaker ID (1, 2, 3, etc.)
        """
        pitch, spectral = self.extract_features(audio_data)

        if pitch is None or spectral is None:
            return 1

        # More lenient threshold - voices vary naturally
        # Typical pitch variation: 50-80 Hz is same person
        # Spectral variation: 800-1200 Hz is same person
        match_threshold = 150  # Much more lenient!

        best_match = None
        best_distance = float('inf')

        for idx, (stored_pitch, stored_spectral) in enumerate(self.speaker_profiles):
            # Calculate distance in feature space
            pitch_diff = abs(pitch - stored_pitch)
            spectral_diff = abs(spectral - stored_spectral)

            # Weighted distance - pitch is more reliable
            distance = (pitch_diff * 2) + (spectral_diff / 10)

            if distance < best_distance:
                best_distance = distance
                best_match = idx

        # If close match found, return that speaker
        if best_match is not None and best_distance < match_threshold:
            speaker_id = best_match + 1
        else:
            # Only create new speaker if REALLY different
            # AND we don't have too many already
            if len(self.speaker_profiles) < 10:  # Cap at 10 speakers max
                self.speaker_profiles.append((pitch, spectral))
                speaker_id = len(self.speaker_profiles)
            else:
                # Too many speakers, just use closest match
                speaker_id = best_match + 1 if best_match is not None else 1

        # Track speaker history for smoothing
        self.speaker_history.append(speaker_id)

        # Use most common speaker in recent history (smoothing)
        if len(self.speaker_history) >= 3:
            from collections import Counter
            counter = Counter(self.speaker_history)
            most_common = counter.most_common(1)[0][0]
            return most_common

        return speaker_id

    def get_speaker_info(self):
        """Get summary of detected speakers"""
        return {
            'total_speakers': len(self.speaker_profiles),
            'profiles': [
                {
                    'speaker_id': i+1,
                    'pitch': f"{pitch:.1f} Hz",
                    'spectral': f"{spectral:.1f} Hz"
                }
                for i, (pitch, spectral) in enumerate(self.speaker_profiles)
            ]
        }


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


def transcribe_with_smart_speakers(model_name="base"):
    """
    Transcribe audio with intelligent speaker detection
    """
    global is_recording

    print(f"\nLoading Whisper model '{model_name}'...")
    model = whisper.load_model(model_name)
    print("Model loaded! ✓")

    speaker_tracker = SpeakerTracker()

    session_file = OUTPUT_DIR / f"transcript_smart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    audio_file = AUDIO_DIR / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"

    print(f"Transcript will be saved to: {session_file}")
    print(f"Audio will be saved to: {audio_file}")

    with open(session_file, 'w') as f:
        f.write(f"Recording Session with Smart Speaker Detection\n")
        f.write(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Model: Whisper {model_name}\n")
        f.write("=" * 70 + "\n\n")

    audio_chunks = []
    all_audio = []
    chunk_counter = 0

    print("\n" + "=" * 70)
    print("  Recording started! Smart speaker detection enabled.")
    print("  System will learn to recognize different voices automatically.")
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
                    # Identify speaker based on voice features
                    speaker_id = speaker_tracker.identify_speaker(audio_data)

                    # Transcribe
                    audio_float = audio_data.astype(np.float32)
                    result = model.transcribe(audio_float, language="en", fp16=False)
                    text = result["text"].strip()

                    if text:
                        timestamp = datetime.now().strftime('%H:%M:%S')
                        print(f"✓")

                        # Display with speaker label
                        print(f"[Speaker {speaker_id}] [{timestamp}] {text}")

                        # Write to file
                        with open(session_file, 'a') as f:
                            f.write(f"[Speaker {speaker_id}] [{timestamp}]\n")
                            f.write(f"{text}\n\n")
                    else:
                        print("✗ (silence/noise)")

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
        print(f"\nSaving audio recording...")
        audio_data = np.concatenate(all_audio).flatten()
        audio_int16 = (audio_data * 32767).astype(np.int16)

        with wave.open(str(audio_file), 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(audio_int16.tobytes())

        print(f"✓ Audio saved: {audio_file}")

    # Save speaker info
    speaker_info = speaker_tracker.get_speaker_info()
    print(f"\n✓ Detected {speaker_info['total_speakers']} unique speaker(s)")

    if speaker_info['total_speakers'] > 0:
        print("\nSpeaker Voice Profiles:")
        for profile in speaker_info['profiles']:
            print(f"  Speaker {profile['speaker_id']}: "
                  f"Pitch={profile['pitch']}, "
                  f"Spectral={profile['spectral']}")

    # Write speaker summary to file
    with open(session_file, 'a') as f:
        f.write("\n" + "=" * 70 + "\n")
        f.write("SESSION SUMMARY\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Total Unique Speakers Detected: {speaker_info['total_speakers']}\n\n")
        if speaker_info['total_speakers'] > 0:
            f.write("Speaker Profiles:\n")
            for profile in speaker_info['profiles']:
                f.write(f"  Speaker {profile['speaker_id']}: "
                       f"Pitch={profile['pitch']}, "
                       f"Spectral={profile['spectral']}\n")

    print(f"\n✓ Transcript saved: {session_file}")


def main():
    global is_recording

    print("=" * 70)
    print("  Audio Recording with SMART Speaker Detection POC")
    print("  Learns to recognize different voices automatically!")
    print("=" * 70)

    if not WHISPER_AVAILABLE:
        print("\nERROR: Whisper not installed!")
        print("Install with: pip install openai-whisper")
        sys.exit(1)

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
        target=transcribe_with_smart_speakers,
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