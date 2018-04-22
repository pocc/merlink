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
    * [ ] Split Tunnel
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
  * [ ] Gray out GUI options that MVP (on that platform) won't have access to)  
  
## Getting Started
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

## Built With

* [PyCharm](https://www.jetbrains.com/pycharm/) - IDE
* [Python 3](https://www.python.org/) - Base language
* [PyQt5](http://pyqt.sourceforge.net/Docs/PyQt5/) - Python GUI Toolkit
* [Mechanical Soup](https://github.com/MechanicalSoup/MechanicalSoup) - Web scraper for Python 3

## Contributing

Please read [CONTRIBUTING.md](https://github.com/pocc/merlink/blob/merlink/CONTRIBUTING.md) for the process for submitting pull requests.
To set up your Windows environment, please read [ENV_SETUP.md](https://github.com/pocc/merlink/blob/merlink/ENV_SETUP.md)

## Versioning

[SemVer](http://semver.org/) is used for versioning: 
* MAJOR version: Incompatible UI from previous version from a user's perspective
* MINOR version: Functionality is added to UI from a user's persective
* PATCH version: Backwards-compatible bug fixes

For the versions available, see the [tags on this repository](https://github.com/pocc/merlink/tags). 

## Authors

* **Ross Jacobs** - *Initial work* - [pocc](https://github.com/pocc)

See also the list of [contributors](https://github.com/pocc/merlink/contributors) who participated in this project.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE.md](LICENSE.md) file for details.

## Acknowledgments
Praise be Stack Overflow!
