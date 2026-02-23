import keras_ocr
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal

class OCREngineWorker(QThread):
    """
    Runs the TensorFlow/Keras-OCR pipeline in a background thread.
    This prevents the heavy ML inference from blocking the UI.
    """
    result_signal = pyqtSignal(str, np.ndarray)  # Returns extracted text and image with boxes
    status_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.pipeline = None
        self.image_to_process = None

    def load_model(self):
        """Loads the TensorFlow models if not already loaded."""
        if self.pipeline is None:
            self.status_signal.emit("Loading TensorFlow OCR Models (May take a moment)...")
            self.pipeline = keras_ocr.pipeline.Pipeline()
            self.status_signal.emit("Models loaded successfully. Ready.")

    def set_image(self, image_array):
        """Sets the image array to be processed."""
        self.image_to_process = image_array

    def run(self):
        if self.image_to_process is None:
            self.status_signal.emit("Error: No image provided.")
            return

        self.load_model()
        
        try:
            self.status_signal.emit("Processing image...")
            # Keras-OCR expects a list of images
            prediction_groups = self.pipeline.recognize([self.image_to_process])
            predictions = prediction_groups[0]
            
            # Extract text and draw boxes
            extracted_text = []
            output_image = self.image_to_process.copy()
            
            for text, box in predictions:
                extracted_text.append(text)
                # Draw bounding boxes around recognized text
                pts = np.array(box, np.int32)
                pts = pts.reshape((-1, 1, 2))
                # Draw a green polygon
                import cv2
                cv2.polylines(output_image, [pts], True, (0, 255, 0), 3)
            
            final_text = " ".join(extracted_text)
            if not final_text.strip():
                final_text = "No text detected."
                
            self.result_signal.emit(final_text, output_image)
            self.status_signal.emit("Processing complete.")
            
        except Exception as e:
            self.status_signal.emit(f"OCR Error: {str(e)}")