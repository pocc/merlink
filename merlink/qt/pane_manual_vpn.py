from PyQt5.QtWidgets import QWidget


class ManualVpnSetupWidget(QWidget):
    """Class to manage first pane where you login."""
    def __init__(self, parent, layout):
        super(ManualVpnSetupWidget, self).__init__(parent)
        self.setLayout(layout)
