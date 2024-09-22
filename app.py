
from flask import Flask, render_template, Response, send_from_directory
from flask_socketio import SocketIO, emit
import os
import sys
from video_utils.utils import start_streaming_thread, stop_streaming_thread


# if os.environ.get('CAMERA'):
#     Camera = import_module('camera_' + os.environ['CAMERA']).Camera
# else:
#     from camera.camera import Camera

BASEDIR = os.path.abspath(os.path.dirname(__file__))

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('settings.py')
    return app

app = create_app()
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    # return "ok yes"
    return render_template('display_video_test.html')

@app.route('/videos/<path:filename>')
def serve_hls(filename):
    return send_from_directory('test_video', filename)

@app.route('/capture')
def capture():
    return render_template('capture.html')

@app.route('/watch')
def watch():
    return render_template('watch.html')

@socketio.on('video_frame')
def handle_video_frame(data):
    emit('video_frame', data, broadcast=True, include_self=False)

# def gen(camera):
#     """Video streaming generator function."""
#     yield b'--frame\r\n'
#     while True:
#         frame = camera.get_frame()
#         yield b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n--frame\r\n'


# @app.route('/video_feed')
# def video_feed():
#     """Video streaming route. Put this in the src attribute of an img tag."""
#     return Response(gen(Camera()),
#                     mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    socketio.run(
        app,
        debug=bool(int(app.config["DEBUG"])),
        host=os.environ.get("FLASK_RUN_HOST", "0.0.0.0"),
        port=int(os.environ.get("FLASK_RUN_PORT", "5000")),
    )