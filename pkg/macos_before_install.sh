#!/usr/bin/env bash
# Update brew and install python3
brew update
brew install python3
# Install pip and venv and then activate
python3 -m easy_install pip
python3 -m pip install virtualenv
virtualenv venv
source venv/bin/activate
