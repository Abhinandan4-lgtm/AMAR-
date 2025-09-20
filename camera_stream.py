# AMAR - AI Med Assistance Robot
# Camera Streaming Module (camera_stream.py)
# Handles capturing frames from the Pi Camera for video streaming.

import cv2
import logging
import time

class CameraStream:
    def __init__(self, resolution=(640, 480), framerate=24):
        self.resolution = resolution
        self.framerate = framerate
        self.camera = None
        self.output = None
        self.frame = None

        try:
            # Attempt to initialize the camera
            self.camera = cv2.VideoCapture(0) # 0 is typically the default camera
            if not self.camera.isOpened():
                raise IOError("Cannot open webcam")
            
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
            self.camera.set(cv2.CAP_PROP_FPS, self.framerate)
            logging.info("Pi Camera initialized successfully.")
            
            # Start a background thread to continuously read frames
            import threading
            self.thread = threading.Thread(target=self._update, args=())
            self.thread.daemon = True
            self.thread.start()
            
        except Exception as e:
            logging.error(f"Failed to initialize camera: {e}")
            logging.warning("Video streaming will use a placeholder image.")
            # Create a placeholder frame for when the camera is not available
            self.placeholder_frame = self._create_placeholder()

    def _create_placeholder(self):
        """Creates a black frame with text for when the camera fails."""
        img = cv2.imread('https://placehold.co/640x480/000000/FFFFFF?text=Camera+Offline', cv2.IMREAD_COLOR)
        if img is None: # Fallback if even the placeholder URL fails
            import numpy as np
            img = np.zeros((self.resolution[1], self.resolution[0], 3), dtype=np.uint8)
            cv2.putText(img, "Camera Offline", (50, self.resolution[1] // 2), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        _, jpeg = cv2.imencode('.jpg', img)
        return jpeg.tobytes()

    def _update(self):
        """The target function for the frame-reading thread."""
        while True:
            if self.camera and self.camera.isOpened():
                ret, frame = self.camera.read()
                if ret:
                    _, jpeg = cv2.imencode('.jpg', frame)
                    self.frame = jpeg.tobytes()
                else:
                    logging.warning("Failed to grab frame from camera.")
                    time.sleep(0.1)
            else:
                # If camera is not available, wait before retrying
                time.sleep(1)

    def get_frame(self):
        """Returns the latest captured frame in JPEG format."""
        if self.frame is not None:
            return self.frame
        else:
            # Return the placeholder if the camera thread hasn't produced a frame yet
            return self.placeholder_frame

    def release(self):
        """Releases the camera resources."""
        if self.camera and self.camera.isOpened():
            self.camera.release()
            logging.info("Camera released.")
