#!/usr/bin/env bash
# See where we are drawing updates from
cat /etc/apt/sources.list
# sudo apt-get update MUST be run in before_install
sudo apt-get update -qq
# Required for trusty and xenial, but fails on bionic
sudo apt install qt5-default
# Required for rpmbuild to build rpm with fpm
sudo apt-get install -y rpm build-essential
