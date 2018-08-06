# PyQt5
from PyQt5.QtWidgets import QListWidgetItem, QListWidget
from PyQt5.QtGui import QIcon

# Local modules
from src.modules.pyinstaller_path_helper import resource_path


def tshoot_failed_vpn_dialog(has_passed_validation):
    validation_list = QListWidget()
    validation_textlist = [
        "Is the MX online?",
        "Can the client ping the firewall's public IP?",
        "Is the user behind the firewall?",
        "Is Client VPN enabled?",
        "Is authentication type Meraki Auth?",
        "Are UDP ports 500/4500 port forwarded through firewall?"]
    # "Is the user authorized for Client VPN?",
    # For as many times as items in the validation_textlist
    for i in range(len(validation_textlist)):
        # Initialize a QListWidgetItem out of a string
        item = QListWidgetItem(validation_textlist[i])
        validation_list.addItem(item)  # Add the item to the QListView

    for i in range(len(validation_textlist)):
        print("has passed" + str(i) + str(has_passed_validation[i]))
        if has_passed_validation[i]:
            validation_list.item(i).setIcon(
                QIcon(resource_path('src/media/checkmark-16.png')))
        else:
            validation_list.item(i).setIcon(
                QIcon(resource_path('src/media/x-mark-16.png')))
