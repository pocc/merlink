#!/usr/bin/python3

# ~ https://ux.stackexchange.com/questions/12045/what-is-a-modal-dialog-window
# "A modal dialog is a window that forces the user to interact with it
# before they can go back to using the parent application."


# Python modules
from PyQt5.QtWidgets import QMessageBox


def show_error_dialog(message):
    error_dialog = QMessageBox()
    error_dialog.setIcon(QMessageBox.Critical)
    error_dialog.setWindowTitle("Error!")
    error_dialog.setText(message)
    error_dialog.exec_()


def show_question_dialog(message):
    question_dialog = QMessageBox()
    question_dialog.setIcon(QMessageBox.Question)
    question_dialog.setWindowTitle("Error!")
    question_dialog.setText(message)
    question_dialog.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
    question_dialog.setDefaultButton(QMessageBox.Yes)
    return question_dialog.exec_()


def show_feature_in_development_dialog():
    fid_message = QMessageBox()
    fid_message.setIcon(QMessageBox.Information)
    fid_message.setWindowTitle("Meraki Client VPN: Features in Progress")
    fid_message.setText('This feature is currently in progress.')
    fid_message.exec_()


def vpn_success_dialog():
    success_message = QMessageBox()
    success_message.setIcon(QMessageBox.Information)
    success_message.setWindowTitle("Success!")
    success_message.setText("Successfully Connected!")
    success_message.exec_()
