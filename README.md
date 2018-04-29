[![BCH compliance](https://bettercodehub.com/edge/badge/pocc/merlink?branch=master)](https://bettercodehub.com/)

# Merlink
This program will connect desktop clients to Meraki firewalls. This project is still in active development.

## MVP Featureset
* [ ] Functionality
  * [ ] Windows
    * [x] Ability to create VPN connections
    * [x] Executables
    * [ ] Autostart on Login
    * [ ] Systray icon that is minimized when connected
    * [x] Split Tunnel
* [x] Network Troubleshooting
  * [x] Basic validation tests prior to connection
    * [x] Is the MX online?
    * [x] Can the client ping the firewall's public IP?
    * [x] Is the user behind the firewall?
    * [x] Is Client VPN enabled?
    * [x] Is authentication type Meraki Auth?
    * [x] Are UDP ports 500/4500 port forwarded through firewall?
* [x] Web scraping
  * [x] Fetch primary IP address and DDNS
  * [x] Fetch organization/network list
  * [x] Connect to VPN with only those Dashboard credentials
* [ ] UI
  * [x] Skeleton UI
  * [x] Login dialog 
  * [x] Displays organizations/networks to connect to 
  * [ ] TFA compatibility
  * [ ] Preferences dialog to catalog VPN options
  * [ ] Image advert + link on login page
  * [ ] "I'm feeling lucky" button that will get info for and connect you to a random security appliance
  
## Installing Merlink
### Executables
Download the executables [here](https://github.com/pocc/merlink/releases).

### Building from Source
**1.** Clone the repository:

```git clone https://github.com/pocc/merlink```

**2.** Download the libraries with pip3

```pip3 install pyqt5 bs4 mechanicalsoup```

**3.** Execute the file

```python3 vpn_client.py```

### Prerequisites

* language: python3 
* libraries: pyqt5 bs4 mechanicalsoup cx_freeze

## Contributing

Please read [CONTRIBUTING.md](https://github.com/pocc/merlink/blob/master/docs/CONTRIBUTING.md) for the process for submitting pull requests.

### Setting up your environment
To set up your Windows environment, please read [pycharm_setup.md](https://github.com/pocc/merlink/blob/master/docs/pycharm_setup.md)

### Versioning

[SemVer](http://semver.org/) is used for versioning: 
* MAJOR version: Incompatible UI from previous version from a user's perspective
* MINOR version: Functionality is added to UI from a user's persective
* PATCH version: Backwards-compatible bug fixes

For the versions available, see the [tags on this repository](https://github.com/pocc/merlink/tags). 

## Addenda
### Reference Material
* [Qt5](https://doc.qt.io/qt-5/index.html) - Comprehensive Qt reference made by the Qt company. It is made for C++, but will supply the information you need about classes and functions.
* [PyQt5](http://pyqt.sourceforge.net/Docs/PyQt5/) - Documentation for PyQt5. This is a copypaste of the Qt docs applied to Python, and generally contains less useful information  
* [PyCharm](https://www.jetbrains.com/pycharm/) - IDE used
* [Python 3](https://www.python.org/) - Base language
* [Mechanical Soup](https://github.com/MechanicalSoup/MechanicalSoup) - Web scraper for Python 3
* [Powershell VPN Client docs](https://docs.microsoft.com/en-us/powershell/module/vpnclient/?view=win10-ps) - Collection of manpages for VPN Client-specific powershell functions.

### License

This project is licensed under the Apache License 2.0 - see the [LICENSE.md](LICENSE.md) file for details.

### Authors

* **Ross Jacobs** - *Initial work* - [pocc](https://github.com/pocc)

See also the list of [contributors](https://github.com/pocc/merlink/contributors) who participated in this project.

### Acknowledgments
Praise be Stack Overflow!
