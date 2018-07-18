#!/usr/bin/python3
# This program will connect desktop clients to Meraki firewalls
# Build this with './venv/bin/python3 setup.py build' from project root

# This file is an entry point to start the controller (MVC)
from src.modules.controller import Controller


def main():
    Controller()


if __name__ == '__main__':
    main()
