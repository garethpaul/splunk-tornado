# Auth Compatibility Gate

## Problem

The Splunk mixin had no local test command. JSON responses were silently parsed
as `None` because `escape.json_decode` was referenced without importing
`escape`, and Python 3 callers failed when `urllib.urlencode` was used.

## TDD Evidence

1. Added unit tests for JSON parsing and query parameter encoding.
2. Ran `make test` before implementation changes and confirmed one JSON parse
   failure plus one Python 3 URL encoding error.
3. Imported Tornado's JSON decoder explicitly, added cross-version `urlencode`,
   and reran the full verification gate.

## Verification

- `make lint`
- `make test`
- `make build`
- `make verify`
- `git diff --check`
