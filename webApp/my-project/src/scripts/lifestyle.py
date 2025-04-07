import cv2
import urllib.request
import numpy as np
import pyttsx3
import sounddevice as sd
import tensorflow_hub as hub
import librosa
import tensorflow as tf
import time

print("Starting lifestyle.py scanner...")

# Initialize TTS engine.
engine = pyttsx3.init()
def speak(text):
    print("TTS:", text)
    engine.say(text)
    engine.runAndWait()

print("Loading YAMNet model...")
yamnet_model = hub.load('https://tfhub.dev/google/yamnet/1')
print("YAMNet loaded.")
class_map_path = yamnet_model.class_map_path().numpy().decode('utf-8')
class_names = [line.strip() for line in tf.io.gfile.GFile(class_map_path).readlines()]
print("YAMNet class names loaded.")

# Use same camera URL as object_detection.py.
CAMERA_URL = 'http://10.69.80.108:8080/shot.jpg?resolution=1280x720'
print("Lifestyle using CAMERA_URL:", CAMERA_URL)

# Timers and thresholds.
last_water_alert_time = 0  
water_alert_cooldown = 5  # seconds
brightness_threshold = 80
last_light_alert_time = 0
light_alert_interval = 20  # seconds

while True:
    try:
        print("Lifestyle: Fetching frame...")
        req = urllib.request.urlopen(CAMERA_URL, timeout=5)
        arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
        frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if frame is None:
            print("Lifestyle: Received empty frame.")
            time.sleep(0.5)
            continue
    except Exception as e:
        print("Lifestyle: Error fetching frame:", e)
        time.sleep(1)
        continue

    frame = cv2.resize(frame, (1280, 720))
    
    # Light detection.
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    avg_brightness = np.mean(gray)
    brightness_status = "ON" if avg_brightness > brightness_threshold else "OFF"
    cv2.putText(frame, f"Light: {brightness_status}", (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    current_time = time.time()
    if brightness_status == "ON" and (current_time - last_light_alert_time > light_alert_interval):
        print("Lifestyle: Light alert triggered.")
        speak("The light is on, please turn it off.")
        last_light_alert_time = current_time

    # Water detection.
    if current_time - last_water_alert_time > water_alert_cooldown:
        duration = 2  # seconds
        sample_rate = 16000
        try:
            print("Lifestyle: Recording audio...")
            audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
            sd.wait()
            print("Lifestyle: Audio recording complete.")
            if audio.ndim > 1:
                audio = np.mean(audio, axis=1)
            waveform = np.squeeze(np.array(audio, dtype=np.float32))
            scores, embeddings, spectrogram = yamnet_model(waveform)
            mean_scores = np.mean(scores, axis=0)
            predicted_class_index = int(np.argmax(mean_scores))
            detected_sound = class_names[predicted_class_index]
            print("Lifestyle: Detected sound:", detected_sound)
            # Use case-insensitive matching.
            water_keywords = ["water", "stream", "faucet", "bee wasp", "toilet flush", "thunder", "crack", "splash",
                              "ratchet", "shatter", "croak", "pulse", "steam whistle", "squish"]
            if any(keyword in detected_sound.lower() for keyword in water_keywords):
                print("Lifestyle: Running water detected!")
                speak("Running water detected. Please close the tap.")
                last_water_alert_time = current_time
        except Exception as e:
            print("Lifestyle: Audio recording error:", e)

    cv2.imshow('Lifestyle Scanner', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Lifestyle: Exiting scanner.")
        break
    time.sleep(0.1)

cv2.destroyAllWindows()
