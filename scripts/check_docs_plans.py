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
