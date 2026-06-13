# Positive Request Timeout Validation

## Status: Planned

## Context

The synchronous and asynchronous Splunk request helpers now default to a
20-second request timeout and preserve a custom timeout across the single
unauthorized retry. Tornado documents `request_timeout=0` as disabling the
timeout, while the current public methods forward caller values without
validation. Zero, negative, non-finite, boolean, or non-real inputs can
therefore defeat or corrupt the bounded-request contract before transport.

Official Tornado reference:
https://www.tornadoweb.org/en/stable/httpclient.html

## Priority

Fail closed before constructing a client or mutating authentication state when
a caller supplies a timeout that cannot represent a positive finite duration.

## Requirements

- R1. Accept positive finite real request timeouts, including integer and
  floating-point values.
- R2. Reject zero, negative, non-finite, boolean, `None`, and non-real
  timeout values with a stable `ValueError` before any network request starts.
- R3. Apply the same validation contract to synchronous and asynchronous
  requests without changing the public parameter order or default.
- R4. Preserve the validated timeout across the one unauthorized retry and the
  asynchronous login refresh path.
- R5. Preserve response-size limits, client cleanup, parsing, callbacks,
  request encoding, authentication state, and retry count.
- R6. Add offline regression tests, static contracts, focused hostile
  mutations, maintenance documentation, and full `make check` verification.

## Scope Boundaries

- Do not change the 20-second default or add a separate connect timeout.
- Do not impose a maximum caller timeout in this unit.
- Do not add retries, backoff, cancellation APIs, or live Splunk dependencies.
- Do not change the 1 MiB response cap, dependency ranges, or package version.

## Implementation Units

### Shared timeout validation

**Files:** `splunktornado/auth.py`

- Add one internal validator for positive finite numeric durations.
- Validate before synchronous client construction and asynchronous request
  construction, then forward the validated value through existing retries.

### Regression and contract coverage

**Files:** `tests/test_auth.py`, `scripts/check_docs_plans.py`, `README.md`,
`SECURITY.md`, `VISION.md`, `CHANGES.md`,
`docs/plans/2026-06-13-positive-request-timeout-validation.md`

- Cover accepted integer and floating-point values on both request paths.
- Cover rejected disabled, malformed, and non-finite values before transport.
- Enforce shared validation, public signature compatibility, retry forwarding,
  completed plan evidence, and user-facing maintenance notes.

## Verification Plan

- focused timeout validation tests
- `python -m unittest discover -s tests -p 'test_auth.py' -v`
- `python scripts/check_docs_plans.py`
- `make check`
- focused timeout-validation mutations
- external-working-directory `make check`
- staged-path, generated-artifact, secret-pattern, and `git diff --check` audits

## Assumptions

- Existing callers that deliberately pass zero to disable timeouts conflict
  with the repository's documented bounded-request security contract and should
  receive an explicit local error instead.
- Positive finite real values remain API-compatible with Tornado's request
  timeout input and require no transport-layer conversion.
