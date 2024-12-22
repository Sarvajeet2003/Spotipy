from flask import Flask, render_template, redirect, url_for, jsonify
import subprocess
import os
import json
import signal  # For terminating processes
import sys
sys.path.insert(0, './vendor')

app = Flask(__name__)

# Reference to the subprocess running emotion_detection.py
process = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start')
def start():
    """
    Starts the emotion_detection.py script in a separate process.
    """
    global process
    if process is None or process.poll() is not None:
        # Start emotion_detection.py as a new subprocess
        process = subprocess.Popen(["python3", "emotion_detection.py"])
    return redirect(url_for('index'))

@app.route('/stop')
def stop():
    """
    Stops the emotion_detection.py script by terminating the process.
    """
    global process
    if process is not None:
        # Send SIGTERM to the subprocess
        process.terminate()
        try:
            process.wait(timeout=5)  # Wait for it to terminate gracefully
        except subprocess.TimeoutExpired:
            process.kill()  # Force kill if it doesn't terminate
        process = None
    return redirect(url_for('index'))

@app.route('/current_song')
def current_song():
    """
    Returns the name of the currently playing track
    and its album art URL by reading current_track.json
    """
    data = {
        "track_name": "",
        "album_art": ""
    }
    if os.path.exists("current_track.json"):
        with open("current_track.json", "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except:
                pass  # If the file is corrupted or not valid JSON

    return jsonify(data)

if __name__ == '__main__':
    # By default runs on http://127.0.0.1:5000
    app.run(debug=True)
