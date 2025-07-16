from PyQt5.QtWidgets import QWidget, QPushButton, QGridLayout

class MainMenuScreen(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.buttons = []
        layout = QGridLayout(self)

        items = [
            ("\U0001F37D\uFE0F I want food", lambda: parent.switch_screen(parent.food_screen)),
            ("\U0001F4A7 I need water", lambda: parent.switch_screen(parent.water_screen)),
            ("\U0001F48A I need medicine", lambda: parent.switch_screen(parent.tablets_screen)),
            ("\U0001F6BB I need to go to washroom", lambda: parent.switch_screen(parent.washroom_screen)),
        ]

        for i, (label, action) in enumerate(items):
            btn = QPushButton(label)
            btn.clicked.connect(action)
            btn.setStyleSheet("""
                font-size: 36px;
                background-color: #2c3e50;
                color: white;
                border-radius: 20px;
                padding: 20px;
            """)
            btn.setMinimumHeight(parent.height() // 2)
            btn.setMinimumWidth(parent.width() // 2)
            self.buttons.append(btn)
            layout.addWidget(btn, i // 2, i % 2)