# Changes

## 2026-06-08

- Made Tornado sync and async Splunk requests pass `raise_error=False` so 401
  responses reach the session refresh/retry path.
- Closed synchronous Tornado HTTP clients after each request and added mocked
  coverage for request kwargs, auth headers, response parsing, and client close.
- Added a Makefile verification gate for Python syntax checks, unit tests, and
  package metadata checks.
- Added tests for Splunk JSON response parsing and query parameter encoding.
- Fixed JSON parsing by importing Tornado's `escape` module explicitly.
- Made request URL/body encoding work on both Python 2 and Python 3 runtimes.
- Added runtime dependency metadata for Tornado and lxml.
