import cv2
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal

class CameraWorker(QThread):
    """
    Handles the OpenCV live camera feed in a separate thread
    to prevent the PyQt6 GUI from freezing.
    """
    frame_update = pyqtSignal(np.ndarray)
    error_signal = pyqtSignal(str)

    def __init__(self, camera_index=0):
        super().__init__()
        self.camera_index = camera_index
        self.running = False
        self.capture = None

    def run(self):
        self.running = True
        self.capture = cv2.VideoCapture(self.camera_index)
        
        if not self.capture.isOpened():
            self.error_signal.emit("Error: Could not open camera.")
            self.running = False
            return

        while self.running:
            ret, frame = self.capture.read()
            if ret:
                # Convert BGR (OpenCV) to RGB for PyQt display and Keras-OCR
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.frame_update.emit(rgb_frame)
            else:
                self.error_signal.emit("Error: Could not read frame.")
                break

    def stop(self):
        """Stops the camera feed and releases resources."""
        self.running = False
        self.wait()
        if self.capture:
            self.capture.release()