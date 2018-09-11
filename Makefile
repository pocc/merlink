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

PYTHON := PYTHONPATH=$(PYTHONPATH) "$(shell which python3)"
PYTHONFILES := merlink.py src docs test pkg
VENV := $(shell pwd)/venv
ROOTDIR := "$(shell pwd)"


	#############
	### USING ###
	#############

.PHONY: help
help:
	@echo "USING"
	@echo "  help:       Execute this message."
	@echo "  run:         Run the program for this project."
	@echo "  lint:        Run pylint, flake8, radon, & dodgy for clean code."
	@echo "  test:        Run the tests to generate coverage (in development)."
	@echo "BUILDING"
	@echo "  pipenv:      Create a venv and install all dependencies in it."
	@echo "  build:       Compile program files specific to this OS."
	@echo "  clean:       Remove the build artifacts."
	@echo "  clean_all:   Remove the virtualenv and build artifacts."
	@echo "PACKAGING"
	@echo "  package:     Create a distributable executable for this OS."
	@echo "  install:     Install program files to this computer."
	@echo "  uninstall:   Delete installation files."
	@echo "  docs:        Compile documentation using sphinx."
	@echo "  publish:     Upload to PyPy."

.PHONY : default
default: help

.PHONY : all
all: install

# Linting with pylint, flake8, radon.
# Checking for commits with sensitive info with dodgy.
.PHONY : lint
lint: $(PYTHONFILES) vendor
	$(PYTHON) -m pylint $(PYTHONFILES)
	$(PYTHON) -m flake8 $(PYTHONFILES)
	radon cc -nc $(PYTHONFILES)
	radon mi -nc $(PYTHONFILES)
	dodgy $(PYTHONFILES)

.PHONY : test
test:
	@echo "Feature in progress..."
# https://wiki.python.org/moin/PyQt/GUI_Testing
#	$(PYTHON) -m nose ./test


	################
	### BUILDING ###
	################

.PHONY : pipenv
pipenv: requirements.txt
# If Pipfile does not exist
ifeq ("$(wildcard ./Pipfile)","")
	$(PYTHON) -m pip install pipenv
	$(PYTHON) -m pipenv install -r requirements.txt
	$(PYTHON) -m pipenv shell $(ROOTDIR)
endif

.PHONY : run
run: pipenv
	$(PYTHON) merlink.py

.PHONY : build
build: merlink.spec vendor
	$(PYTHON) -m PyInstaller -y $<

.PHONY : clean
clean:
	$(RM) -r ./build ./dist

.PHONY : clean_all
clean_all:
	$(RM) -r ./build ./dist ./venv

	#################
	### PACKAGING ###
	#################

# Create a package for this platform (in build)
.PHONY : package
package: build
	$(PYTHON) pkg/package.py

# Install files to appropriate directory per-OS
.PHONY : install
install: build
	$(PYTHON) pkg/install.py

# Delete files created by `make install`
.PHONY : uninstall
uninstall:
	$(PYTHON) pkg/uninstall.py

# Generate Sphinx HTML docuentation
.PHONY : html
html:
	cd docs
	make html

# When this gets on PyPy
# publish: