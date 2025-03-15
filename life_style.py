import cv2
import urllib.request
import numpy as np
import pyttsx3

# Initialize Text-to-Speech engine
engine = pyttsx3.init()
def speak(text):
    engine.say(text)
    engine.runAndWait()

# IP Webcam URL
url = 'http://10.69.80.108:8080/shot.jpg?resolution=1280x720'

print("Starting Sustainable Lifestyle Assistant: Light Detection. Press 'q' to quit.")

light_status_prev = None

while True:
    img_arr = np.array(bytearray(urllib.request.urlopen(url).read()), dtype=np.uint8)
    frame = cv2.imdecode(img_arr, -1)
    frame = cv2.resize(frame, (1280, 720))

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    avg_brightness = np.mean(gray)

    # Define brightness threshold (adjust according to your environment)
    threshold = 100

    if avg_brightness > threshold:
        light_status = "ON"
        feedback = "The light is on, please turn it off to save energy."
    else:
        light_status = "OFF"
        feedback = "The light is off, great job!"

    if light_status != light_status_prev:
        speak(feedback)
        light_status_prev = light_status

    label = f"Light status: {light_status}, Brightness: {int(avg_brightness)}"
    cv2.putText(frame, label, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow('Sustainable Lifestyle Assistant - Light Detection', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
