from flask import Flask, render_template, redirect, url_for, jsonify
import subprocess
import os
import json
import cv2  # OpenCV for local camera access

app = Flask(__name__)

# Reference to the subprocess running emotion_detection.py
process = None

# Detect environment: DEVELOPMENT (local) or PRODUCTION (Render)
ENV = os.getenv("ENVIRONMENT", "DEVELOPMENT")

# Camera initialization
# if ENV == "PRODUCTION":
print("Running in production mode. Mocking camera.")
cap = None  # No actual camera access in production

def mock_read():
    # Simulate reading frames using a placeholder image
    frame = cv2.imread("static/sample_image.jpg")  # Use a static sample image
    if frame is None:
        return False, None
    return True, frame

def mock_is_opened():
    return True

# Mock OpenCV functions
cap = type("MockCapture", (object,), {
    "read": mock_read,
    "isOpened": mock_is_opened,
    "release": lambda: None,
})()
# else:
#     print("Running in development mode. Using real camera.")
#     cap = cv2.VideoCapture(0)
#     if not cap.isOpened():
#         print("Unable to access the camera.")
#         exit()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/start')
def start():
    """
    Starts the emotion detection process.
    Simulates the process if running in production.
    """
    global cap
    if cap is None or not cap.isOpened():
        return "Camera not accessible. Check configuration."

    ret, frame = cap.read()
    if not ret:
        return "Failed to capture frame."

    # Here you can add logic for processing the frame
    # For example, emotion detection, saving the frame, etc.
    cv2.imwrite("static/output_frame.jpg", frame)  # Save a captured frame
    return redirect(url_for('index'))


@app.route('/stop')
def stop():
    """
    Stops the emotion detection process.
    """
    global process
    if process is not None:
        process.terminate()
        try:
            process.wait(timeout=5)  # Wait for graceful termination
        except subprocess.TimeoutExpired:
            process.kill()
        process = None
    return redirect(url_for('index'))


@app.route('/current_song')
def current_song():
    """
    Returns the name of the currently playing track
    and its album art URL by reading current_track.json.
    """
    data = {
        "track_name": "",
        "album_art": ""
    }
    if os.path.exists("current_track.json"):
        with open("current_track.json", "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                pass  # Handle invalid JSON

    return jsonify(data)


if __name__ == '__main__':
    # Run the Flask app
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
