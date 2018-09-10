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

# maybe add targets to build wheel
VENDORPATH := $(shell pwd)/vendor
PYTHONPATH := ".:$(VENDORPATH)"

PYTHON := PYTHONPATH=$(PYTHONPATH) "$(shell which python3)"
VENDOR := $(PYTHON) -m pip install --target "$(VENDORPATH)"
PROJDIR := "$(shell pwd)"


clean:
	$(RM) -r ./build ./dist

# https://github.com/vintasoftware/python-linters-and-code-analysis
lint: vendor
    $(PYTHON) -m pylint ./

# TODO
test:
# https://wiki.python.org/moin/PyQt/GUI_Testing
	$(PYTHON) -m nose ./test

run: vendor
	$(PYTHON) merlink.py

# TODO
build: merlink.spec vendor
	$(PYTHON) -m PyInstaller $<

# TODO
# Install files to appropriate directory per-OS
install: build

# TODO
# Delete files created by `make install`
uninstall: build

# TODO
# Create a package for this platform (in build)
package: build

# TODO
# Build a binary for this platform (in dist)
bin: build merlink.spec

vendor: requirements.txt
	$(VENDOR) --upgrade pip
	$(VENDOR) --upgrade -r requirements.txt
