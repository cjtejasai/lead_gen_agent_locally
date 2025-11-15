#!/usr/bin/env python3
"""
Simple test script - just record 10 seconds of audio and show you what happens
No transcription, just testing if audio recording works
"""

import sounddevice as sd
import numpy as np
from datetime import datetime

print("=" * 70)
print("  SIMPLE AUDIO TEST")
print("  This will record 10 seconds of audio from your device")
print("=" * 70)

# Show devices
print("\n📱 Available Input Devices:\n")
devices = sd.query_devices()
for idx, device in enumerate(devices):
    if device['max_input_channels'] > 0:
        print(f"[{idx}] {device['name']}")

# Select device
device_input = input("\nSelect device number (or press Enter for default): ").strip()
device_id = None
if device_input:
    try:
        device_id = int(device_input)
        print(f"\n✓ Using device: {devices[device_id]['name']}")
    except:
        print("\n✓ Using default device")

# Record settings
duration = 10  # seconds
sample_rate = 16000

print(f"\n🎤 Recording for {duration} seconds...")
print("   Speak into your microphone/headset now!")
print("   " + "-" * 50)

try:
    # Record audio
    recording = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        device=device_id,
        dtype='float32'
    )

    # Show progress
    for i in range(duration):
        sd.sleep(1000)  # 1 second

        # Calculate volume level (simple amplitude)
        if i > 0:
            chunk = recording[i*sample_rate:(i+1)*sample_rate]
            volume = np.abs(chunk).mean() * 100
            bars = int(volume * 50)
            bar_display = "█" * min(bars, 50)
            print(f"   Second {i+1:2d}: {bar_display} ({volume:.1f})")

    sd.wait()  # Wait for recording to finish

    print("   " + "-" * 50)
    print("\n✅ Recording complete!")

    # Calculate statistics
    max_amplitude = np.abs(recording).max()
    mean_amplitude = np.abs(recording).mean()

    print(f"\n📊 Audio Statistics:")
    print(f"   Duration: {duration} seconds")
    print(f"   Sample Rate: {sample_rate} Hz")
    print(f"   Max Amplitude: {max_amplitude:.4f}")
    print(f"   Mean Amplitude: {mean_amplitude:.4f}")

    if mean_amplitude < 0.001:
        print("\n⚠️  WARNING: Very low audio level detected!")
        print("   Possible issues:")
        print("   1. Microphone is muted")
        print("   2. Wrong device selected")
        print("   3. Microphone permissions not granted")
        print("\n   Check: System Settings > Privacy & Security > Microphone")
    elif mean_amplitude < 0.01:
        print("\n⚠️  Audio level is low. Try speaking louder or closer to mic.")
    else:
        print("\n✅ Audio level looks good! Your microphone is working.")

    # Save to file
    import soundfile as sf
    filename = f"test_recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
    sf.write(filename, recording, sample_rate)
    print(f"\n💾 Saved to: {filename}")
    print("   You can play this file to hear what was recorded.")

except KeyboardInterrupt:
    print("\n\n⚠️  Recording interrupted!")
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nPossible fixes:")
    print("1. Check microphone permissions")
    print("2. Try a different device")
    print("3. Make sure device is not being used by another app")

print("\n" + "=" * 70)