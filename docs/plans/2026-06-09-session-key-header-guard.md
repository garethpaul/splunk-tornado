# Session Key Header Guard

## Status: Completed

## Context

`SplunkMixin.request_headers()` builds the Splunk `Authorization` header from
the current session key. Session keys are normally returned by Splunk, but a
defensive header boundary should still reject CR/LF characters before placing a
value into HTTP headers.

## Objectives

- Preserve existing Authorization header construction for normal session keys.
- Reject session keys that contain carriage returns or newlines.
- Add mocked unit coverage for the fail-closed header path.
- Extend static verification so the header guard remains in place.

## Work Completed

- Added CR/LF validation in `request_headers()`.
- Raised `ValueError` before constructing headers from unsafe session keys.
- Added a unit test for newline-bearing session keys.
- Extended `scripts/check_docs_plans.py` to require the header guard.
- Updated README, VISION, and CHANGES.

## Verification

- Negative: `python3 -m unittest discover -s tests` failed before the code fix
  because newline-bearing session keys were still accepted.
- `python3 -m unittest discover -s tests`
- `python3 -m py_compile setup.py splunktornado/auth.py`
- `python3 scripts/check_docs_plans.py`
- `make check`
- `make verify`
- `git diff --check`
