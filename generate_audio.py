"""
Generate audio files for the Stacking Plates Game
Run this once to create the required audio files
"""
import numpy as np
from scipy.io import wavfile
import os

def generate_move_sound():
    """Generate a quick 'pop' sound for plate moves"""
    sample_rate = 44100
    duration = 0.15
    frequency = 800
    
    t = np.linspace(0, duration, int(sample_rate * duration))
    # Quick decay envelope
    envelope = np.exp(-t * 15)
    wave = np.sin(2 * np.pi * frequency * t) * envelope
    
    # Normalize and convert to 16-bit
    wave = np.int16(wave * 32767 * 0.5)
    wavfile.write('move.wav', sample_rate, wave)
    print("✓ Created move.wav")

def generate_win_sound():
    """Generate a celebratory win sound"""
    sample_rate = 44100
    duration = 1.0
    
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Ascending chord progression
    frequencies = [523, 659, 784, 1047]  # C, E, G, C (major chord)
    wave = np.zeros_like(t)
    
    for i, freq in enumerate(frequencies):
        start = i * 0.15
        segment = np.where((t >= start) & (t < start + 0.4),
                          np.sin(2 * np.pi * freq * (t - start)) * np.exp(-(t - start) * 3),
                          0)
        wave += segment
    
    # Normalize and convert to 16-bit
    wave = wave / np.max(np.abs(wave))
    wave = np.int16(wave * 32767 * 0.7)
    wavfile.write('win.wav', sample_rate, wave)
    print("✓ Created win.wav")

def generate_background_music():
    """Generate simple looping background music"""
    sample_rate = 44100
    duration = 8.0  # 8 second loop
    
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Simple melody with bass
    melody_notes = [
        (262, 0, 0.5), (294, 0.5, 0.5), (330, 1.0, 0.5), (349, 1.5, 0.5),
        (392, 2.0, 0.5), (349, 2.5, 0.5), (330, 3.0, 0.5), (294, 3.5, 0.5),
        (262, 4.0, 0.5), (294, 4.5, 0.5), (330, 5.0, 0.5), (349, 5.5, 0.5),
        (392, 6.0, 1.0), (262, 7.0, 1.0)
    ]
    
    wave = np.zeros_like(t)
    
    # Add melody
    for freq, start, dur in melody_notes:
        segment = np.where((t >= start) & (t < start + dur),
                          np.sin(2 * np.pi * freq * (t - start)) * 
                          np.exp(-(t - start) * 2) * 0.3,
                          0)
        wave += segment
    
    # Add bass line (octave lower)
    bass_freq = 131  # C3
    bass = np.sin(2 * np.pi * bass_freq * t) * 0.15
    wave += bass
    
    # Normalize and convert to 16-bit
    wave = wave / np.max(np.abs(wave))
    wave = np.int16(wave * 32767 * 0.6)
    
    # Save as WAV first
    wavfile.write('background_temp.wav', sample_rate, wave)
    print("✓ Created background_temp.wav")
    
    # Try to convert to MP3 if pydub is available
    try:
        from pydub import AudioSegment
        audio = AudioSegment.from_wav('background_temp.wav')
        audio.export('background.mp3', format='mp3')
        os.remove('background_temp.wav')
        print("✓ Created background.mp3")
    except ImportError:
        # If pydub not available, rename wav to mp3 (pygame can handle it)
        os.rename('background_temp.wav', 'background.mp3')
        print("✓ Created background.mp3 (as WAV format - pygame will handle it)")

if __name__ == "__main__":
    print("Generating audio files for Stacking Plates Game...")
    print("-" * 50)
    
    try:
        generate_move_sound()
        generate_win_sound()
        generate_background_music()
        print("-" * 50)
        print("✓ All audio files generated successfully!")
        print("\nYou can now run Python_project.py with sound!")
    except Exception as e:
        print(f"✗ Error generating audio: {e}")
        print("\nMake sure you have numpy and scipy installed:")
        print("  pip install numpy scipy")
