import cv2
import urllib.request
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
import pyttsx3
import time
import threading
import sys

print("Starting grocery.py scanner...")

# Create a named window (this ensures the window is created on launch)
cv2.namedWindow("Grocery Scanner (Full)", cv2.WINDOW_NORMAL)

# Determine if we have an interactive keyboard (i.e. if run from a terminal)
keyboard_control = sys.stdin.isatty()
if keyboard_control:
    print("Keyboard control enabled.")
else:
    print("Keyboard control disabled (likely launched from server).")

# Custom objects for model loading.
@tf.keras.utils.register_keras_serializable()
def wrap_hub_layer(x):
    layer = hub.KerasLayer(
        "https://tfhub.dev/google/imagenet/mobilenet_v2_100_160/feature_vector/4",
        trainable=False
    )
    return layer(x)

def output_shape_fn(input_shape):
    return (input_shape[0], 1280)

MODEL_PATH = "sustainability_model_finetune.keras"
CAMERA_URL = "http://10.69.80.108:8080/shot.jpg?resolution=1280x720"
print("Grocery using CAMERA_URL:", CAMERA_URL)

custom_objects = {"wrap_hub_layer": wrap_hub_layer, "output_shape_fn": output_shape_fn}
try:
    model = tf.keras.models.load_model(MODEL_PATH, custom_objects=custom_objects)
    print("Grocery model loaded successfully.")
except Exception as e:
    print("Grocery: Error loading model:", e)
    exit()

engine = pyttsx3.init()
def speak(text):
    print("Grocery TTS:", text)
    threading.Thread(target=lambda: (engine.say(text), engine.runAndWait())).start()

CLASS_LABELS = ["Highly Sustainable", "Less Sustainable", "Moderately Sustainable"]

def preprocess_image(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (160, 160))
    img = img.astype("float32") / 255.0
    return np.expand_dims(img, axis=0)

def predict_sustainability(frame):
    proc = preprocess_image(frame)
    preds = model.predict(proc)
    print("Grocery: Raw predictions:", preds)
    idx = int(np.argmax(preds))
    return CLASS_LABELS[idx]

print("Starting real-time grocery scanning...")
print("Press 'p' to predict, 'q' to quit (if keyboard control is enabled).")

# Camera handling variables
last_frame_time = 0
frame_interval = 1  # 1 second between frame updates
current_frame = None
last_prediction_time = 0
prediction_interval = 3  # seconds

while True:
    # Handle window events every iteration
    key = cv2.waitKey(1) & 0xFF
    if keyboard_control and key == ord('q'):
        break

    current_time = time.time()
    
    # Fetch new frame every 1 second
    if current_time - last_frame_time >= frame_interval:
        try:
            req = urllib.request.urlopen(CAMERA_URL, timeout=5)
            arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
            new_frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            if new_frame is not None:
                current_frame = cv2.resize(new_frame, (1280, 720))
                last_frame_time = current_time
        except Exception as e:
            print("Grocery: Camera error:", e)
    
    # Process predictions on the current frame
    if current_frame is not None:
        # Show frame continuously
        cv2.imshow("Grocery Scanner (Full)", current_frame)
        
        # Prediction logic (original timing preserved)
        if current_time - last_prediction_time > prediction_interval:
            print("Grocery: Predicting frame...")
            label = predict_sustainability(current_frame)
            speak(f"This item is {label}.")
            cv2.putText(current_frame, f"Prediction: {label}", (20, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            last_prediction_time = current_time

    # Handle forced predictions
    if keyboard_control and key == ord('p'):
        print("Grocery: Forcing prediction...")
        label = predict_sustainability(current_frame)
        speak(f"This item is {label}.")
        cv2.putText(current_frame, f"Prediction: {label}", (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

cv2.destroyAllWindows()