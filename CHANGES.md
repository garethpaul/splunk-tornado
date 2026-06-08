# Changes

## 2026-06-08

- Added a Makefile verification gate for Python syntax checks, unit tests, and
  package metadata checks.
- Added tests for Splunk JSON response parsing and query parameter encoding.
- Fixed JSON parsing by importing Tornado's `escape` module explicitly.
- Made request URL/body encoding work on both Python 2 and Python 3 runtimes.
- Added runtime dependency metadata for Tornado and lxml.
