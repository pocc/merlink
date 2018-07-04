#!/usr/bin/env bash
# Update brew and install python3
brew update
brew install python3
# Install pip and venv and then activate
python -m easy_install pip
pip install venv
python3 -m venv venv
source venv/bin/activate
