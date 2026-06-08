# Splunk Tornado Baseline

## Status: Completed

## Context

`splunk-tornado` is a legacy Python mixin for Tornado handlers that authenticates
to Splunk services, refreshes session keys, and wraps synchronous or
asynchronous Splunk API requests. The maintenance baseline should keep auth
response handling and package metadata verifiable without a live Splunk
instance.

## Objectives

- Preserve the `SplunkMixin` request URL, header, session-key, and response
  parsing behavior.
- Keep credentials caller-provided through application settings.
- Validate synchronous request kwargs, error-response preservation, and client
  cleanup through mocked tests.
- Run syntax, unit, package, and docs-plan checks through `make check`.
- Maintain completed maintenance plans under `docs/plans`.

## Work Completed

- Confirmed `make check` runs Python syntax checks, unit tests, and
  `setup.py check`.
- Added canonical `docs/plans` coverage for the current auth/request baseline.
- Added a docs-plan checker under `make lint` that requires completed plans
  with `make check` verification.
- Updated README, VISION, and CHANGES to make the baseline discoverable.

## Verification

- `python3 -m py_compile setup.py splunktornado/auth.py`
- `python3 scripts/check_docs_plans.py`
- `python3 -m unittest discover -s tests`
- `python3 setup.py check`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Add async request retry tests around 401 responses and malformed Splunk
  responses.
- Document supported Tornado and Splunk API versions.
