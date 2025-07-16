# screens/final_message.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QSpacerItem, QSizePolicy, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

class FinalMessageScreen(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(40)
        self.layout.setContentsMargins(100, 100, 100, 100)

        self.message_label = QLabel("", self)
        self.message_label.setStyleSheet("font-size: 48px; color: #34495e;")
        self.message_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.message_label, alignment=Qt.AlignCenter)

        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.layout.addItem(spacer)

        back_btn = QPushButton("\u2B05 Back to Main Menu")
        back_btn.setStyleSheet("font-size: 36px; background-color: #e74c3c; color: white;")
        back_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        back_btn.setFixedHeight(400)
        back_btn.clicked.connect(lambda: self.parent.switch_screen(self.parent.main_menu))
        self.layout.addWidget(back_btn)

        self.buttons = [back_btn]

    def set_message(self, message):
        self.message_label.setText(message)
