# Narrow Parser Exceptions

## Status: Completed

## Context

`SplunkMixin.parse_response()` intentionally returns empty parse results when
Splunk sends invalid XML or JSON. The implementation used bare `except:` blocks
for those parser failures, which can also hide unrelated control-flow or runtime
exceptions while handling operational responses.

## Objectives

- Preserve empty parse results for invalid XML and JSON payloads.
- Catch expected XML parser and JSON decode failures explicitly.
- Add unit and static coverage so bare parser exceptions do not return.

## Work Completed

- Replaced the XML bare exception with explicit `XMLSyntaxError` and
  `ValueError` handling.
- Replaced the JSON bare exception with explicit `ValueError` handling.
- Added invalid XML and invalid JSON unit coverage for the existing empty
  parse-result behavior.
- Extended `scripts/check_docs_plans.py` to reject bare parser exceptions and
  require the explicit parser failure handlers.
- Documented the parser-exception guard in README, VISION, and CHANGES.

## Verification

- `python3 -m py_compile setup.py splunktornado/auth.py`
- `python3 scripts/check_docs_plans.py`
- `python3 -m unittest discover -s tests`
- `make check`
- `make verify`
- `git diff --check`
