from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QWidget


class ManualVpnSetupWidget(QWidget):
    """Class to manage first pane where you login."""
    def __init__(self, parent=None):
        super(ManualVpnSetupWidget, self).__init__(parent)
        layout = QHBoxLayout()
        self.button = QPushButton('Manual')
        layout.addWidget(self.button)
        self.setLayout(layout)
