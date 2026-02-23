import sys
from PyQt6.QtWidgets import QApplication
from ui_main import ModernOCRApp

def main():
    """
    Main entry point for the Modern OCR & AI Tutor Application.
    Initializes the PyQt6 application loop.
    """
    app = QApplication(sys.argv)
    
    # Apply a global stylesheet for modern dark mode base
    app.setStyleSheet("""
        QMainWindow {
            background-color: #1e1e2e;
        }
        QScrollBar:vertical {
            background: #181825;
            width: 10px;
        }
        QScrollBar::handle:vertical {
            background: #585b70;
            border-radius: 5px;
        }
    """)
    
    window = ModernOCRApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()