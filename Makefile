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

default: vendor
	$(PYTHON) ./src/merlink.py

clean:
	$(RM) -r "$(VENDORPATH)"

lint: vendor
	# https://github.com/vintasoftware/python-linters-and-code-analysis
	#$(PYTHON) -m pylint ./src # or whatever you use

test: lint vendor
	# https://wiki.python.org/moin/PyQt/GUI_Testing
	#$(PYTHON) -m nose ./test # or whatever you use

merlink.exe: merlink.spec vendor
	$(PYTHON) -m PyInstaller $<

merlink.zip: src vendor
	$(PYTHON) zip.py $@ $^

vendor: requirements.txt
	$(VENDOR) --upgrade pip # latest pip
	$(VENDOR) --upgrade -r requirements.txt