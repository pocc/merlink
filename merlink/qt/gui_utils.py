# -*- coding: utf-8 -*-
"""GUI utilities not tied to the main application object."""
import os
import signal
import psutil
import tempfile

from PyQt5.QtWidgets import QMessageBox


def check_for_duplicate_instance():
    """Abort if existing application found.
    This is for GUI instances where the window might be minimized.
    No ill effects should come from killing existing process.
    """
    pid = str(os.getpid())
    pidfile = tempfile.gettempdir() + "/merlink.pid"
    if os.path.isfile(pidfile):
        with open(pidfile) as f:
            previous_pid = f.read()
        # If the pidfile contents are non-numeric, just create a new process
        if previous_pid.isdigit() and previous_pid in psutil.pids():
            print("Killing existing Merlink at PID " + previous_pid)
            os.kill(int(previous_pid), signal.SIGTERM)
    with open(pidfile, 'w') as f:
        f.write(pid)


def show_error_dialog(message):
    """Show an error dialog with a message.

    This script contains multiple GUI modal dialogs:
    https://ux.stackexchange.com/questions/12045/what-is-a-modal-dialog-window

    "A modal dialog is a window that forces the user to interact with it
    before they can go back to using the parent application."

    Args:
        message (string): A message telling the user what is wrong.
    """
    error_dialog = QMessageBox()
    error_dialog.setIcon(QMessageBox.Critical)
    error_dialog.setWindowTitle("Error!")
    error_dialog.setText(message)
    error_dialog.exec_()


def show_question_dialog(message):
    """Send the user a question and record their decision.

    Args:
        message (string): A question asking the user what they want to do.
    Returns:
        result (QDialog.DialogCode): Returns a QDialog code of Rejected (no) |
        Accepted (yes) depending on user input.

    """
    question_dialog = QMessageBox()
    question_dialog.setIcon(QMessageBox.Question)
    question_dialog.setWindowTitle("Error!")
    question_dialog.setText(message)
    question_dialog.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
    question_dialog.setDefaultButton(QMessageBox.Yes)
    decision = question_dialog.exec_()
    return decision


def show_feature_in_development_dialog():
    """Informs the user that something is a feature in development."""
    fid_message = QMessageBox()
    fid_message.setIcon(QMessageBox.Information)
    fid_message.setWindowTitle("Meraki Client VPN: Features in Progress")
    fid_message.setText('This feature is currently in progress.')
    fid_message.exec_()


def vpn_status_dialog(title, message):
    """Tells the user the status of the VPN connection.

    args:
        title (string): A window title to summarize the message.
        message (string): A message to give to the user.
    """
    success_message = QMessageBox()
    success_message.setIcon(QMessageBox.Information)
    success_message.setWindowTitle(title)
    success_message.setText(message)
    success_message.exec_()
