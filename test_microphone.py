"""
Microphone Diagnostic Tool
Test your microphone and audio recording
"""

import sounddevice as sd
import numpy as np
import soundfile as sf

print("="*70)
print("🎤 MICROPHONE DIAGNOSTIC TOOL")
print("="*70)

# List available devices
print("\n📋 Available Audio Devices:")
print(sd.query_devices())

# Get default input device
default_device = sd.query_devices(kind='input')
print(f"\n✅ Default Input Device: {default_device['name']}")
print(f"   Sample Rate: {int(default_device['default_samplerate'])} Hz")
print(f"   Channels: {default_device['max_input_channels']}")

# Test recording
print("\n" + "="*70)
print("🔴 RECORDING TEST (5 seconds)")
print("="*70)
print("\n🎤 Recording will start in...")
import time
for i in range(3, 0, -1):
    print(f"   {i}...")
    time.sleep(1)

print("   🔴 RECORDING NOW! Please speak loudly...")

try:
    # Record 5 seconds at 16 kHz
    sample_rate = 16000
    duration = 5
    
    audio = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype='float32'
    )
    sd.wait()
    
    print("   ✅ Recording complete!")
    
    # Analyze audio
    audio = audio.squeeze()
    
    audio_max = np.max(np.abs(audio))
    audio_min = np.min(np.abs(audio))
    audio_rms = np.sqrt(np.mean(audio**2))
    audio_mean = np.mean(np.abs(audio))
    
    print("\n" + "="*70)
    print("📊 AUDIO ANALYSIS")
    print("="*70)
    
    print(f"\n📈 Signal Levels:")
    print(f"   Max amplitude: {audio_max:.6f}")
    print(f"   Min amplitude: {audio_min:.6f}")
    print(f"   RMS (average): {audio_rms:.6f}")
    print(f"   Mean absolute: {audio_mean:.6f}")
    
    print(f"\n🎯 Threshold Checks:")
    print(f"   Required max: 0.01")
    print(f"   Your max: {audio_max:.6f}")
    
    if audio_max < 0.001:
        print("\n❌ CRITICAL: Almost silent!")
        print("   - Microphone might be muted")
        print("   - Check Windows Sound Settings")
    elif audio_max < 0.01:
        print("\n⚠️  WARNING: Very quiet recording")
        print("   - Speak louder")
        print("   - Increase microphone boost in Windows")
        print("   - Move closer to microphone")
    elif audio_max < 0.1:
        print("\n✅ GOOD: Moderate level (authentication will work)")
    else:
        print("\n✅ EXCELLENT: Strong signal!")
    
    # Save for inspection
    output_file = "mic_test.wav"
    sf.write(output_file, audio, sample_rate)
    print(f"\n💾 Audio saved to: {output_file}")
    print("   You can play this file to hear what was recorded")
    
    # Suggest next steps
    print("\n" + "="*70)
    print("💡 RECOMMENDATIONS")
    print("="*70)
    
    if audio_max >= 0.01:
        print("\n✅ Your microphone is working!")
        print("\n📝 Next steps:")
        print("   1. Re-enroll your voice profile in the main app")
        print("   2. Make sure to speak at the same volume")
        print("   3. Use the same environment (room, noise level)")
    else:
        print("\n❌ Microphone issue detected!")
        print("\n🔧 Try these fixes:")
        print("   1. Check microphone is plugged in")
        print("   2. Open Windows Sound Settings:")
        print("      - Right-click speaker icon")
        print("      - 'Sounds' → 'Recording' tab")
        print("      - Select microphone → 'Properties'")
        print("      - Set levels to 80-100%")
        print("   3. Grant microphone permissions:")
        print("      - Settings → Privacy → Microphone")
        print("      - Enable for desktop apps")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\n🔧 Possible issues:")
    print("   - No microphone detected")
    print("   - Microphone permissions denied")
    print("   - Audio driver issues")

print("\n" + "="*70)
print("Test complete!")
print("="*70)
