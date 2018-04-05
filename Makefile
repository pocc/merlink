# maybe add targets to build wheel
PYTHONPATH := "$(shell pwd)/vendor"

PYTHON := PYTHONPATH=$(PYTHONPATH) "$(shell which python3)"
VENDOR := $(PYTHON) -m pip install --target $(PYTHONPATH)

default: vendor
	$(PYTHON) client_vpn.py

clean:
	$(RM) -r $(PYTHONPATH)

.PHONY: clean default

vendor: requirements.txt
	$(VENDOR) --upgrade pip # latest pip
	$(VENDOR) --upgrade -r requirements.txt
