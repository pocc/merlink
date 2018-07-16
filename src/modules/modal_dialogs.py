#!/usr/bin/python3
from PyQt5.QtWidgets import QMessageBox

def error_dialog(message):
    error_dialog = QMessageBox()
    error_dialog.setIcon(QMessageBox.Critical)
    error_dialog.setWindowTitle("Error!")
    error_dialog.setText(message)
    error_dialog.exec_()


def question_dialog(message):
    question_dialog = QMessageBox()
    question_dialog.setIcon(QMessageBox.Question)
    question_dialog.setWindowTitle("Error!")
    question_dialog.setText(message)
    question_dialog.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
    question_dialog.setDefaultButton(QMessageBox.Yes)
    return question_dialog.exec_()

def feature_in_development():
    dev_message = QMessageBox()
    dev_message.setIcon(QMessageBox.Information)
    dev_message.setWindowTitle("Meraki Client VPN: Features in Progress")
    dev_message.setText('This feature is currently in progress.')
    dev_message.exec_()

