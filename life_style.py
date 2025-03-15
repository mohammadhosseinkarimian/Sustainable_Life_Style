import cv2
import urllib.request
import numpy as np
import pyttsx3
import sounddevice as sd
import tensorflow_hub as hub
import librosa
import tensorflow as tf
import time  # Import time module for tracking alerts

# ✅ Initialize Text-to-Speech engine
engine = pyttsx3.init()

def speak(text):
    """Speaks the provided text using pyttsx3."""
    engine.say(text)
    engine.runAndWait()

# ✅ Load the YAMNet model from TensorFlow Hub
yamnet_model = hub.load('https://tfhub.dev/google/yamnet/1')

# ✅ Extract class labels directly from YAMNet model
class_map_path = yamnet_model.class_map_path().numpy().decode('utf-8')
class_names = [line.strip() for line in tf.io.gfile.GFile(class_map_path).readlines()]

# ✅ IP Webcam URL
url = 'http://10.69.80.108:8080/shot.jpg?resolution=1280x720'

# ✅ Cooldown timer for water detection alerts
last_water_alert_time = 0  
water_alert_cooldown = 50  # seconds

def detect_running_water():
    """Records and detects running water using the YAMNet model."""
    global last_water_alert_time  

    duration = 2  # seconds
    sample_rate = 16000

    print("🎙 Recording audio...")
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
    sd.wait()
    print("✅ Audio recording complete.")

    # ✅ Convert stereo to mono if needed
    if audio.ndim > 1:
        audio = np.mean(audio, axis=1)

    # ✅ Resample if necessary
    if sample_rate != 16000:
        audio = librosa.resample(audio, orig_sr=sample_rate, target_sr=16000)

    # ✅ Ensure correct shape
    waveform = np.array(audio, dtype=np.float32)
    waveform = np.squeeze(waveform)

    # ✅ Run YAMNet model on the processed audio
    scores, embeddings, spectrogram = yamnet_model(waveform)

    # ✅ Average over time to get final scores
    mean_scores = np.mean(scores, axis=0)

    # ✅ Find the predicted class index
    predicted_class_index = np.argmax(mean_scores)

    # ✅ Get class label
    detected_class = class_names[predicted_class_index]

    print(f"🎧 Detected sound: {detected_class}")

    # ✅ Check if detected sound is related to running water
    water_related_sounds =["Water", "Stream", "Faucet", "Bee wasp", "Toilet flush", "Thunder", "Crack", "Splash",
                            "Ratchet","Shatter","Croak","Pulse","Steam whistle","Squish"]
    
    if any(sound in detected_class for sound in water_related_sounds):
        current_time = time.time()
        if current_time - last_water_alert_time > water_alert_cooldown:
            print("🚰 Running water detected!")
            speak("Running water detected. Please close the tap.")
            last_water_alert_time = current_time
        return True

    return False

# ✅ Light Detection Variables
brightness_threshold = 80
last_light_alert_time = 0
alert_interval = 20  # seconds

print("💡🚰 Starting Light & Water Detection. Press 'q' to quit.")

while True:
    # ✅ Fetch camera image
    img_arr = np.array(bytearray(urllib.request.urlopen(url).read()), dtype=np.uint8)
    frame = cv2.imdecode(img_arr, -1)
    frame = cv2.resize(frame, (1280, 720))

    # ✅ Improved light detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    avg_brightness = np.mean(gray)
    brightness_status = "ON" if avg_brightness > 80 else "OFF"

    # ✅ Repeat warning only every 60 seconds
    current_time = time.time()
    if brightness_status == "ON" and (current_time - last_light_alert_time > alert_interval):
        speak("The light is on, please turn it off.")
        last_light_alert_time = current_time

    cv2.putText(frame, f"Light status: {brightness_status}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # ✅ Detect running water
    detect_running_water()

    cv2.imshow('Light & Water Detection', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
