import cv2
import urllib.request
import numpy as np
import pyttsx3
import time

# Initialize Text-to-Speech engine
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

# Load MobileNet SSD model for object detection
net = cv2.dnn.readNetFromCaffe('MobileNetSSD_deploy.prototxt', 'MobileNetSSD_deploy.caffemodel')

# Object classes (MobileNet SSD standard 21 classes)
classNames = [
    "background", "aeroplane", "bicycle", "bird", "boat",
    "bottle", "bus", "car", "cat", "chair",
    "cow", "diningtable", "dog", "horse",
    "motorbike", "person", "pottedplant", "sheep",
    "sofa", "train", "tvmonitor"
]

# Helper function to map the x-center of a bounding box to a clock position.
def get_clock_position(x_center, frame_width):
    section_width = frame_width / 6
    if x_center < section_width:
        return "9 o'clock"
    elif x_center < 2 * section_width:
        return "10 o'clock"
    elif x_center < 3 * section_width:
        return "11 o'clock"
    elif x_center < 4 * section_width:
        return "1 o'clock"
    elif x_center < 5 * section_width:
        return "2 o'clock"
    else:
        return "3 o'clock"

# Initialize tracking variables.
last_spoken_object = None
last_nearest_distance = 0  # previous frame's largest box height.
last_spoken_time = 0
speak_cooldown = 3  # seconds between speaking

# IP Webcam URL (resolution set to 1280x720)
url = 'http://10.69.80.108:8080/shot.jpg?resolution=1280x720'

print("Starting Object Detection. Press 'q' to quit.")

while True:
    try:
        # Fetch frame from the webcam.
        resp = urllib.request.urlopen(url, timeout=5)
        arr = np.asarray(bytearray(resp.read()), dtype=np.uint8)
        frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if frame is None:
            print("Warning: empty frame.")
            continue
    except Exception as e:
        print(f"Error accessing camera: {e}")
        time.sleep(1)
        continue

    # Optionally, ensure the frame is 1280x720.
    frame = cv2.resize(frame, (1280, 720))

    # Prepare the image for object detection.
    blob = cv2.dnn.blobFromImage(frame, scalefactor=0.007843, size=(300, 300), swapRB=True, crop=False)
    net.setInput(blob)
    detections = net.forward()

    nearest_object = None
    nearest_distance = 0  # use the bounding box height as proxy for closeness.
    nearest_position = None

    # Loop over detections.
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.6:
            idx = int(detections[0, 0, i, 1])
            detected_class = classNames[idx]

            # Get bounding box coordinates.
            box = detections[0, 0, i, 3:7] * np.array([frame.shape[1], frame.shape[0],
                                                        frame.shape[1], frame.shape[0]])
            (startX, startY, endX, endY) = box.astype("int")
            x_center = (startX + endX) // 2

            # Use the height of the bounding box as a proxy for distance (larger = closer)
            box_height = endY - startY

            # Update the nearest object if this detection is closer.
            if box_height > nearest_distance:
                nearest_distance = box_height
                nearest_object = detected_class
                nearest_position = get_clock_position(x_center, frame.shape[1])

            # Draw bounding box and label.
            cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 0), 2)
            label_text = f"{detected_class} ({get_clock_position(x_center, frame.shape[1])})"
            cv2.putText(frame, label_text, (startX, startY - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    current_time = time.time()
    # Check if we should speak: if an object is detected and cooldown passed.
    if nearest_object is not None and (current_time - last_spoken_time > speak_cooldown):
        # If the object has changed or if it's significantly closer (at least 10% larger).
        if (nearest_object != last_spoken_object) or (nearest_distance > last_nearest_distance * 1.1):
            print(f"Speaking: {nearest_object} at {nearest_position}")
            speak(f"{nearest_object} detected at {nearest_position}.")
            last_spoken_time = current_time
            last_spoken_object = nearest_object

    last_nearest_distance = nearest_distance

    cv2.imshow("Object Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
