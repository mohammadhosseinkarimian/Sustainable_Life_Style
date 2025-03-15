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
classNames = ["background", "bicycle", "bird", "boat",
              "bottle", "bus", "car", "cat", "chair",
              "cow", "diningtable", "dog", "horse",
              "motorbike", "person", "pottedplant", "sheep",
              "sofa", "train", "tvmonitor"]

# Define a helper to get clock position based on x-coordinate.
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

# Initialize tracking variables
last_spoken_object = None
last_nearest_distance = 0  # keep track of the largest bounding-box height from previous frame
last_spoken_time = 0
speak_cooldown = 3  # seconds between speaking

# IP Webcam URL (full resolution)
url = 'http://10.69.80.108:8080/shot.jpg?resolution=1280x720'

print("Starting Object Detection. Press 'q' to quit.")

while True:
    try:
        # Fetch the frame from the webcam.
        img_arr = np.array(bytearray(urllib.request.urlopen(url).read()), dtype=np.uint8)
        frame = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)
        if frame is None:
            print("Warning: empty frame.")
            continue
    except Exception as e:
        print(f"Error accessing camera: {e}")
        continue

    # Prepare the image for object detection using a blob.
    blob = cv2.dnn.blobFromImage(frame, scalefactor=0.007843, size=(300, 300), swapRB=True, crop=False)
    net.setInput(blob)
    detections = net.forward()

    # Initialize for this frame.
    nearest_object = None
    nearest_distance = 0  # We'll use the height of the bounding box as an approximate measure (larger = closer)
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

            # Use height of bounding box as a proxy for distance.
            box_height = endY - startY

            # Update the nearest object if this bounding box is larger (closer).
            if box_height > nearest_distance:
                nearest_distance = box_height
                nearest_object = detected_class
                nearest_position = get_clock_position(x_center, frame.shape[1])

            # Draw bounding box and label.
            cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 0), 2)
            cv2.putText(frame, f"{detected_class} ({get_clock_position(x_center, frame.shape[1])})", 
                        (startX, startY - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Check if we should speak.
    current_time = time.time()
    # Speak if there's a nearest object and cooldown has passed, and if it is different or significantly closer.
    if nearest_object is not None and (current_time - last_spoken_time > speak_cooldown):
        # If the object changed, or if it got at least 10% larger (closer) than last time.
        if (nearest_object != last_spoken_object) or (nearest_distance > last_nearest_distance * 1.1):
            print(f"Speaking: {nearest_object} at {nearest_position}")
            speak(f"{nearest_object} detected at {nearest_position}.")
            last_spoken_time = current_time
            last_spoken_object = nearest_object

    # Update last_nearest_distance for next iteration.
    last_nearest_distance = nearest_distance

    cv2.imshow("Object Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
