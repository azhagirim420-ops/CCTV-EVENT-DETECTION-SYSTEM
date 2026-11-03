
from flask import Flask, render_template, Response, jsonify, request
from detection import ObjectDetector
from database import create_table, save_event, get_events
import cv2
import numpy as np
import threading
import time

app = Flask(__name__)

create_table()

detector = None
latest_frame = None
frame_lock = threading.Lock()

last_event_time = {}
EVENT_COOLDOWN = 15
CROWD_LIMIT = 5


def get_detector():
    global detector

    if detector is None:
        detector = ObjectDetector()

    return detector


def record_event(event_type):
    now = time.time()
    previous = last_event_time.get(event_type, 0)

    if now - previous >= EVENT_COOLDOWN:
        save_event(event_type, "CAMERA_01")
        last_event_time[event_type] = now


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/status")
def status():
    return jsonify({
        "status": "online",
        "project": "CCTV Event Detection System"
    })


@app.route("/api/frame", methods=["POST"])
def process_frame():
    global latest_frame

    uploaded = request.files.get("frame")

    if uploaded is None:
        return jsonify({"error": "No frame received"}), 400

    data = np.frombuffer(uploaded.read(), np.uint8)
    frame = cv2.imdecode(data, cv2.IMREAD_COLOR)

    if frame is None:
        return jsonify({"error": "Invalid image"}), 400

    try:
        ai = get_detector()
        output, people, vehicles = ai.detect(frame)

        if people > 0:
            record_event("Person Detected")

        if vehicles > 0:
            record_event("Vehicle Detected")

        if people >= CROWD_LIMIT:
            record_event("Crowd Detected")

        with frame_lock:
            latest_frame = output.copy()

        return jsonify({
            "success": True,
            "people": people,
            "vehicles": vehicles,
            "crowd": people >= CROWD_LIMIT
        })

    except Exception as error:
        app.logger.exception("Detection failed")
        return jsonify({"error": "AI processing failed"}), 500


@app.route("/video_feed")
def video_feed():

    def generate():
        while True:
            with frame_lock:
                frame = (
                    latest_frame.copy()
                    if latest_frame is not None else None
                )

            if frame is not None:
                success, buffer = cv2.imencode(".jpg", frame)

                if success:
                    yield (
                        b"--frame\r\n"
                        b"Content-Type: image/jpeg\r\n\r\n"
                        + buffer.tobytes()
                        + b"\r\n"
                    )

            time.sleep(0.1)

    return Response(
        generate(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/api/events")
def events():
    records = get_events()

    return jsonify([
        {
            "id": row[0],
            "event": row[1],
            "camera": row[2],
            "time": row[3]
        }
        for row in records
    ])


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        threaded=True
    )
