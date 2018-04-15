# Merlink
This program will connect desktop clients to Meraki firewalls. These are the project's MVP featureset:
* [ ] Functionality
  * [ ] Ability to create VPN connections (Windows)
  * [ ] Executable (Windows)
  * [ ] Autostart on Login
  * [ ] Systray icon that is minimized when connected
  * [ ] Split Tunnel
* [ ] Network Troubleshooting
  * [ ] Basic validation tests prior to connection
    * [ ] Stuff
* [ ] Web scraping
  * [x] Fetch primary IP address and DDNS
  * [x] Fetch organization/network list
  * [ ] Connect to VPN with only those Dashboard credentials
* [ ] UI
  * [x] Skeleton UI
  * [x] Login dialog 
  * [x] Displays organizations/networks to connect to 
  * [ ] Preferences dialog to catalog VPN options
  * [ ] Image advert + link on login page
  * [ ] "I'm feeling lucky" button that will get info for and connect you to a random security appliance
  * [ ] Gray out GUI options that MVP (on that platform) won't have access to)
  

This project is still in active development.

## Getting Started
### Executables
Download the executables [here](https://github.com/pocc/merlink/tree/master/bin).

### Building from Source
1. Clone the repository:
> git clone https://github.com/pocc/merlink
2. Download the libraries with pip3
> pip3 install pyqt5 bs4 mechanicalsoup
3. Execute the file
> python3 vpn_client.py

### Prerequisites

* language: python3 
* libraries: pyqt5 bs4 mechanicalsoup cx_freeze

### Installing with PyCharm

1. Clone the repository:
> git clone https://github.com/pocc/merlink
2. Go to Settings > Project > Project Interpreter and download the missing libraries

This is what the initial screen looks like: 
<Insert image here>

## Running the tests

In development...

### Break down into end to end tests

In development...

### Coding style tests
In development...

## Built With

* [PyCharm](https://www.jetbrains.com/pycharm/) - IDE
* [Python 3](https://www.python.org/) - Base language
* [PyQt5](http://pyqt.sourceforge.net/Docs/PyQt5/) - Python GUI Toolkit

## Contributing

Please read [CONTRIBUTING.md](gist) for details on our code of conduct, and the process for submitting pull requests.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/pocc/merlink/tags). 

## Authors

* **Ross Jacobs** - *Initial work* - [pocc](https://github.com/pocc)

See also the list of [contributors](https://github.com/pocc/merlink/contributors) who participated in this project.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE.md](LICENSE.md) file for details.

## Acknowledgments
Praise be Stack Overflow! 
