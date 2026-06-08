# Bounded Auth Retry

## Status: Completed

## Context

`SplunkMixin` refreshes the Splunk session key after an HTTP 401 response and
retries the failed request. The previous implementation did not bound that retry
per request, and `request_session_key()` set an unused retry flag before calling
the same request path.

## Objectives

- Preserve the existing session-key refresh behavior for a stale key.
- Retry an unauthorized request at most once after refreshing the session key.
- Avoid retry recursion when the login endpoint itself returns 401.
- Cover synchronous and asynchronous retry behavior without a live Splunk
  service.

## Work Completed

- Added `retry_on_unauthorized` control to sync and async request paths.
- Disabled retry recursion for session-key login requests and retried requests.
- Added mocked tests for sync and async one-retry behavior.
- Updated README, VISION, and CHANGES.

## Verification

- `python3 -m py_compile setup.py splunktornado/auth.py`
- `python3 -m unittest discover -s tests`
- `python3 setup.py check`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Return clearer auth failure objects for callers that need user-facing errors.
- Add fixtures for XML login failure payloads and malformed Splunk responses.
