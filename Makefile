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

.PHONY: clean default lint test

merlink.exe: merlink.spec vendor
	$(PYTHON) -m PyInstaller $<

merlink.zip: src vendor
	$(PYTHON) zip.py $@ $^

vendor: requirements.txt
	$(VENDOR) --upgrade pip # latest pip
	$(VENDOR) --upgrade -r requirements.txt
