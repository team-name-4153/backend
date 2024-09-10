import os
import cv2
from base_camera import BaseCamera


class Camera(BaseCamera):
    video_source = 0
    max_failures = 10

    def __init__(self):
        if os.environ.get('OPENCV_CAMERA_SOURCE'):
            Camera.set_video_source(int(os.environ['OPENCV_CAMERA_SOURCE']))
        super(Camera, self).__init__()

    @staticmethod
    def set_video_source(source):
        Camera.video_source = source

    @staticmethod
    def frames():
        camera = cv2.VideoCapture(Camera.video_source)
        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')
        failure_count = 0
        while True:
            # read current frame
            ret, img = camera.read()
            if not ret:
                failure_count += 1
                print(f"Warning: Skipping frame {failure_count}/{Camera.max_failures}, no image captured")
                
                if failure_count >= Camera.max_failures:
                    print("Error: Too many consecutive failures, shutting down...")
                    break

                continue

            if img is None:
                raise RuntimeError("Error: Image not loaded properly")
            
            # reset failure count
            failure_count = 0
            yield cv2.imencode('.jpg', img)[1].tobytes()