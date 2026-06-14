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
RESPONSE_SIZE_PLAN = os.path.join(DOCS_PLANS, "2026-06-12-response-body-size-limit.md")
ASYNC_REFRESH_PLAN = os.path.join(DOCS_PLANS, "2026-06-12-nonblocking-async-session-refresh.md")
TIMEOUT_VALIDATION_PLAN = os.path.join(DOCS_PLANS, "2026-06-13-positive-request-timeout-validation.md")
SESSION_KEY_WHITESPACE_PLAN = os.path.join(DOCS_PLANS, "2026-06-13-session-key-whitespace-validation.md")
ROOT_OVERRIDE_PLAN = os.path.join(DOCS_PLANS, "2026-06-14-make-root-override-protection.md")
CI_WORKFLOW = os.path.join(ROOT, ".github", "workflows", "check.yml")
WORKFLOW_DIR = os.path.dirname(CI_WORKFLOW)

EXPECTED_CI_WORKFLOW = """name: Check

on:
  push:
  pull_request:
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: check-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  check:
    runs-on: ubuntu-24.04
    timeout-minutes: 10
    strategy:
      fail-fast: false
      matrix:
        python-version: [\"3.10\", \"3.12\", \"3.14\"]
    steps:
      - name: Check out repository
        uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10 # v6.0.3
        with:
          persist-credentials: false

      - name: Set up Python
        uses: actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405 # v6.2.0
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip

      - name: Install dependencies
        run: python -m pip install -r requirements.txt -r requirements-dev.txt

      - name: Run baseline
        run: make check

      - name: Verify external working directory
        run: cd "$(mktemp -d)" && make -f "$GITHUB_WORKSPACE/Makefile" check
"""


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
if not os.path.isfile(RESPONSE_SIZE_PLAN):
    failures.append("%s is missing" % rel(RESPONSE_SIZE_PLAN))
if not os.path.isfile(ASYNC_REFRESH_PLAN):
    failures.append("%s is missing" % rel(ASYNC_REFRESH_PLAN))
if not os.path.isfile(TIMEOUT_VALIDATION_PLAN):
    failures.append("%s is missing" % rel(TIMEOUT_VALIDATION_PLAN))
if not os.path.isfile(SESSION_KEY_WHITESPACE_PLAN):
    failures.append("%s is missing" % rel(SESSION_KEY_WHITESPACE_PLAN))
if not os.path.isfile(ROOT_OVERRIDE_PLAN):
    failures.append("%s is missing" % rel(ROOT_OVERRIDE_PLAN))
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
    if workflow != EXPECTED_CI_WORKFLOW:
        failures.append("%s must match the fail-closed hosted verification contract" % rel(CI_WORKFLOW))
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
        "persist-credentials: false",
        "timeout-minutes: 10",
        "workflow_dispatch:",
        "python -m pip install -r requirements.txt -r requirements-dev.txt",
        "run: make check",
        'run: cd "$(mktemp -d)" && make -f "$GITHUB_WORKSPACE/Makefile" check',
    )
    for phrase in required_workflow_phrases:
        if phrase not in workflow:
            failures.append("%s must contain %s" % (rel(CI_WORKFLOW), phrase))

workflow_files = sorted(glob.glob(os.path.join(WORKFLOW_DIR, "*.yml")) + glob.glob(os.path.join(WORKFLOW_DIR, "*.yaml")))
if workflow_files != [CI_WORKFLOW]:
    failures.append(".github/workflows must contain only check.yml")

requirements = read(os.path.join(ROOT, "requirements.txt"))
requirements_dev = read(os.path.join(ROOT, "requirements-dev.txt"))
setup_source = read(os.path.join(ROOT, "setup.py"))
for requirement in ("lxml==6.1.1", "tornado==6.5.6"):
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
if 'version = "0.2.0"' not in setup_source:
    failures.append("setup.py must identify the breaking compatibility baseline as version 0.2.0")

package_source = read(os.path.join(ROOT, "splunktornado", "__init__.py"))
if 'version = "0.2.0"' not in package_source or "version_info = (0, 2, 0)" not in package_source:
    failures.append("splunktornado package version metadata must match version 0.2.0")

pyproject = read(os.path.join(ROOT, "pyproject.toml"))
for phrase in ('requires = ["setuptools==82.0.1"]', 'build-backend = "setuptools.build_meta"'):
    if phrase not in pyproject:
        failures.append("pyproject.toml must contain %s" % phrase)

makefile = read(os.path.join(ROOT, "Makefile"))
root_declaration = "override ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))"
if makefile.count(root_declaration) != 1:
    failures.append("Makefile must contain exactly one protected repository-root declaration")
if makefile.count("PYTHON ?= python3\n" + root_declaration) != 1:
    failures.append("Makefile must keep the Python override before the protected repository root")
for phrase in (
    ".PHONY: audit build check lint test verify",
    "build: lint",
    "verify: lint test build",
    "check: verify audit",
    '$(PYTHON) -m build --no-isolation --outdir "$(ROOT)/dist" "$(ROOT)"',
    '"$(ROOT)/requirements.txt"',
    '"$(ROOT)/requirements-dev.txt"',
):
    if phrase not in makefile:
        failures.append("Makefile must contain %s" % phrase)

if "docs/plans/2026-06-14-make-root-override-protection.md" not in read(os.path.join(ROOT, "README.md")):
    failures.append("README.md must index Make root override protection evidence")

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
if "except Exception as error:" not in auth_source or 'getattr(error, "response", None)' not in auth_source:
    failures.append("splunktornado/auth.py must preserve callback delivery for async transport failures")
if "response.error.code==401" in auth_source or "response.error.code == 401" in auth_source:
    failures.append("splunktornado/auth.py must use the HTTP response status for unauthorized retry decisions")
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
if "max_response_body_size = 1024 * 1024" not in auth_source:
    failures.append("splunktornado/auth.py must retain the 1 MiB response body policy")
if auth_source.count("max_body_size=self.max_response_body_size") != 2:
    failures.append("splunktornado/auth.py must apply the response limit to sync and async clients")
sync_request_source = auth_source.split("    def sync_request", 1)[1].split("    def async_request", 1)[0]
if "def sync_request(self, pathname, post_args=None, session_key=None, retry_on_unauthorized=True, request_timeout=20.0, **kwargs):" not in auth_source:
    failures.append("splunktornado/auth.py must expose a bounded default synchronous request timeout")
if '"request_timeout": request_timeout' not in sync_request_source:
    failures.append("splunktornado/auth.py must pass the synchronous timeout to Tornado")
if "session_key=self.session_key,\n                        request_timeout=request_timeout,\n                        retry_on_unauthorized=False" not in sync_request_source:
    failures.append("splunktornado/auth.py must preserve the synchronous timeout across unauthorized retry")
if "def _validated_request_timeout(self, request_timeout):" not in auth_source:
    failures.append("splunktornado/auth.py must centralize request timeout validation")
if "isinstance(request_timeout, bool)" not in auth_source or "isinstance(request_timeout, Real)" not in auth_source:
    failures.append("splunktornado/auth.py must reject boolean and non-real request timeouts")
if "math.isfinite(request_timeout)" not in auth_source or "request_timeout > 0" not in auth_source:
    failures.append("splunktornado/auth.py must require positive finite request timeouts")
if auth_source.count('raise ValueError("request_timeout must be a positive finite real number")') != 1:
    failures.append("splunktornado/auth.py must fail closed with the stable request timeout error")
if auth_source.count("request_timeout = self._validated_request_timeout(request_timeout)") != 2:
    failures.append("splunktornado/auth.py must validate sync and async request timeouts")
if "from tornado.simple_httpclient import SimpleAsyncHTTPClient" not in auth_source:
    failures.append("splunktornado/auth.py must use the Tornado client implementation that enforces max_body_size")
if "async_client_class=SimpleAsyncHTTPClient" not in auth_source:
    failures.append("splunktornado/auth.py must bound the synchronous client's selected implementation")
if "http = SimpleAsyncHTTPClient(" not in auth_source:
    failures.append("splunktornado/auth.py must bound asynchronous requests with SimpleAsyncHTTPClient")
if "force_instance=True" not in auth_source:
    failures.append("splunktornado/auth.py must isolate bounded async HTTP clients")
if "def _on_async_fetch_complete(self, callback, request, http, future):" not in auth_source:
    failures.append("splunktornado/auth.py must retain async client ownership through future completion")
if "finally:\n            http.close()\n        callback(response)" not in auth_source:
    failures.append("splunktornado/auth.py must close bounded async clients before callback delivery")
if "except Exception:\n            http.close()\n            raise" not in auth_source:
    failures.append("splunktornado/auth.py must close bounded async clients when fetch setup fails")
if "if len(body) > self.max_response_body_size:" not in auth_source:
    failures.append("splunktornado/auth.py must reject oversized custom responses before parsing")
if "def _request_session_key_async(self, callback):" not in auth_source:
    failures.append("splunktornado/auth.py must provide a non-blocking session-key request")
if '"/services/auth/login",\n            partial(self._on_async_session_key, callback)' not in auth_source:
    failures.append("splunktornado/auth.py must use the bounded async request path for login")
async_login_source = auth_source.split("def _request_session_key_async", 1)[1].split("def _on_async_session_key", 1)[0]
if "retry_on_unauthorized=False" not in async_login_source:
    failures.append("splunktornado/auth.py must not retry the async login request")
async_response_source = auth_source.split("def _on_async_response", 1)[1].split("def _on_async_session_refresh", 1)[0]
if "self.refresh_session_key()" in async_response_source:
    failures.append("splunktornado/auth.py must not block the event loop with synchronous session refresh")
if "self._request_session_key_async(partial(" not in async_response_source:
    failures.append("splunktornado/auth.py must refresh async 401 responses through the async login helper")
if "def _on_async_session_refresh(" not in auth_source:
    failures.append("splunktornado/auth.py must resume the original request after async login")
if "self.session_key = session_key\n        if not session_key:" not in auth_source:
    failures.append("splunktornado/auth.py must clear a stale shared key when async login fails")
if "if not session_key:\n            callback(original_response)\n            return" not in auth_source:
    failures.append("splunktornado/auth.py must return the original 401 when async login fails")
if "retry_on_unauthorized=False" not in auth_source.split("def _on_async_session_refresh", 1)[1]:
    failures.append("splunktornado/auth.py must bound the replay after async login to one attempt")
async_session_key_source = auth_source.split("def _on_async_session_key", 1)[1].split("def xml_parser", 1)[0]
if "def _session_key_from_xml(self, xml):" not in auth_source:
    failures.append("splunktornado/auth.py must centralize login session-key validation")
if auth_source.count("self._session_key_from_xml(xml) if response.error is None else None") != 2:
    failures.append("splunktornado/auth.py must validate both sync and async login responses")
if "if not session_key:\n            return None" not in async_session_key_source:
    failures.append("splunktornado/auth.py must reject missing login session keys")
if "self.request_headers(session_key=session_key)" not in async_session_key_source:
    failures.append("splunktornado/auth.py must validate login keys through the header boundary")
session_key_whitespace_guard = (
    "stripped_session_key = session_key.strip()\n"
    "        if not stripped_session_key or stripped_session_key != session_key:\n"
    "            return None\n"
    "        return session_key"
)
if session_key_whitespace_guard not in async_session_key_source:
    failures.append("splunktornado/auth.py must reject blank or trim-unstable login keys without normalizing them")
if 'return xml.findtext("sessionKey")' in auth_source:
    failures.append("splunktornado/auth.py must not return unvalidated login session keys")

test_source = read(os.path.join(ROOT, "tests", "test_auth.py"))
for test_name in (
    "test_parse_response_accepts_body_at_limit",
    "test_parse_response_rejects_oversized_supported_content_types",
    "test_async_request_preserves_streaming_callback_with_body_limit",
    "test_async_request_reports_transport_failures_to_callback",
    "test_async_request_closes_client_when_fetch_raises_synchronously",
    "test_async_request_retries_unauthorized_once",
    "test_async_request_returns_original_unauthorized_when_refresh_fails",
    "test_async_session_key_request_uses_bounded_login_without_retry",
    "test_async_session_key_request_rejects_missing_or_unsafe_keys",
    "test_request_session_key_accepts_safe_login_key",
    "test_request_session_key_rejects_missing_or_unsafe_login_keys",
    "test_request_session_key_uses_default_sync_timeout",
    "test_request_timeout_accepts_positive_finite_real_values",
    "test_requests_reject_invalid_timeouts_before_client_construction",
    "test_sync_request_preserves_positional_retry_control_and_default_timeout",
    "test_sync_request_retries_unauthorized_once",
):
    if "def %s(" % test_name not in test_source:
        failures.append("tests/test_auth.py must retain %s" % test_name)
for login_key_fixture in (
    'b"<response><sessionKey>   </sessionKey></response>"',
    'b"<response><sessionKey> fresh</sessionKey></response>"',
    'b"<response><sessionKey>fresh </sessionKey></response>"',
    'b"<response><sessionKey>\\tfresh\\t</sessionKey></response>"',
):
    if test_source.count(login_key_fixture) != 2:
        failures.append("tests/test_auth.py must cover sync and async rejection for %s" % login_key_fixture)
if "self.assertEqual([None] * 7, callback_calls)" not in test_source:
    failures.append("tests/test_auth.py must retain all async unsafe-login rejection outcomes")

for docs_file in ("README.md", "VISION.md", "SECURITY.md", "CHANGES.md"):
    if "1 MiB" not in read(os.path.join(ROOT, docs_file)):
        failures.append("%s must document the 1 MiB response limit" % docs_file)
    if "non-blocking" not in read(os.path.join(ROOT, docs_file)).lower():
        failures.append("%s must document non-blocking async session refresh" % docs_file)

for docs_file in ("README.md", "SECURITY.md", "CHANGES.md"):
    if "20-second" not in read(os.path.join(ROOT, docs_file)):
        failures.append("%s must document the synchronous request timeout" % docs_file)

for docs_file in ("README.md", "VISION.md", "SECURITY.md", "CHANGES.md"):
    if "positive finite" not in read(os.path.join(ROOT, docs_file)):
        failures.append("%s must document positive finite request timeout validation" % docs_file)
    if "session-key whitespace validation" not in read(os.path.join(ROOT, docs_file)).lower():
        failures.append("%s must document session-key whitespace validation" % docs_file)

if failures:
    print("Documentation plan checks failed:\n- %s" % "\n- ".join(failures), file=sys.stderr)
    sys.exit(1)

print("Documentation plan checks passed")
