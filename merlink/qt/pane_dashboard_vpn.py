from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QWidget


class DashboardVpnSetupWidget(QWidget):
    """Class to manage first pane where you login."""
    def __init__(self, parent=None):
        super(DashboardVpnSetupWidget, self).__init__(parent)
        layout = QHBoxLayout()
        self.button = QPushButton('Dashboard')
        layout.addWidget(self.button)
        self.setLayout(layout)
