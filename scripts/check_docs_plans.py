#!/usr/bin/env python
from __future__ import print_function

import glob
import os
import sys


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOCS_PLANS = os.path.join(ROOT, "docs", "plans")
CANONICAL_PLAN = os.path.join(DOCS_PLANS, "2026-06-08-splunk-tornado-baseline.md")


def rel(path):
    return os.path.relpath(path, ROOT)


def read(path):
    with open(path, "r") as handle:
        return handle.read()


failures = []

if not os.path.isfile(CANONICAL_PLAN):
    failures.append("%s is missing" % rel(CANONICAL_PLAN))

plans = sorted(glob.glob(os.path.join(DOCS_PLANS, "*.md")))
if not plans:
    failures.append("docs/plans must contain at least one completed plan")

for plan_path in plans:
    plan = read(plan_path)
    if "Status: Completed" not in plan or "make check" not in plan:
        failures.append("%s must record completed status and make check verification" % rel(plan_path))

auth_source = read(os.path.join(ROOT, "splunktornado", "auth.py"))
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

if failures:
    print("Documentation plan checks failed:\n- %s" % "\n- ".join(failures), file=sys.stderr)
    sys.exit(1)

print("Documentation plan checks passed")
