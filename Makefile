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
WHICH_PIP := "$(shell which pip)"
WHICH_PIPENV := "$(shell which pipenv)"
PYTHONFILES := merlink.py src/ docs test/ pkg/
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
	@echo "  build:       Compile OS-specific program files to dist/merlink/"
	@echo "  clean:       Remove the build artifacts."
	@echo "  clean_all:   Remove the virtualenv and build artifacts."
	@echo "PACKAGING"
	@echo "  package:     Create a distributable executable for this OS."
	@echo "  install:     Install program files to this computer."
	@echo "  uninstall:   Delete installation files."
	@echo "  docs:        Compile documentation using sphinx with `make html`."
	@echo "  publish:     Upload to PyPy."


.PHONY : default
default: help


.PHONY : run
run: pipenv
	$(PYTHON) merlink.py


.PHONY : lint
# Linting with pylint, flake8, radon.
lint: $(PYTHONFILES) pipenv
	$(PYTHON) -m pylint $(PYTHONFILES)
	$(PYTHON) -m flake8 $(ROOTDIR)
	radon cc -nc $(PYTHONFILES)
	radon mi -nc $(PYTHONFILES)


.PHONY : test
# https://wiki.python.org/moin/PyQt/GUI_Testing
#	$(PYTHON) -m nose ./test
test:
	@echo "Feature in progress..."



    ################
    ### BUILDING ###
    ################

.PHONY : pipenv
pipenv: requirements.txt
# If python3 isn't installed, quit.
ifeq ("$(PYTHON)","")
	@echo "python3 is not installed and is required. Exiting..."
	exit 1
endif
# If pip is missing, install it.
ifeq ("$(WHICH_PIP)","")
	curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
	python get-pip.py
endif
ifeq ("$(WHICH_PIPENV)","")
	$(PYTHON) -m pip install pipenv
endif
	$(PYTHON) -m pipenv install -r requirements.txt
# If the user is already in a pipenv shell, they'll get an error stating such.
	$(PYTHON) -m pipenv shell


.PHONY : build
build: merlink.spec vendor
	$(PYTHON) -m PyInstaller -y $<


.PHONY : clean
clean:
	$(RM) -r ./build ./dist


.PHONY : clean_all
clean_all:
	$(CLEAN)
	pipenv --rm
	exit



    #################
    ### PACKAGING ###
    #################


.PHONY : exe
exe: build
	$(PYTHON) pkg/make_exe.py


.PHONY : all
all: install
.PHONY : install
install: build
	$(PYTHON) pkg/make_install.py


.PHONY : uninstall
uninstall:
	$(PYTHON) pkg/make_uninstall.py


.PHONY : docs
# Trigger Sphinx's makefile `make html`
docs:
	cd docs; make html;


# When this gets on PyPy
.PHONY : publish
publish: