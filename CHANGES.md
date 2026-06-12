# Changes

## 2026-06-10

- Added a GitHub Actions check workflow that installs checked-in requirements
  and runs the existing Python `make check` baseline on pushes, pull requests,
  and manual dispatches.
- Added a docs/source guard requiring the CI workflow and completed CI baseline
  plan to remain checked in.

## 2026-06-09

- Rejected non-text session-key values before constructing Splunk Authorization
  headers, with regression and static coverage.
- Preserved repeated Splunk query and POST parameters by centralizing request
  argument encoding with `doseq=True`, with regression coverage.
- Switched response parser dispatch to exact normalized media types, including
  `application/xml`, and added coverage for near-match content types.
- Rejected CR/LF-bearing session keys before constructing Splunk Authorization
  headers, with mocked regression coverage.
- Narrowed XML and JSON parser exception handling and added regression coverage
  for invalid parser payloads.
- Normalized Splunk response `Content-Type` casing before parser dispatch and
  added regression coverage for mixed-case JSON headers with parameters.
- Added a no-network, no-entity-resolution XML parser for Splunk XML responses.
- Added mocked and entity-response coverage plus a static source guard for safe
  XML parsing under `make check`.

## 2026-06-08

- Stopped sync requests from retrying 401 responses when session refresh fails
  to produce a replacement key, with mocked coverage.
- Bounded unauthorized Splunk request retries to one session-key refresh and
  added mocked sync/async coverage.
- Added `make check` as the shared repository verification alias.
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
- Added canonical `docs/plans` coverage and a docs-plan checker under
  `make check`.
