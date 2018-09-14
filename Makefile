# Copyright 2018 Ross Jacobs All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Philosophy on Makefile: Syntax is annoying, so get it to work and then
# proxy to scripts in other languages if possible.

.PHONY: help run lint test configure build clean clean_all all
.PHONY: package install docs publish

VENV_NAME = venv/bin/activate
PYTHON := $(shell which python3)
WHICH_PIP := $(shell which pip)
PYTHONFILES := merlink.py src/ docs/ test/ pkg/
ROOTDIR := "$(shell pwd)"
UNAME_S := "$(shell uname -s)"


    #############
    ### USING ###
    #############


help:
	@echo "USING"
	@echo "  help:       Execute this message"
	@echo "  run:         Run the program for this project"
	@echo "  lint:        Run pylint, flake8, radon, & dodgy for clean code"
	@echo "  test:        Run the tests to generate coverage (in development)"
	@echo "CONFIGURING"
	@echo "  configure:   Download and install all dependencies with pip"
	@echo "  venv:        Create a virtualenv for this project"
	@echo "  clean:       Remove the build artifacts"
	@echo "  clean_all:   Remove the virtualenv and build artifacts"
	@echo "PACKAGING"
	@echo "  install:     Install locally to dist/merlink/"
	@echo "  package:     Create an exe/dmg/deb+rpm for this OS in build/"
	@echo "  archive      Compress merlink into tar (POSIX systems) or zip"
	@echo "  docs:        Compile documentation using sphinx with `make html`"
	@echo "  publish:     Upload to PyPy"


.DEFAULT: help

run: venv
	$(PYTHON) merlink.py

# Linting with pylint, flake8, radon.
lint: $(PYTHONFILES) venv
	$(PYTHON) -m pylint $(PYTHONFILES)
	$(PYTHON) -m flake8 $(ROOTDIR)
	radon cc -nc $(PYTHONFILES)
	radon mi -nc $(PYTHONFILES)

# https://wiki.python.org/moin/PyQt/GUI_Testing
#	$(PYTHON) -m nose ./test
test:
	@echo "Feature in progress..."


    ################
    ### BUILDING ###
    ################


configure:
# If python3 isn't installed, quit.
ifeq ("$(PYTHON)","")
	@echo "python3 is not installed and is required. Exiting..."
	exit 1
endif
# If pip is missing, install it.
ifeq ("$(WHICH_PIP)","")
	curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py;
	python get-pip.py
endif
	$(PYTHON) -m pip install -U pip


venv: venv/bin/activate configure
PYTHON = venv/bin/python3
ifeq ("$(UNAME_S)", "Linux")
	VENV_ACTIVATE = $(shell source $(VENV_NAME))
else ifeq ("$(UNAME_S)", "Darwin")
	VENV_ACTIVATE = $(shell source $(VENV_NAME))
else
	VENV_ACTIVATE = $(shell $(VENV_NAME))
endif


venv/bin/activate: setup.py
	virtualenv -p python3 venv
ifeq ("$(UNAME_S)", "Darwin")
	$(PYTHON) -m pip install dmgbuild
endif
	$(PYTHON) -m pip install -e .
	$(PYTHON) -m pip install -Ur requirements.txt
	$(VENV_ACTIVATE)


clean:
	$(RM) -r ./build ./dist


clean_all: clean
	$(RM) -r ./venv
	exit



    #################
    ### PACKAGING ###
    #################


all: install
install: venv
	$(PYTHON) -m PyInstaller -y merlink.spec


package: install
	$(PYTHON) pkg/make_package.py


archive: setup.py
	$(PYTHON) setup.py sdist


# Trigger Sphinx's makefile `make html`
docs:
	cd docs; make html;


# When this gets on PyPy
publish: