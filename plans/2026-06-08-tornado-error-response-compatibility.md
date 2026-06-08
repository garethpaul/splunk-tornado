# Tornado Error Response Compatibility

## Problem

`SplunkMixin.sync_request()` and `async_request()` expected Tornado to return
HTTP responses with `response.error` populated so 401 responses could refresh a
Splunk session key. Modern Tornado clients raise on non-2xx responses unless
`raise_error=False` is passed, which bypasses that retry path.

## TDD Evidence

1. Added a mocked `HTTPClient` unit test that verifies sync requests pass
   `raise_error=False`, preserve auth headers and encoded POST bodies, parse the
   returned response, and close the client.
2. Updated sync requests to build shared fetch kwargs, pass `raise_error=False`,
   and close the Tornado HTTP client in a `finally` block.
3. Updated async requests to pass `raise_error=False` so the existing
   `_on_async_response` retry logic can inspect 401 responses.

## Verification

- `make lint`
- `make test`
- `make verify`
- `git diff --check`
