# screens/final_message.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QSpacerItem, QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import pyttsx3
from PyQt5.QtCore import Qt, QTimer


class FinalMessageScreen(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(40)
        self.layout.setContentsMargins(0, 100, 0, 0)  # Remove left/right margins to allow full width

        # Initialize text-to-speech engine
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 100)  # Speech speed
        self.tts_engine.setProperty('volume', 1.0)  # Volume level (0.0 to 1.0)

        self.message_label = QLabel("", self)
        self.message_label.setStyleSheet("font-size: 48px; color: #34495e;")
        self.message_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.message_label, alignment=Qt.AlignCenter)

        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.layout.addItem(spacer)

        back_btn = QPushButton("⬅ Back to Main Menu")
        back_btn.setStyleSheet("""
            font-size: 32px;
            background-color: #e74c3c;
            color: white;
            border: none;
            border-radius: 0px;
            padding: 20px;
        """)
        back_btn.setFixedHeight(parent.height() // 5)
        back_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        back_btn.clicked.connect(lambda: self.parent.switch_screen(self.parent.main_menu))
        
        self.layout.addWidget(back_btn, alignment=Qt.AlignBottom)
        self.buttons = [back_btn]

    def set_message(self, message):
        self.message_label.setText(message)
        QTimer.singleShot(100, lambda: self.speak_message(message))

    def speak_message(self, message):
        self.tts_engine.stop()  # Stop any previous speech
        self.tts_engine.say(message)
        self.tts_engine.runAndWait()
