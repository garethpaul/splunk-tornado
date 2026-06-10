.PHONY: audit build check lint test verify

PYTHON ?= python3

lint:
	$(PYTHON) -m py_compile setup.py splunktornado/auth.py
	$(PYTHON) scripts/check_docs_plans.py

test:
	$(PYTHON) -m unittest discover -s tests

build: lint
	$(PYTHON) setup.py check

verify: lint test build

audit:
	$(PYTHON) -m pip_audit -r requirements.txt -r requirements-dev.txt

check: verify audit
