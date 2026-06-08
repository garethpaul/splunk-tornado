.PHONY: lint test build verify

PYTHON ?= python3

lint:
	$(PYTHON) -m py_compile setup.py splunktornado/auth.py

test:
	$(PYTHON) -m unittest discover -s tests

build: lint
	$(PYTHON) setup.py check

verify: lint test build
