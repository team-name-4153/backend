import os
import subprocess
import threading

ffmpeg_process = None

def start_streaming_thread():
    global ffmpeg_process
    if ffmpeg_process is None:
        threading.Thread(target=start_ffmpeg).start()
        return {'status': 'Streaming started'}
    else:
        return {'status': 'Already streaming'}
    
def stop_streaming_thread():
    global ffmpeg_process
    if ffmpeg_process is not None:
        ffmpeg_process.terminate()
        ffmpeg_process = None
        return {'status': 'Streaming stopped'}
    else:
        return {'status': 'Not streaming'}


def start_ffmpeg():
    global ffmpeg_process
    hls_dir = os.path.join('static', 'hls')
    os.makedirs(hls_dir, exist_ok=True)
    # Clear existing segments
    for file in os.listdir(hls_dir):
        os.remove(os.path.join(hls_dir, file))
    ffmpeg_command = [
        'ffmpeg',
        '-f', 'v4l2',            # Linux video input
        '-i', '/dev/video0',     # Input device (webcam)
        '-s', '640x480',         # Set frame size
        '-r', '25',              # Set frame rate
        '-codec:v', 'libx264',   # Video codec
        '-preset', 'ultrafast',  # Encoding speed
        '-tune', 'zerolatency',  # Reduce latency
        '-f', 'hls',             # Output format
        '-hls_time', '1',        # Segment length in seconds
        '-hls_list_size', '3',   # Number of segments in playlist
        '-hls_flags', 'delete_segments+append_list',  # Manage segments
        '-hls_allow_cache', '0',
        '-hls_segment_type', 'mpegts',
        os.path.join(hls_dir, 'stream.m3u8')  # Output HLS playlist
    ]
    ffmpeg_process = subprocess.Popen(ffmpeg_command)