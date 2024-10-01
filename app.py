import requests
from flask import Flask, render_template, Response, send_from_directory, request
from flask_socketio import SocketIO, emit, join_room
from flask_cors import CORS
import os
import sys
from video_utils.utils import start_streaming_thread, stop_streaming_thread


# if os.environ.get('CAMERA'):
#     Camera = import_module('camera_' + os.environ['CAMERA']).Camera
# else:
#     from camera.camera import Camera

BASEDIR = os.path.abspath(os.path.dirname(__file__))

users_in_room = {}
rooms_sid = {}
names_sid = {}

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('settings.py')
    return app

app = create_app()
CORS(app, resources={r"/*": {"origins": "*"}})
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

@socketio.on("connect")
def on_connect():
    sid = request.sid
    print("New socket connected ", sid)


@socketio.on("join-room")
def on_join_room(data):
    sid = request.sid
    room_id = data["room_id"]
    display_name = data["name"]

    # register sid to the room
    join_room(room_id)
    rooms_sid[sid] = room_id
    names_sid[sid] = display_name

    # broadcast to others in the room
    print("[{}] New member joined: {}<{}>".format(room_id, display_name, sid))
    emit("user-connect", {"sid": sid, "name": display_name},
         broadcast=True, include_self=False, room=room_id)

    # add to user list maintained on server
    if room_id not in users_in_room:
        users_in_room[room_id] = [sid]
        emit("user-list", {"my_id": sid})  # send own id only
    else:
        usrlist = {u_id: names_sid[u_id]
                   for u_id in users_in_room[room_id]}
        # send list of existing users to the new member
        emit("user-list", {"list": usrlist, "my_id": sid})
        # add new member to user list maintained on server
        users_in_room[room_id].append(sid)

    print("\nusers: ", users_in_room, "\n")


@socketio.on("disconnect")
def on_disconnect():
    sid = request.sid
    room_id = rooms_sid[sid]
    display_name = names_sid[sid]

    print("[{}] Member left: {}<{}>".format(room_id, display_name, sid))
    emit("user-disconnect", {"sid": sid},
         broadcast=True, include_self=False, room=room_id)

    users_in_room[room_id].remove(sid)
    if len(users_in_room[room_id]) == 0:
        users_in_room.pop(room_id)

    rooms_sid.pop(sid)
    names_sid.pop(sid)

    print("\nusers: ", users_in_room, "\n")


@socketio.on("data")
def on_data(data):
    sender_sid = data['sender_id']
    target_sid = data['target_id']
    if sender_sid != request.sid:
        print("[Not supposed to happen!] request.sid and sender_id don't match!!!")

    if data["type"] != "new-ice-candidate":
        print('{} message from {} to {}'.format(
            data["type"], sender_sid, target_sid))
    socketio.emit('data', data, room=target_sid)


@socketio.on("send_message")
def on_send_message(data):
    target_sid = data['target_id']
    sender_id = data['sender_id']
    message = data['message']
    requests.post("http://localhost:5001/comments/upload", json={ "comment": message, "userId": sender_id })
    socketio.emit('message', data, room=target_sid)


if __name__ == '__main__':
    socketio.run(
        app,
        debug=bool(int(app.config["DEBUG"])),
        host=os.environ.get("FLASK_RUN_HOST", "0.0.0.0"),
        port=int(os.environ.get("FLASK_RUN_PORT", "5000")),
    )