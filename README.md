# splunk-tornado

<!-- README-OVERVIEW-IMAGE -->
![Project overview](docs/readme-overview.svg)

## Overview

`garethpaul/splunk-tornado` is a Python web API or service project. Splunk Tornado Authentication

This README is based on the checked-in source, manifests, scripts, and repository metadata on the `master` branch. The project language mix found during review was: Python (5).

## Repository Contents

- `README`
- `CHANGES.md` - maintenance history for auth compatibility checks
- `Makefile` - local verification entry points
- `docs/plans` - completed maintenance plans for the current baseline
- `plans` - historical implementation notes
- `requirements.txt` - runtime dependency notes
- `scripts` - documentation-plan validators
- `SECURITY.md` - security reporting and disclosure guidance
- `setup.py` - Python dependency or packaging metadata
- `splunktornado` - source or example code
- `VISION.md` - project direction and maintenance guardrails

Additional scan context:

- Source directories: splunktornado
- Dependency and build manifests: setup.py
- Entry points or build surfaces: none detected
- Test-looking files: tests/test_auth.py, splunktornado/test/__init__.py, splunktornado/test/noauth.py

## Getting Started

### Prerequisites

- Git
- Python 3 for local verification

### Setup

```bash
git clone https://github.com/garethpaul/splunk-tornado.git
cd splunk-tornado
python3 -m pip install -r requirements.txt
python3 -m pip install -r requirements-dev.txt
```

The development requirements pin `msgpack 1.2.1` across `pip-audit`'s
CacheControl dependency so the verification environment does not resolve the
vulnerable 1.1.2 release covered by `GHSA-6v7p-g79w-8964`.

The setup commands above are derived from repository files. Legacy mobile, Python, or JavaScript samples may require older SDKs or package versions than a modern workstation uses by default.

## Running or Using the Project

- No single runtime entry point was identified. Start by reading the source files and manifests listed above.

## Compatibility Boundary

- The tested package matrix is Python 3.10, 3.12, and 3.14 with Tornado
  6.5.7 through the supported 6.x line and lxml 6.1.1 through the supported 6.x
  line. These client-library claims are enforced by metadata, tests, builds,
  and GitHub Actions.
- The implemented Splunk authentication surface is the legacy
  `/services/auth/login` session-key exchange followed by the standard
  `Authorization: Splunk <session-key>` REST header.
- The test suite uses mocked Tornado clients and responses. No live Splunk
  Enterprise or Splunk Cloud version matrix is claimed.
- Splunk authentication tokens introduced in Splunk 7.3 use a JWT flow and are
  outside this mixin's current API. See Splunk's official
  [REST API authentication overview](https://help.splunk.com/en?resourceId=Splunk_RESTUM_RESTusing&version=splunk-9_1)
  and [token usage guidance](https://help.splunk.com/en/splunk-enterprise/administer/manage-users-and-security/9.1/authenticate-into-the-splunk-platform-with-tokens/use-authentication-tokens).

## Testing and Verification

- `make check` runs Python syntax checks, unit tests, a PEP 517 wheel/sdist
  build, and dependency auditing.
- `make root-test` exercises repository-root, shell, Make metadata, and
  non-executing-mode authority without network access.
- The `PYTHON` override remains an intentional trusted-input boundary for the
  supported Python 3.10, 3.12, and 3.14 verification matrix.
- GitHub Actions installs pinned runtime and development requirements and runs
  `make check` on fixed Ubuntu 24.04 runners across Python 3.10, 3.12, and
  3.14 for every push and pull request, with pinned Node 24 actions, read-only
  permissions, credential-free checkout, and timeouts.
- Each hosted matrix job also reruns `make check` from a temporary directory to
  enforce path-independent Makefile behavior.
- `make check` audits the pinned Tornado 6 and lxml 6 runtime baseline plus the
  patched `msgpack 1.2.1` verification dependency for known vulnerabilities
  after the offline unit and packaging checks.
- The tests mock response objects and Tornado HTTP clients; they do not require
  a live Splunk instance.
- Auth retry tests verify that unauthorized requests retry at most once after a
  session-key refresh.
- Async 401 handling refreshes the session key through the bounded non-blocking
  login request, then replays the original request once only after receiving a
  safe non-empty key. Failed refreshes return the original unauthorized
  response.
- Streamed 401 responses are terminal because Tornado delivers chunks before
  the final response callback; replaying would mix unauthorized and successful
  response bytes in the caller's stream.
- Sync and async login responses share one validator that rejects missing or
  CR/LF-bearing session keys before storing or replaying them.
- Session-key whitespace validation also rejects blank or surrounding-whitespace
  login values without silently modifying the server-provided credential.
- Session-key header whitespace validation applies the same non-normalizing
  boundary to caller-provided Authorization credentials; only `None` omits it.
- Session-key control-character validation rejects ASCII controls from direct
  and login-provided credentials before they can enter Authorization headers.
- Async requests use Tornado 6's future-returning HTTP client API while keeping
  the mixin's existing response callback contract, including transport errors.
- Sync, async, retried, and streamed Splunk responses are capped at 1 MiB by
  Tornado's `SimpleAsyncHTTPClient` before parsing; custom response objects
  receive the same defensive parser check. The bounded mixin does not use a
  globally configured curl client because Tornado's curl implementation has no
  equivalent `max_body_size` constructor policy.
- Synchronous requests and login use a 20-second default transport timeout;
  caller-provided positive finite timeouts are preserved across the single
  unauthorized retry, while disabled or malformed timeout values fail locally.
- Version 0.2.0 is the first package baseline requiring Python 3.10+, Tornado
  6.5.7+, and lxml 6.1.1+. Tornado 6.5.7 is the minimum patched release for
  `GHSA-pw6j-qg29-8w7f`.
- Request encoding tests verify that repeated query and POST parameters remain
  repeated fields instead of collapsing into a Python list string.
- Header tests verify that session keys containing carriage returns or newlines
  are rejected before Authorization headers are built.
- Header tests also verify that non-text session key values are rejected before
  Authorization headers are built.
- Sync and async retry paths do not issue a second upstream request when the
  session refresh fails to produce a key.
- XML response parsing disables entity resolution and network access before
  handing Splunk responses to `lxml`.
- Response parsing normalizes `Content-Type` casing before choosing XML, JSON,
  or text decoding.
- Response parsing strips `Content-Type` parameters and dispatches only on exact
  media types, including `application/xml`.
- Parser error handling catches expected XML and JSON decode failures without
  swallowing unrelated exceptions.
- Supported XML, JSON, and text responses with missing bodies use the parser's
  normalized empty body path instead of raising or returning `None`.
- `make check` also requires completed canonical plans under `docs/plans`.

When the required SDK or runtime is unavailable, use static checks and source review first, then verify on a machine that has the matching platform toolchain.

## Configuration and Secrets

- No required secret or credential file was identified in the repository scan. If you add integrations later, keep secrets out of git.

## Security and Privacy Notes

- Review changes touching authentication or token handling; examples from the scan include splunktornado/__init__.py, splunktornado/auth.py.
- Review changes touching network requests, sockets, or service endpoints; examples from the scan include setup.py, splunktornado/__init__.py, splunktornado/auth.py, splunktornado/test/noauth.py.
- Review changes touching file, media, JSON, XML, CSV, OCR, or data parsing; examples from the scan include splunktornado/auth.py.

## Maintenance Notes

- See `SECURITY.md` for vulnerability reporting and safe research guidance.
- See `VISION.md` for project direction and contribution guardrails.
- See `docs/plans/2026-06-08-splunk-tornado-baseline.md` for the canonical
  auth and request compatibility baseline.
- See `docs/plans/2026-06-08-bounded-auth-retry.md` for the bounded
  unauthorized retry guard.
- See `docs/plans/2026-06-08-sync-refresh-failure.md` for the sync retry
  refresh-failure guard.
- See `docs/plans/2026-06-09-safe-xml-parser.md` for the XML parser hardening
  guard.
- See `docs/plans/2026-06-09-content-type-normalization.md` for response
  content-type normalization coverage.
- See `docs/plans/2026-06-09-narrow-parser-exceptions.md` for parser exception
  handling coverage.
- See `docs/plans/2026-06-09-session-key-header-guard.md` for the session-key
  Authorization header boundary.
- See `docs/plans/2026-06-09-text-session-key-guard.md` for the non-text
  session-key header guard.
- See `docs/plans/2026-06-09-exact-content-type-dispatch.md` for exact media
  type parser dispatch coverage.
- See `docs/plans/2026-06-09-repeated-parameter-encoding.md` for repeated
  request parameter encoding coverage.
- See `docs/plans/2026-06-10-ci-baseline.md` for the GitHub Actions baseline.
- See `docs/plans/2026-06-10-tornado-future-async.md` for the Tornado 6 async
  request compatibility fix.
- See `docs/plans/2026-06-12-response-body-size-limit.md` for the 1 MiB
  transport and parser response boundary.
- See `docs/plans/2026-06-12-nonblocking-async-session-refresh.md` for the
  non-blocking async 401 refresh and replay contract.
- See `docs/plans/2026-06-13-session-key-whitespace-validation.md` for the
  shared login credential whitespace boundary.
- See `docs/plans/2026-06-14-make-root-override-protection.md` for authoritative
  repository-root selection across all Make aliases.
- See `docs/plans/2026-06-21-make-authority-isolation.md` for quoted checkout
  paths, fixed shell authority, Make mode rejection, and startup boundaries.
- See `docs/plans/2026-06-26-supported-auth-versions.md` for the tested client
  matrix and source-backed Splunk authentication boundary.
- See `docs/plans/2026-06-14-session-key-header-whitespace.md` for the shared
  caller and login Authorization credential boundary.
- See `docs/plans/2026-06-19-missing-response-body-parsing.md` for supported
  response parser behavior when Tornado or synthetic responses expose no body.
- See `docs/plans/2026-06-20-msgpack-1-2-1-advisory-remediation.md` for the
  patched verification-tool dependency boundary.

## Contributing

Keep changes small and tied to the project that is already present in this repository. For code changes, document the toolchain used, avoid committing generated dependency directories or local configuration, and update this README when setup or verification steps change.
