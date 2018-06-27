#!/usr/bin/env bash
# See where we are drawing updates from
cat /etc/apt/sources.list
# sudo apt-get update MUST be run in before_install
sudo apt-get update -qq
# Required for trusty and xenial
sudo apt-get install python3 python3-pip

### FPM
# Required for rpmbuild to build rpm with fpm
sudo apt-get install -y rpm build-essential
# Install ruby meta packages
sudo apt-get install -y ruby ruby-dev rubygems-integration
sudo gem install --no-ri --no-rdoc fpm
