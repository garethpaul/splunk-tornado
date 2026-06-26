# Streaming Authentication Retry Boundary

## Status: Completed

## Goal

Prevent an async streamed 401 body from being combined with bytes from an
authenticated replay while preserving the existing bounded retry for buffered
requests.

## Evidence

Tornado documents that `streaming_callback` runs for each chunk as it arrives
and that the final `HTTPResponse.body` is empty. The response status is handled
by this mixin only after those chunks may have reached the caller:
https://www.tornadoweb.org/en/stable/httpclient.html

## Design

1. Keep the existing non-blocking session refresh and one replay for buffered
   async requests.
2. Treat a 401 as terminal when `streaming_callback` is present because emitted
   bytes cannot be recalled or separated from a replay by the current API.
3. Preserve the normal response callback so callers can inspect the terminal
   unauthorized response.
4. Enforce the distinction with focused behavior and source contracts.

## Verification

- Run focused buffered and streamed unauthorized-response tests.
- Run repository and external-directory `make check` across the supported
  Python matrix.
- Require hosted Check and CodeQL on the exact pull-request head.

## Verification Results

- Focused buffered and streamed unauthorized-response tests passed.
- All 38 tests, package builds, dependency audits, and Make authority checks
  passed from repository and external working directories under Python 3.10.20,
  3.12.3, and 3.14.6. Python 3.10 used the clean official container because the
  uv-managed interpreter lacks `ensurepip` for pip-audit's nested environment.
- Two hostile mutations restoring unconditional streamed retry or removing the
  focused regression were rejected by the documentation/source contract gate.
- No live Splunk Enterprise or Splunk Cloud service was exercised.

## Non-Goals

- Buffering streamed bodies until authentication succeeds.
- Changing synchronous retries or non-streaming async retries.
- Adding a new callback API that separates attempts.
