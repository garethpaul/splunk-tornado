# Login Session Key Validation

## Status: Completed

## Context

Asynchronous login refresh validated the session key extracted from Splunk XML
before replay, but synchronous `request_session_key()` returned XML text
directly. A missing or CR/LF-bearing key could therefore survive synchronous
refresh and fail later when request headers were constructed.

## Objectives

- Apply one login session-key validation contract to sync and async refresh.
- Reject missing or unsafe keys before shared authentication state changes.
- Preserve successful login and bounded retry behavior.
- Add mocked and static regression coverage for both paths.

## Work Completed

- Added a shared XML session-key extractor that rejects missing values.
- Reused the Authorization header boundary to reject unsafe key text.
- Routed synchronous and asynchronous login responses through the helper.
- Added unit tests and static contracts for safe and rejected login keys.

## Verification

- `python3 -m unittest discover -s tests`
- `python3 scripts/check_docs_plans.py`
- `make check`
- `make verify`
- `git diff --check`
