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
```

The setup commands above are derived from repository files. Legacy mobile, Python, or JavaScript samples may require older SDKs or package versions than a modern workstation uses by default.

## Running or Using the Project

- No single runtime entry point was identified. Start by reading the source files and manifests listed above.

## Testing and Verification

- `make check` runs Python syntax checks, unit tests, and `setup.py check`.
- GitHub Actions installs `requirements.txt` and runs `make check` through
  `.github/workflows/check.yml` on pushes, pull requests, and manual
  dispatches.
- The tests mock response objects and Tornado HTTP clients; they do not require
  a live Splunk instance.
- Auth retry tests verify that unauthorized requests retry at most once after a
  session-key refresh.
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

## Contributing

Keep changes small and tied to the project that is already present in this repository. For code changes, document the toolchain used, avoid committing generated dependency directories or local configuration, and update this README when setup or verification steps change.
