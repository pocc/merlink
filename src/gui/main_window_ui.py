from PyQt5.QtWidgets import \
    (QFrame, QStatusBar, QComboBox, QVBoxLayout, QHBoxLayout, QRadioButton, 
     QCheckBox, QSpinBox, QLineEdit, QPushButton, QWidget, QLabel)


class MainWindowUi:
    # Telling PyCharm linter not to (incorrectly) inspect PyQt function args
    # noinspection PyArgumentList

    # Taking in 'app', which is the MainWindow object
    def __init__(self, app):
        # MAIN INIT UI
        # QMainWindow requires that a central app be set
        self.app = app
        app.cw = QWidget(app)
        app.setCentralWidget(app.cw)
        # CURRENT minimum width of Main Window
        # SUBJECT TO CHANGE as features are added
        # self.cw.setMinimumWidth(400)

        app.setWindowTitle('Merlink - VPN Client for Meraki firewalls')
        
        # Create a horizontal line above the status bar to highlight it        
        app.hline = QFrame()
        app.hline.setFrameShape(QFrame.HLine)
        app.hline.setFrameShadow(QFrame.Sunken)
        
        app.status = QStatusBar()
        app.status.showMessage("Status: Select organization")
        app.status.setStyleSheet("Background: white")

        # Set initial vars for username/password fields for dasboard/guest user
        app.radio_username_label = QLabel("Email")
        app.radio_username_label.setStyleSheet("color: #606060")  # Gray
        app.radio_username_textfield = QLineEdit()
        app.radio_password_label = QLabel("Password")
        app.radio_password_label.setStyleSheet("color: #606060")  # Gray
        app.radio_password_textfield = QLineEdit()
        app.radio_password_textfield.setEchoMode(QLineEdit.Password)
        
        # Title is an NSIS uninstall reference (see Modern.nsh)
        app.org_dropdown = QComboBox()
        app.org_dropdown.addItems(["-- Select an Organzation --"])
        app.network_dropdown = QComboBox()
        app.network_dropdown.setEnabled(False)
        
        app.user_auth_section = QVBoxLayout()
        app.radio_user_layout = QHBoxLayout()
        app.user_auth_section.addLayout(app.radio_user_layout)
        app.radio_dashboard_admin_user = QRadioButton("Dashboard Admin")
        # Default is to have dashboard user
        app.radio_dashboard_admin_user.setChecked(True)
        app.radio_guest_user = QRadioButton("Guest User")
        app.radio_user_layout.addWidget(app.radio_dashboard_admin_user)
        app.radio_user_layout.addWidget(app.radio_guest_user)
        app.radio_dashboard_admin_user.toggled.connect(
            self.set_dashboard_user_layout)
        app.radio_guest_user.toggled.connect(self.set_guest_user_layout)

        app.user_auth_section.addWidget(app.radio_username_label)
        app.user_auth_section.addWidget(app.radio_username_textfield)
        app.user_auth_section.addWidget(app.radio_password_label)
        app.user_auth_section.addWidget(app.radio_password_textfield)
        
        # Ask the user for int/str values if they want to enter them
        app.idle_disconnect_layout = QHBoxLayout()
        app.idle_disconnect_chkbox = QCheckBox("Idle disconnect seconds?")
        app.idle_disconnect_spinbox = QSpinBox()
        app.idle_disconnect_spinbox.setValue(0)
        # Negative seconds aren't useful here
        app.idle_disconnect_spinbox.setMinimum(0)
        app.idle_disconnect_layout.addWidget(app.idle_disconnect_chkbox)
        app.idle_disconnect_layout.addWidget(app.idle_disconnect_spinbox)
        
        app.dns_suffix_layout = QHBoxLayout()
        app.dns_suffix_chkbox = QCheckBox("DNS Suffix?") 
        app.dns_suffix_txtbox = QLineEdit('-')
        app.dns_suffix_layout.addWidget(app.dns_suffix_chkbox)
        app.dns_suffix_layout.addWidget(app.dns_suffix_txtbox)
        
        # Boolean asks of the user
        app.split_tunneled_chkbox = QCheckBox("Split-Tunnel?")
        app.remember_credential_chkbox = QCheckBox("Remember Credentials?")
        app.use_winlogon_chkbox = QCheckBox("Use Windows Logon Credentials")
        
        app.connect_btn = QPushButton("Connect")
        vert_layout = QVBoxLayout()

        # Add Dashboard Entry-only dropdowns
        vert_layout.addWidget(app.org_dropdown)
        vert_layout.addWidget(app.network_dropdown)
        vert_layout.addLayout(app.user_auth_section)

        # Add layouts for specialized params
        vert_layout.addLayout(app.idle_disconnect_layout)
        vert_layout.addLayout(app.dns_suffix_layout)

        # Add checkboxes
        vert_layout.addWidget(app.split_tunneled_chkbox)
        vert_layout.addWidget(app.remember_credential_chkbox)
        vert_layout.addWidget(app.use_winlogon_chkbox)

        # Add stuff at bottom
        vert_layout.addWidget(app.connect_btn)
        vert_layout.addWidget(app.hline)
        vert_layout.addWidget(app.status)

        app.cw.setLayout(vert_layout)

    def set_dashboard_user_layout(self):
        self.app.radio_username_textfield.setText(self.app.browser.username)
        self.app.radio_username_textfield.setReadOnly(True)
        self.app.radio_password_textfield.setText(self.app.browser.password)
        self.app.radio_password_textfield.setReadOnly(True)

    def set_guest_user_layout(self):
        self.app.radio_username_textfield.clear()
        self.app.radio_username_textfield.setReadOnly(False)
        self.app.radio_password_textfield.clear()
        self.app.radio_password_textfield.setReadOnly(False)
