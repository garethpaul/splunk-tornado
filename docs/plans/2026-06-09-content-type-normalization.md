# Content Type Normalization

## Status: Completed

## Context

`SplunkMixin.parse_response()` dispatches response parsing based on the
`Content-Type` header. The checks were case-sensitive, so a valid mixed-case
header such as `Application/JSON; charset=utf-8` was not decoded as JSON.

## Objectives

- Preserve existing XML, JSON, and plain-text parsing behavior.
- Normalize response content-type casing before parser dispatch.
- Add mocked regression coverage for mixed-case JSON content types with
  parameters.
- Keep live Splunk services out of the test suite.

## Work Completed

- Added a unit test for `Application/JSON; charset=utf-8`.
- Lowercased the response `Content-Type` header before matching parser types.
- Updated README, VISION, and CHANGES notes for content-type normalization.

## Verification

- `python3 -m unittest discover -s tests`
- `make check`
- `make verify`
- `git diff --check`
