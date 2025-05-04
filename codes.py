import subprocess
import os
import queue
import speech_recognition as sr
import json
import soundfile as sf
import noisereduce as nr
import numpy as np

# ----- Step 1: Config -----
input_video = "vid.mp4"  # Path to your video file
expected_digits = [1, 7, 8]  # Hardcoded expected digits
model_path = "model"  # Path to CMU Sphinx model folder (this will be handled internally by SpeechRecognition)

# ----- Step 2: Extract Audio from Video Using ffmpeg -----
def extract_audio(video_path, output_wav):
    # Use ffmpeg command to extract audio from video
    command = [
        'ffmpeg', '-i', video_path, '-vn', '-acodec', 'pcm_s16le', 
        '-ar', '16000', '-ac', '1', output_wav
    ]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("[INFO] Audio extracted to:", output_wav)

# ----- Step 3: Noise Reduction -----
def reduce_noise(audio_path, output_path):
    # Load the audio
    data, samplerate = sf.read(audio_path)
    
    # Apply noise reduction
    reduced_noise_data = nr.reduce_noise(y=data, sr=samplerate)
    
    # Save the cleaned audio
    sf.write(output_path, reduced_noise_data, samplerate)
    print("[INFO] Noise reduction applied.")

# ----- Step 4: Recognize Digits from Audio Using SpeechRecognition -----
def recognize_digits(wav_path, expected_digits):
    # Initialize recognizer
    recognizer = sr.Recognizer()

    # Load the audio file
    audio_file = sr.AudioFile(wav_path)

    # Recognize using Sphinx offline engine
    with audio_file as source:
        audio_data = recognizer.record(source)

    # Convert the audio to text using CMU Sphinx
    try:
        print("[INFO] Recognizing...")
        text = recognizer.recognize_sphinx(audio_data)
        print("[INFO] Transcript:", text)

        digit_words = {
            "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
            "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9
        }

        current_index = 0
        words = text.split()

        for word in words:
            if word in digit_words and current_index < len(expected_digits):
                spoken = digit_words[word]
                expected = expected_digits[current_index]
                if spoken == expected:
                    print(f"[{current_index+1}] ✅ Correct: {spoken}")
                    current_index += 1
                else:
                    print(f"[{current_index+1}] ❌ Wrong: {spoken} (Expected {expected})")

        if current_index == len(expected_digits):
            print("\n🎉 All digits spoken correctly in order!")
        else:
            print(f"\n⛔ Only {current_index}/{len(expected_digits)} digits were correct.")
    except sr.UnknownValueError:
        print("[ERROR] Could not understand audio.")
    except sr.RequestError as e:
        print(f"[ERROR] Sphinx error; {e}")

# ----- Step 5: Run Entire Process -----
def process_video(video_path):
    temp_wav = "temp_audio.wav"
    reduced_wav = "reduced_audio.wav"

    # Extract audio from video
    extract_audio(video_path, temp_wav)

    # Apply noise reduction
    reduce_noise(temp_wav, reduced_wav)

    # Recognize digits
    recognize_digits(reduced_wav, expected_digits)

    # Cleanup temporary files
    os.remove(temp_wav)
    os.remove(reduced_wav)

# Run it
if __name__ == "__main__":
    process_video(input_video)
