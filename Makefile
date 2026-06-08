.PHONY: build check lint test verify

PYTHON ?= python3

lint:
	$(PYTHON) -m py_compile setup.py splunktornado/auth.py
	$(PYTHON) scripts/check_docs_plans.py

test:
	$(PYTHON) -m unittest discover -s tests

build: lint
	$(PYTHON) setup.py check

verify: lint test build

check: verify
