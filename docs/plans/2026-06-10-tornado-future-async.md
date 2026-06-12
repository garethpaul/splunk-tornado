# Tornado Future-Based Async Requests

Status: Completed

## Context

The package requires Tornado 6.5.6 or newer, but `async_request` still called
the removed `RequestHandler.async_callback` helper and passed the obsolete
`callback` keyword to `AsyncHTTPClient.fetch`. Every async request therefore
failed before the HTTP client could send it on the supported runtime.

## Changes

- Replaced `async_callback` with a bound `functools.partial` response handler.
- Consumed the future returned by `AsyncHTTPClient.fetch` through
  `add_done_callback`.
- Converted future transport exceptions back into callback-delivered
  `HTTPResponse` objects so callers cannot hang waiting for a callback.
- Preserved POST encoding, headers, streaming callbacks, timeouts, response
  parsing, and the public callback shape.
- Added no-network success, retry, and transport-failure regression tests plus
  static guards for the Tornado 6 API contract.

## Verification

- `make check`
- Tests in an isolated environment with Tornado 6.5.6
- Negative source mutation checks for both removed callback APIs
- `git diff --check`
