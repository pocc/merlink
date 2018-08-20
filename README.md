[![Build Status](https://travis-ci.org/pocc/merlink.svg?branch=master)](https://travis-ci.org/pocc/merlink)
[![Build status](https://ci.appveyor.com/api/projects/status/ktmvfms5ithcevcl/branch/master?svg=true)](https://ci.appveyor.com/project/pocc/merlink/branch/master)
[![BCH compliance](https://bettercodehub.com/edge/badge/pocc/merlink?branch=master)](https://bettercodehub.com/)

# MerLink
This program will connect desktop devices to Meraki firewalls via an 
L2TP/IPSEC connection. This program uses a Meraki dashboard admin's 
credentials to pull the data required for a Client VPN connection, create 
the connection with OS built-ins, and then connect. 

## Current Feature Set (targeting v1.0.0)
* Authentication/Authorization
    * Dashboard admins/Guest users supported with Meraki Auth
    * TFA prompt supported
    * Only networks/organizations that that user has access to are shown

* VPN Connection (Windows-only)
    * Split Tunnel
    * Remember Credential

* Platforms
    * Windows 7/8/10
    * macOS 10.7-13
    * linux (requires network-manager)

* CI/CD on tagged commits 
    * Windows 10
    * macOS 10.13
    * Ubuntu 14.04
    * Ubuntu 16.04

* Troubleshooting tests on connection failure
  * Is the MX online?
  * Can the client ping the firewall's public IP?
  * Is the user behind the firewall?
  * Is Client VPN enabled?
  * Is authentication type Meraki Auth?
  * Are UDP ports 500/4500 port forwarded through firewall?
 
The goals for future major versions can be found in the 
[Project list](https://github.com/pocc/merlink/projects).
  
## Installing Merlink
### Executables
Download the executables [here](https://github.com/pocc/merlink/releases).

### Building from Source
**1.** Clone the repository:

```git clone https://github.com/pocc/merlink```

**2.** Download the required libraries with pip3

```pip3 install requirements.txt```

**3.** Execute the file

```python3 merlink.py```

## Contributing

Please read [CONTRIBUTING.md](https://github.com/pocc/merlink/blob/master/docs/CONTRIBUTING.md) 
for the process for submitting pull requests.

### Setting up your environment
To set up your Windows environment, please read 
[pycharm_setup.md](https://github.com/pocc/merlink/blob/master/docs/pycharm_setup.md)


### Versioning

[SemVer](http://semver.org/) is used for versioning: 
* MAJOR version: Incompatible UI from previous version from a user's perspective
* MINOR version: Functionality is added to UI from a user's persective
* PATCH version: Minor enhancements and bug fixes

For the versions available, see the [tags on this repository](https://github.com/pocc/merlink/tags). 

### Branching
Adapting [Git Branching](http://nvie.com/posts/a-successful-git-branching-model/) 
for this projcet

* **iss#-desc**: Branch from dev and reintegrate to dev. Should be tied  to 
an issue tagged with 'bug', 'feature', or 'enchancement' on repo. 
* **dev**: Development branch. When it's ready for a release,  branch into a 
release.
* **master**: Master branch.

## Addenda
### Reference Material
#### Language and Libraries
* [Python 3](https://www.python.org/) - Base language
* [Qt5](https://doc.qt.io/qt-5/index.html) - Comprehensive Qt reference made
  by the Qt company. It is made for C++, but will supply the information you
    need about classes and functions.
* [PyQt5](http://pyqt.sourceforge.net/Docs/PyQt5/) - Documentation for PyQt5.
  This is a copypaste of the Qt docs applied to Python, and generally 
  contains less useful information  
* [Mechanical Soup](https://github.com/MechanicalSoup/MechanicalSoup) - Web 
 scraper for Python 3

#### Environment
* [PyCharm](https://www.jetbrains.com/pycharm/) - IDE used

#### General Documentation
* [Powershell VPN Client docs](https://docs.microsoft.com/en-us/powershell/module/vpnclient/?view=win10-ps) -
Collection of manpages for VPN Client-specific powershell functions.

#### Style Guide
* [Google Python Style Guide (2018)](https://github.com/google/styleguide/blob/gh-pages/pyguide.md)

#### Building
* [PyInstaller](https://pyinstaller.readthedocs.io/en/v3.3.1/) - Python 
 bundler used as part of this project 
    * [PyInstaller Recipes](https://github.com/pyinstaller/pyinstaller/wiki/Recipes) - 
    Useful example code
    * Make sure you install the latest PyIntstaller directly:
    
    `pip install https://github.com/pyinstaller/pyinstaller/archive/develop.zip
`
* [NSIS](http://nsis.sourceforge.net/Docs/) - Windows program installer system
    * [NSIS Wizard + IDE](http://hmne.sourceforge.net/) - Will build and 
     debug NSIS scripts
    * [NSIS Sample Installers](http://nsis.sourceforge.net/Category:Real_World_Installers) - 
     To learn how to build your own installer by example
* [FPM](https://github.com/jordansissel/fpm) - A way to package to targets 
 deb, rpm, pacman, and osxpkg

### License

This project is licensed under the Apache License 2.0 - see the 
[LICENSE.md](LICENSE.md) file for details.

### Authors

* **Ross Jacobs** - *Initial work* - [pocc](https://github.com/pocc)

See also the list of 
[contributors](https://github.com/pocc/merlink/contributors) who participated 
in this project.

### Acknowledgments
Praise be Stack Overflow!