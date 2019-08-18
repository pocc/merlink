"""
Before the user is shown the VPN setup screens, show the user the login screen.
There should be an option to skip Dashboard login to show manual login
"""
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.Qt import QPixmap

from merlink.os_utils import pyinstaller_path


class LoginWindowUi:
    """This class manages the system tray icon of the main program, post-login.
    Attributes:
        app (QMainWindow): Set to MainWindow object (required binding for Qt)
    """

    def __init__(self, app):
        self.app = app
        self.login_widget_setup()
        self.login_window_setup()
        self.login_set_layout()

    def login_widget_setup(self):
        """Take login self.app.and add widgets to it."""
        # Copying style from Dashboard Login
        # (https://account.meraki.com/login/dashboard_login)
        self.app.heading_style = \
            "font-family: verdana, sans-serif; font-style: normal; font-size" \
            ": 28px; font-weight: 300; color:  #606060;"
        self.app.label_style = "font-family: verdana, sans-serif; font-style" \
                               ": normal; font-size: 13px; color: #606060;"
        self.app.link_style = "font-family: verdana, sans-serif; font-style:" \
                              " normal; font-size: 13px; color: #1795E6;"
        self.app.heading = QLabel("Dashboard Login")
        self.app.heading.setStyleSheet(self.app.heading_style)
        self.app.username_lbl = QLabel("Email")
        self.app.username_lbl.setStyleSheet(self.app.label_style)
        self.app.password_lbl = QLabel("Password")
        self.app.password_lbl.setStyleSheet(self.app.label_style)
        self.app.username_field = QLineEdit(self.app)
        self.app.password_field = QLineEdit(self.app)
        # Reset password field to '', especially if login failed
        self.app.password_field.setText('')
        # Masks password as a series of dots instead of characters
        self.app.password_field.setEchoMode(QLineEdit.Password)
        self.app.login_btn = QPushButton("Log in")

        # self.app.login_btn.setStyleSheet(self.app.login_btn_style)
        self.app.forgot_password_lbl = \
            QLabel("<a href=\"https://account.meraki.com/login/reset_password"
                   "\" style=\"color:#1795E6;text-decoration:none\">"
                   "I forgot my password</a>")
        self.app.forgot_password_lbl.setStyleSheet(self.app.link_style)
        self.app.forgot_password_lbl.setOpenExternalLinks(True)
        self.app.create_account_lbl = \
            QLabel(" <a href=\"https://account.meraki.com/login/signup\" "
                   "style=\"color:#1795E6;text-decoration:none\">"
                   "Create an account</a>")
        self.app.create_account_lbl.setStyleSheet(self.app.link_style)
        self.app.create_account_lbl.setOpenExternalLinks(True)
        self.app.about_lbl = \
            QLabel("<a href=\"https://github.com/pocc/merlink\" style=\""
                   "color:#1795E6;text-decoration:none\">About</a>")
        self.app.about_lbl.setStyleSheet(self.app.link_style)
        self.app.about_lbl.setOpenExternalLinks(True)

        # Set up username and password so these vars have values
        self.app.username = ''
        self.app.password = ''

    def login_window_setup(self):
        """Set options for the login window self.app."""
        self.app.setModal(True)  # Make the login window prevent program usage
        self.app.meraki_img = QLabel()
        self.app.meraki_img.setOpenExternalLinks(True)
        pixmap = QPixmap(pyinstaller_path('media/cloud_miles.png'))
        self.app.meraki_img.setPixmap(pixmap)
        # Background for program should be #Meraki green = #78be20
        self.app.setStyleSheet("background-color:#eee")
        self.app.setWindowTitle('MerLink - Login Window')

    def login_set_layout(self):
        """Tie login layout to QDialog object."""
        layout_login_options = QHBoxLayout()
        layout_login_options.addWidget(self.app.forgot_password_lbl)
        layout_login_options.addStretch()
        layout_login_options.addWidget(self.app.create_account_lbl)

        # Create a widget to contain the login layout.
        # This allows us to paint the background of the widget
        login_widget = QWidget(self.app)
        login_widget.setStyleSheet("background-color:#fff")
        # Create labels and textboxes to form a login layout
        layout_login = QVBoxLayout(login_widget)
        layout_login.addStretch()
        layout_login.addWidget(self.app.heading)
        layout_login.addWidget(self.app.username_lbl)
        layout_login.addWidget(self.app.username_field)
        layout_login.addWidget(self.app.password_lbl)
        layout_login.addWidget(self.app.password_field)
        layout_login.addWidget(self.app.login_btn)
        layout_login.addLayout(layout_login_options)
        layout_login.addStretch()
        layout_login.addStretch()
        layout_login.addWidget(self.app.about_lbl)

        layout_main = QHBoxLayout()
        layout_main.addWidget(login_widget)
        layout_main.addWidget(self.app.meraki_img)
        self.app.setLayout(layout_main)


class TfaDialogUi:
    """This class manages the system tray icon of the main program, post-login.
    Attributes:
        app (QMainWindow): Set to MainWindow object (required binding for Qt)
    """

    def __init__(self, app):
        self.app = app
        self.login_tfa_set_layout()
        self.tfa_widget_setup()
        self.tfa_set_layout()

    def login_tfa_set_layout(self):
        """Set the layout for the tfa dialog."""
        # Required to have this class variables as it is not possible to
        # return/pass values to/from triggered functions (self.app.tfa_verify)
        self.app.get_twofactor_code = QLineEdit()
        self.app.twofactor_dialog = QDialog()

    def tfa_widget_setup(self):
        """Set up the two-factor dialog UI."""
        self.app.get_twofactor_code.clear()  # Clear if exists
        # QDialog that gets 6 digit two-factor code
        self.app.twofactor_dialog.setWindowTitle("Two-Factor Authentication")

        self.app.twofactor_code_label = QLabel("Enter verification code")
        self.app.twofactor_dialog_yesno = QHBoxLayout()
        self.app.yesbutton = QPushButton("Verify")
        self.app.yesbutton.setToolTip("Attempt connection with this tfa code")
        self.app.nobutton = QPushButton("Cancel")
        self.app.yesbutton.setToolTip("Quit")
        self.app.twofactor_dialog_yesno.addWidget(self.app.yesbutton)
        self.app.twofactor_dialog_yesno.addWidget(self.app.nobutton)

    def tfa_set_layout(self):
        """Set up the TFA layout."""
        # Layout code
        dialog_layout = QVBoxLayout()
        twofactor_code_layout = QHBoxLayout()
        twofactor_code_layout.addWidget(self.app.twofactor_code_label)
        twofactor_code_layout.addWidget(self.app.get_twofactor_code)
        dialog_layout.addLayout(twofactor_code_layout)
        # dialog_layout.addWidget(self.app.get_remember_choice)
        dialog_layout.addLayout(self.app.twofactor_dialog_yesno)
        self.app.twofactor_dialog.setLayout(dialog_layout)
