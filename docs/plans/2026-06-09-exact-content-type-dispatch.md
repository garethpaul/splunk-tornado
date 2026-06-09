# Exact Content-Type Dispatch

## Status: Completed

## Context

The response parser lowercased `Content-Type` values before dispatch, but still
used substring matching. That allowed near-matches such as `application/jsonp`
to enter the JSON parser, and it missed valid Splunk XML responses served as
`application/xml`.

## Objectives

- Strip `Content-Type` parameters before parser dispatch.
- Match parsers by exact normalized media type.
- Accept both `text/xml` and `application/xml` for XML responses.
- Keep invalid or unsupported media types returning empty parser results.
- Add mocked regression coverage and static checks for the dispatch boundary.

## Work Completed

- Added `response_content_type()` to normalize response media types.
- Replaced substring parser dispatch with exact media-type comparisons.
- Added test coverage for `application/xml` with parameters.
- Added test coverage that `application/jsonp` is ignored instead of parsed.
- Extended `scripts/check_docs_plans.py` to preserve exact dispatch behavior.
- Updated README, VISION, and CHANGES.

## Verification

- `python3 -m py_compile setup.py splunktornado/auth.py`
- `python3 -m unittest discover -s tests`
- `python3 scripts/check_docs_plans.py`
- `make check`
- `git diff --check`

## Follow-Up Candidates

- Return clearer application-level errors for auth failures and retry paths.
- Document supported Tornado and Splunk API versions.
