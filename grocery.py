"""
realtime_scanner_full.py

Uses the trained model (trained on entire product images at 160x160)
for real-time scanning. Only images that were labeled in training are used.
The entire frame is classified (no ROI selection). Audio feedback is provided via pyttsx3.

Press 'p' to predict, 'q' to quit.
"""

import cv2
import urllib.request
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
import pyttsx3

# Custom objects used in training:
@tf.keras.utils.register_keras_serializable()
def wrap_hub_layer(x):
    # MobileNetV2 (160x160) feature vector.
    layer = hub.KerasLayer(
        "https://tfhub.dev/google/imagenet/mobilenet_v2_100_160/feature_vector/4",
        trainable=False
    )
    return layer(x)

def output_shape_fn(input_shape):
    return (input_shape[0], 1280)

# Set model path and camera URL.
MODEL_PATH = "sustainability_model_finetune.keras"
CAMERA_URL = "http://10.69.80.108:8080/shot.jpg"

# Load the model with custom objects.
custom_objects = {"wrap_hub_layer": wrap_hub_layer, "output_shape_fn": output_shape_fn}
try:
    model = tf.keras.models.load_model(MODEL_PATH, custom_objects=custom_objects)
    print("Model loaded successfully.")
except Exception as e:
    print("Error loading model:", e)
    exit()

# Initialize text-to-speech engine.
engine = pyttsx3.init()
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Define class labels.
# IMPORTANT: The order here must match the order from training's LabelBinarizer.
# For example, if LabelBinarizer sorted alphabetically,
# you might get: ["Highly Sustainable", "Less Sustainable", "Moderately Sustainable"]
CLASS_LABELS = ["Highly Sustainable", "Less Sustainable", "Moderately Sustainable"]

def preprocess_image(img):
    """
    Convert BGR image from OpenCV to RGB, resize to 160x160,
    normalize pixel values to [0,1], and add a batch dimension.
    """
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (160, 160))
    img = img.astype("float32") / 255.0
    return np.expand_dims(img, axis=0)

def predict_sustainability(frame):
    processed = preprocess_image(frame)
    preds = model.predict(processed)
    print("Raw predictions:", preds)
    idx = np.argmax(preds)
    return CLASS_LABELS[idx]

cv2.namedWindow("Grocery Scanner (Full)", cv2.WINDOW_NORMAL)
print("Starting real-time scanning...")
print("Press 'p' to predict, 'q' to quit.")

while True:
    try:
        resp = urllib.request.urlopen(CAMERA_URL)
        arr = np.asarray(bytearray(resp.read()), dtype=np.uint8)
        frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if frame is None:
            print("Warning: empty frame.")
            continue
    except Exception as e:
        print("Error accessing camera:", e)
        continue

    cv2.imshow("Grocery Scanner (Full)", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('p'):
        print("Predicting frame...")
        label = predict_sustainability(frame)
        speak(f"This item is {label}.")
        print("Predicted:", label)
    elif key == ord('q'):
        print("Exiting...")
        break

cv2.destroyAllWindows()
