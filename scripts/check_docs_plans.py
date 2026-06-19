#!/usr/bin/env python
from __future__ import print_function

import glob
import os
import sys


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOCS_PLANS = os.path.join(ROOT, "docs", "plans")
CANONICAL_PLAN = os.path.join(DOCS_PLANS, "2026-06-08-splunk-tornado-baseline.md")
CONTENT_DISPATCH_PLAN = os.path.join(DOCS_PLANS, "2026-06-09-exact-content-type-dispatch.md")
REPEATED_ARGS_PLAN = os.path.join(DOCS_PLANS, "2026-06-09-repeated-parameter-encoding.md")
CI_PLAN = os.path.join(DOCS_PLANS, "2026-06-10-ci-baseline.md")
PACKAGE_PLAN = os.path.join(DOCS_PLANS, "2026-06-10-package-build-matrix.md")
ASYNC_PLAN = os.path.join(DOCS_PLANS, "2026-06-10-tornado-future-async.md")
CI_WORKFLOW = os.path.join(ROOT, ".github", "workflows", "check.yml")


def rel(path):
    return os.path.relpath(path, ROOT)


def read(path):
    with open(path, "r") as handle:
        return handle.read()


failures = []

if not os.path.isfile(CANONICAL_PLAN):
    failures.append("%s is missing" % rel(CANONICAL_PLAN))
if not os.path.isfile(CONTENT_DISPATCH_PLAN):
    failures.append("%s is missing" % rel(CONTENT_DISPATCH_PLAN))
if not os.path.isfile(REPEATED_ARGS_PLAN):
    failures.append("%s is missing" % rel(REPEATED_ARGS_PLAN))
if not os.path.isfile(CI_PLAN):
    failures.append("%s is missing" % rel(CI_PLAN))
if not os.path.isfile(PACKAGE_PLAN):
    failures.append("%s is missing" % rel(PACKAGE_PLAN))
if not os.path.isfile(ASYNC_PLAN):
    failures.append("%s is missing" % rel(ASYNC_PLAN))
if not os.path.isfile(CI_WORKFLOW):
    failures.append("%s is missing" % rel(CI_WORKFLOW))

plans = sorted(glob.glob(os.path.join(DOCS_PLANS, "*.md")))
if not plans:
    failures.append("docs/plans must contain at least one completed plan")

for plan_path in plans:
    plan = read(plan_path)
    if "Status: Completed" not in plan or "make check" not in plan:
        failures.append("%s must record completed status and make check verification" % rel(plan_path))

if os.path.isfile(CI_WORKFLOW):
    workflow = read(CI_WORKFLOW)
    required_workflow_phrases = (
        "uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10",
        "uses: actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405",
        "concurrency:",
        "cancel-in-progress: true",
        "runs-on: ubuntu-24.04",
        'python-version: ["3.10", "3.12", "3.14"]',
        "python-version: ${{ matrix.python-version }}",
        "permissions:",
        "contents: read",
        "timeout-minutes: 10",
        "workflow_dispatch:",
        "python -m pip install -r requirements.txt -r requirements-dev.txt",
        "run: make check",
    )
    for phrase in required_workflow_phrases:
        if phrase not in workflow:
            failures.append("%s must contain %s" % (rel(CI_WORKFLOW), phrase))

requirements = read(os.path.join(ROOT, "requirements.txt"))
requirements_dev = read(os.path.join(ROOT, "requirements-dev.txt"))
setup_source = read(os.path.join(ROOT, "setup.py"))
for requirement in ("lxml==6.1.1", "tornado==6.5.7"):
    if requirement not in requirements:
        failures.append("requirements.txt must pin %s" % requirement)
for requirement in ("build==1.5.0", "pip-audit==2.10.0", "setuptools==82.0.1"):
    if requirement not in requirements_dev:
        failures.append("requirements-dev.txt must pin %s" % requirement)
for requirement in ("lxml>=6.1.1,<7", "tornado>=6.5.6,<7"):
    if requirement not in setup_source:
        failures.append("setup.py must bound runtime dependency %s" % requirement)
if 'python_requires=">=3.10"' not in setup_source:
    failures.append("setup.py must declare the tested Python >=3.10 baseline")

pyproject = read(os.path.join(ROOT, "pyproject.toml"))
for phrase in ('requires = ["setuptools==82.0.1"]', 'build-backend = "setuptools.build_meta"'):
    if phrase not in pyproject:
        failures.append("pyproject.toml must contain %s" % phrase)

makefile = read(os.path.join(ROOT, "Makefile"))
for phrase in (
    "ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))",
    '$(PYTHON) -m build --no-isolation --outdir "$(ROOT)/dist" "$(ROOT)"',
    '"$(ROOT)/requirements.txt"',
    '"$(ROOT)/requirements-dev.txt"',
):
    if phrase not in makefile:
        failures.append("Makefile must contain %s" % phrase)

manifest = read(os.path.join(ROOT, "MANIFEST.in"))
if "include README README.md requirements.txt requirements-dev.txt" not in manifest:
    failures.append("MANIFEST.in must include package documentation and requirement inputs")

for docs_file in ("README.md", "VISION.md", "SECURITY.md", "CHANGES.md"):
    docs_path = os.path.join(ROOT, docs_file)
    if not os.path.isfile(docs_path) or "GitHub Actions" not in read(docs_path):
        failures.append("%s must document the GitHub Actions baseline" % docs_file)

auth_source = read(os.path.join(ROOT, "splunktornado", "auth.py"))
if "self.async_callback(" in auth_source:
    failures.append("splunktornado/auth.py must not use the removed Tornado async_callback helper")
if "callback=callback" in auth_source:
    failures.append("splunktornado/auth.py must not pass the removed callback argument to AsyncHTTPClient.fetch")
if "future.add_done_callback(" not in auth_source:
    failures.append("splunktornado/auth.py must dispatch async responses through the Tornado future API")
if "XMLParser(resolve_entities=False, no_network=True)" not in auth_source:
    failures.append("splunktornado/auth.py must create XMLParser with entity resolution disabled and no network access")
if "et.fromstring(response.body)" in auth_source:
    failures.append("splunktornado/auth.py must not parse XML responses without the safe parser")
if "except:" in auth_source:
    failures.append("splunktornado/auth.py must not use bare parser exceptions")
if "except (et.XMLSyntaxError, ValueError):" not in auth_source:
    failures.append("splunktornado/auth.py must catch expected XML parser failures explicitly")
if "except ValueError:" not in auth_source:
    failures.append("splunktornado/auth.py must catch JSON decode failures explicitly")
if '"\\r" in session_key or "\\n" in session_key' not in auth_source:
    failures.append("splunktornado/auth.py must reject newline characters in session keys before building headers")
if 'raise ValueError("session_key must not contain newline characters")' not in auth_source:
    failures.append("splunktornado/auth.py must fail closed on unsafe session keys")
if "string_types = (basestring,)" not in auth_source or "string_types = (str,)" not in auth_source:
    failures.append("splunktornado/auth.py must define Python 2/3 text session-key types")
if "if not isinstance(session_key, string_types):" not in auth_source:
    failures.append("splunktornado/auth.py must reject non-text session keys before building headers")
if 'raise ValueError("session_key must be text")' not in auth_source:
    failures.append("splunktornado/auth.py must fail closed on non-text session keys")
if "def response_content_type(self, response):" not in auth_source:
    failures.append("splunktornado/auth.py must centralize response content-type normalization")
if '.split(";", 1)[0].strip().lower()' not in auth_source:
    failures.append("splunktornado/auth.py must strip content-type parameters before parser dispatch")
if 'content.find("application/json")' in auth_source or 'content.find("text/xml")' in auth_source:
    failures.append("splunktornado/auth.py must not dispatch parsers with content-type substring matches")
if 'content in ("text/xml", "application/xml")' not in auth_source:
    failures.append("splunktornado/auth.py must parse text/xml and application/xml responses")
if 'content == "application/json"' not in auth_source:
    failures.append("splunktornado/auth.py must dispatch JSON parsing by exact media type")
if 'content == "text/plain"' not in auth_source:
    failures.append("splunktornado/auth.py must dispatch text parsing by exact media type")
if "def encode_args(self, args):" not in auth_source:
    failures.append("splunktornado/auth.py must centralize request argument encoding")
if "urlencode(args, doseq=True)" not in auth_source:
    failures.append("splunktornado/auth.py must preserve repeated request arguments with doseq=True")
if "urlencode(kwargs)" in auth_source or "urlencode(post_args)" in auth_source:
    failures.append("splunktornado/auth.py must not directly encode query or post args without doseq=True")
if "self.encode_args(kwargs)" not in auth_source:
    failures.append("splunktornado/auth.py must use shared encoding for query parameters")
if "self.encode_args(post_args)" not in auth_source:
    failures.append("splunktornado/auth.py must use shared encoding for POST parameters")

if failures:
    print("Documentation plan checks failed:\n- %s" % "\n- ".join(failures), file=sys.stderr)
    sys.exit(1)

print("Documentation plan checks passed")
