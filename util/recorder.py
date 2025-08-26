"""Here the User can record the audio and it will be saved in the dataset folder"""

import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import keyboard

def record_audio(filename="recording.wav", samplerate=44100, channels=2):
    print("Recording... Press 'q' to stop.")

    recorded_frames = []

    # Callback function to store audio chunks
    def callback(indata, frames, time, status):
        if status:
            print(status)
        recorded_frames.append(indata.copy())

    # Start streaming
    with sd.InputStream(samplerate=samplerate, channels=channels, callback=callback):
        while True:
            if keyboard.is_pressed('q'):
                print("Recording stopped.")
                break

    # Combine all recorded chunks
    audio_data = np.concatenate(recorded_frames, axis=0)
    
    # Save as WAV file
    write(filename, samplerate, audio_data)
    print(f"Saved recording to {filename}")

def save_recording(audio_bytes, filename):
    """
    Save audio bytes (from API or web client) to a file.
    """
    with open(filename, "wb") as f:
        f.write(audio_bytes)
    print(f"Saved uploaded/recorded audio to {filename}")