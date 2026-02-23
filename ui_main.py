import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QTextEdit, QFileDialog, QStackedWidget, QFrame)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QImage, QPixmap, QFont

from camera_worker import CameraWorker
from ocr_engine import OCREngineWorker
from ai_tutor import AITeacher

class ModernOCRApp(QMainWindow):
    """
    The main graphical user interface for the AI OCR Tutor application.
    Features a modern dark UI with rounded corners and distinct panels.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Vision & Tutor (TensorFlow OCR)")
        self.setGeometry(100, 100, 1200, 800)

        # Initialize core components
        self.ai_teacher = AITeacher()
        self.ocr_thread = OCREngineWorker()
        self.ocr_thread.result_signal.connect(self.handle_ocr_result)
        self.ocr_thread.status_signal.connect(self.update_status)
        
        self.camera_thread = None
        self.current_frame = None

        self.init_ui()

    def init_ui(self):
        # Main Widget and Layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Sidebar Panel
        sidebar = QFrame()
        sidebar.setFixedWidth(250)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #11111b;
                border-right: 1px solid #313244;
            }
            QPushButton {
                background-color: transparent;
                color: #cdd6f4;
                font-size: 16px;
                font-weight: bold;
                text-align: left;
                padding: 15px;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #313244;
            }
            QPushButton:checked {
                background-color: #89b4fa;
                color: #11111b;
            }
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        
        title_label = QLabel("🤖 AI Tutor Vision")
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #89b4fa; padding: 10px;")
        
        self.btn_live = QPushButton("📷 Live Camera OCR")
        self.btn_live.setCheckable(True)
        self.btn_live.setChecked(True)
        self.btn_live.clicked.connect(lambda: self.switch_mode(0))

        self.btn_image = QPushButton("🖼️ Upload Image")
        self.btn_image.setCheckable(True)
        self.btn_image.clicked.connect(lambda: self.switch_mode(1))

        sidebar_layout.addWidget(title_label)
        sidebar_layout.addSpacing(30)
        sidebar_layout.addWidget(self.btn_live)
        sidebar_layout.addWidget(self.btn_image)
        sidebar_layout.addStretch()

        # 2. Main Content Area
        content_area = QFrame()
        content_area.setStyleSheet("background-color: #1e1e2e;")
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(20, 20, 20, 20)

        # Image/Camera Display
        self.image_display = QLabel("No Image Selected")
        self.image_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_display.setStyleSheet("""
            background-color: #313244; 
            border-radius: 12px;
            color: #a6adc8;
            font-size: 18px;
        """)
        self.image_display.setMinimumHeight(400)

        # Controls under image
        controls_layout = QHBoxLayout()
        self.btn_capture = QPushButton("SCAN CURRENT FRAME")
        self.btn_capture.setStyleSheet("""
            QPushButton {
                background-color: #a6e3a1; color: #11111b;
                font-size: 14px; font-weight: bold;
                padding: 10px 20px; border-radius: 6px;
            }
            QPushButton:hover { background-color: #94e2d5; }
        """)
        self.btn_capture.clicked.connect(self.process_current_frame)

        self.btn_load_file = QPushButton("CHOOSE FILE")
        self.btn_load_file.setStyleSheet("""
            QPushButton {
                background-color: #89b4fa; color: #11111b;
                font-size: 14px; font-weight: bold;
                padding: 10px 20px; border-radius: 6px;
            }
            QPushButton:hover { background-color: #b4befe; }
        """)
        self.btn_load_file.clicked.connect(self.load_image_file)
        self.btn_load_file.hide() # Hidden by default (Live mode)

        controls_layout.addWidget(self.btn_capture)
        controls_layout.addWidget(self.btn_load_file)

        # 3. AI Teaching Panel (Bottom)
        ai_panel_layout = QHBoxLayout()
        
        # Raw Text Area
        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        self.text_output.setPlaceholderText("OCR Extracted text will appear here...")
        self.text_output.setStyleSheet("""
            background-color: #181825; color: #cdd6f4;
            border-radius: 8px; padding: 10px; font-size: 14px;
        """)

        # AI Tutor Explanation Area
        self.ai_output = QTextEdit()
        self.ai_output.setReadOnly(True)
        self.ai_output.setPlaceholderText("AI Tutor lesson plan will appear here...")
        self.ai_output.setStyleSheet("""
            background-color: #313244; color: #f38ba8;
            border-radius: 8px; padding: 10px; font-size: 14px;
            border: 1px solid #f38ba8;
        """)

        ai_panel_layout.addWidget(self.text_output)
        ai_panel_layout.addWidget(self.ai_output)

        # Status Bar
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #a6adc8; font-style: italic;")

        # Combine Content Layout
        content_layout.addWidget(self.image_display)
        content_layout.addLayout(controls_layout)
        content_layout.addSpacing(10)
        content_layout.addLayout(ai_panel_layout)
        content_layout.addWidget(self.status_label)

        # Assemble Main Layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(content_area, stretch=1)

        # Start Camera by Default
        self.start_camera()

    def switch_mode(self, mode_index):
        """Switches between Live Camera (0) and Image Upload (1) modes."""
        self.btn_live.setChecked(mode_index == 0)
        self.btn_image.setChecked(mode_index == 1)

        if mode_index == 0:
            self.btn_load_file.hide()
            self.btn_capture.show()
            self.btn_capture.setText("SCAN CURRENT FRAME")
            self.start_camera()
        else:
            self.stop_camera()
            self.btn_load_file.show()
            self.btn_capture.hide()
            self.image_display.setText("Click 'Choose File' to upload an image")
            self.current_frame = None

    def start_camera(self):
        if self.camera_thread is None or not self.camera_thread.running:
            self.camera_thread = CameraWorker()
            self.camera_thread.frame_update.connect(self.update_image_display)
            self.camera_thread.error_signal.connect(self.update_status)
            self.camera_thread.start()

    def stop_camera(self):
        if self.camera_thread and self.camera_thread.running:
            self.camera_thread.stop()
            self.camera_thread = None

    @pyqtSlot(np.ndarray)
    def update_image_display(self, rgb_image):
        """Receives RGB numpy array from camera or OCR result and displays it."""
        self.current_frame = rgb_image
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        
        # Convert to QImage and then Pixmap
        q_img = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)
        
        # Scale to fit label maintaining aspect ratio
        scaled_pixmap = pixmap.scaled(self.image_display.size(), 
                                      Qt.AspectRatioMode.KeepAspectRatio, 
                                      Qt.TransformationMode.SmoothTransformation)
        self.image_display.setPixmap(scaled_pixmap)

    def load_image_file(self):
        """Opens a file dialog to load an image."""
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if file_name:
            # Read image using OpenCV and convert to RGB
            img = cv2.imread(file_name)
            if img is not None:
                rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                self.update_image_display(rgb_img)
                # Automatically process when image is loaded
                self.process_current_frame()
            else:
                self.update_status("Error loading image file.")

    def process_current_frame(self):
        """Sends the current image to the background OCR Thread."""
        if self.current_frame is None:
            self.update_status("No image to process!")
            return

        # Disable button to prevent spamming while processing
        self.btn_capture.setEnabled(False)
        self.text_output.setText("Processing OCR...")
        self.ai_output.setText("Analyzing...")
        
        # Stop live feed temporarily so we can show the drawn boxes
        if self.camera_thread and self.camera_thread.running:
            self.stop_camera()

        self.ocr_thread.set_image(self.current_frame)
        self.ocr_thread.start()

    @pyqtSlot(str, np.ndarray)
    def handle_ocr_result(self, text, drawn_image):
        """Called when TensorFlow finishes processing the image."""
        self.btn_capture.setEnabled(True)
        
        # Display the image with bounding boxes
        self.update_image_display(drawn_image)
        
        # Display extracted text
        self.text_output.setText(text)
        
        # Trigger the AI Teaching process
        lesson_data = self.ai_teacher.analyze_and_teach(text)
        self.ai_output.setMarkdown(lesson_data["lesson"])

        # If we were in live mode, optionally restart camera after 5 seconds
        # Here we leave it frozen so the user can read the lesson. 
        # Clicking "Scan" or "Live Camera" will reset it.

    @pyqtSlot(str)
    def update_status(self, message):
        self.status_label.setText(message)

    def closeEvent(self, event):
        """Ensures camera and threads are cleanly closed when window closes."""
        self.stop_camera()
        if self.ocr_thread.isRunning():
            self.ocr_thread.terminate()
        event.accept()