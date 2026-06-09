# Sync Refresh Failure Guard

## Status: Completed

## Context

`SplunkMixin` refreshes a session key after unauthorized Splunk responses.
The async path already stops and returns the original response when refresh
does not produce a replacement key. The sync path still issued a second request
with no authorization header, which adds unnecessary upstream load and makes
failed-auth behavior harder to reason about.

## Objectives

- Keep unauthorized retries bounded to one refresh attempt.
- Avoid a second sync upstream request when refresh returns no session key.
- Preserve successful sync retry behavior when refresh produces a new key.
- Cover both outcomes with mocked HTTP-client tests.

## Work Completed

- Updated `sync_request` to retry only when `refresh_session_key()` leaves a
  non-empty `session_key`.
- Added a mocked sync test for refresh failure with no second upstream request.
- Updated README, VISION, and CHANGES notes for the guardrail.

## Verification

- `python3 -m unittest discover -s tests`
- `make check`
- `make verify`
- `git diff --check`
