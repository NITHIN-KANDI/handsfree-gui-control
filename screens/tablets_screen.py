# screens/tablets_screen.py
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout

class TabletsScreen(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.buttons = []
        layout = QVBoxLayout(self)

        back_btn = QPushButton("⬅ Back")
        back_btn.setStyleSheet("font-size: 32px; background-color: #e74c3c; color: white;")
        back_btn.setFixedHeight(parent.height() // 5)
        back_btn.clicked.connect(lambda: parent.switch_screen(parent.main_menu))
        self.buttons.append(back_btn)
        layout.addWidget(back_btn)

        for label in ["I need have my Syrup", "I need to take Tablet"]:
            btn = QPushButton(label)
            btn.setStyleSheet("font-size: 36px; background-color: #2ecc71; color: white;")
            btn.setMinimumHeight((parent.height() - back_btn.height()) // 2)
            btn.clicked.connect(lambda _, l=label: parent.show_final_message(f"{l}"))
            self.buttons.append(btn)
            layout.addWidget(btn)
