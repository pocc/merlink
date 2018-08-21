# -*- coding: utf-8 -*-
# Copyright 2018 Ross Jacobs All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

""" https://ux.stackexchange.com/questions/12045/what-is-a-modal-dialog-window

    "A modal dialog is a window that forces the user to interact with it
    before they can go back to using the parent application."

This script contains multiple GUI modal dialogs."""


# Python modules
from PyQt5.QtWidgets import QMessageBox


def show_error_dialog(message):
    """Show an error dialog with a message.

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


def vpn_success_dialog():
    """Tells the user that the VPN connection has been successful."""
    success_message = QMessageBox()
    success_message.setIcon(QMessageBox.Information)
    success_message.setWindowTitle("Success!")
    success_message.setText("Successfully Connected!")
    success_message.exec_()
