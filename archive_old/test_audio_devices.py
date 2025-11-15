#!/usr/bin/env python3
"""
Quick test script to check available audio devices
Run this first to make sure your Bluetooth headset is detected
"""

try:
    import sounddevice as sd
    print("✓ sounddevice is installed\n")
except ImportError:
    print("✗ sounddevice not installed")
    print("Install with: pip install sounddevice")
    exit(1)

print("=" * 70)
print("  AUDIO DEVICE DETECTION TEST")
print("=" * 70)

# Get all devices
devices = sd.query_devices()

print("\n📝 ALL AUDIO DEVICES:\n")
for idx, device in enumerate(devices):
    print(f"[{idx}] {device['name']}")
    print(f"    Max Input Channels:  {device['max_input_channels']}")
    print(f"    Max Output Channels: {device['max_output_channels']}")
    print(f"    Default Sample Rate: {device['default_samplerate']} Hz")
    print()

print("=" * 70)
print("\n📱 INPUT DEVICES (Microphones/Headsets):\n")

input_devices = []
for idx, device in enumerate(devices):
    if device['max_input_channels'] > 0:
        input_devices.append((idx, device))
        print(f"[{idx}] {device['name']}")

        # Highlight potential Bluetooth devices
        name_lower = device['name'].lower()
        if any(keyword in name_lower for keyword in ['bluetooth', 'boat', 'wireless', 'bt']):
            print(f"    👉 This looks like a Bluetooth device!")

        print(f"    Channels: {device['max_input_channels']}")
        print(f"    Sample Rate: {device['default_samplerate']} Hz")
        print()

if not input_devices:
    print("⚠️  No input devices found!")
    print("    Make sure your Bluetooth headset is:")
    print("    1. Turned on")
    print("    2. Paired with this laptop")
    print("    3. Connected (not just paired)")
    print("    4. Set as input device in System Settings")
else:
    print(f"✓ Found {len(input_devices)} input device(s)")

print("=" * 70)
print("\n🎤 DEFAULT INPUT DEVICE:\n")

try:
    default_input = sd.query_devices(kind='input')
    print(f"Device: {default_input['name']}")
    print(f"Channels: {default_input['max_input_channels']}")
    print(f"Sample Rate: {default_input['default_samplerate']} Hz")
except Exception as e:
    print(f"⚠️  Could not detect default input device: {e}")

print("\n" + "=" * 70)
print("\n💡 NEXT STEPS:")
print("\n1. If you see your Bluetooth headset above, you're good to go!")
print("2. Note the device number (in brackets)")
print("3. Run: python audio_recorder_poc.py")
print("   or: python audio_recorder_whisper.py")
print("4. Enter the device number when prompted")
print("\n" + "=" * 70)