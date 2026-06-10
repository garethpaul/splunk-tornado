.PHONY: audit build check lint test verify

PYTHON ?= python3
ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))

lint:
	$(PYTHON) -m py_compile "$(ROOT)/setup.py" "$(ROOT)/splunktornado/auth.py"
	$(PYTHON) "$(ROOT)/scripts/check_docs_plans.py"

test:
	cd "$(ROOT)" && $(PYTHON) -m unittest discover -s tests

build: lint
	$(PYTHON) -m build --no-isolation --outdir "$(ROOT)/dist" "$(ROOT)"

verify: lint test build

audit:
	$(PYTHON) -m pip_audit -r "$(ROOT)/requirements.txt" -r "$(ROOT)/requirements-dev.txt"

check: verify audit
