# Missing Response Body Parsing

Status: Completed

## Context

`SplunkMixin.parse_response()` normalized `response.body` to `b""` for the
response-size check, but the XML, JSON, and text branches still consumed the
original `response.body`. Synthetic Tornado transport failures and streamed
responses may carry `body=None`, so supported content types could raise a
`TypeError` or return a `None` text body instead of using the existing
fail-closed parser contract.

## Objectives

- Treat missing XML and JSON bodies as empty parser input and return empty
  parse results.
- Treat a missing text body as `b""` so the callback contract remains stable.
- Keep the 1 MiB defensive body limit and exact media-type dispatch unchanged.
- Add regression and static coverage so parser branches keep using the
  normalized body value.

## Work Completed

- Added `test_parse_response_treats_missing_supported_bodies_as_empty` for
  XML, JSON, and text responses with `body=None`.
- Updated XML parsing, JSON decoding, and text response handling to use the
  normalized `body` local value.
- Extended `scripts/check_docs_plans.py` to reject direct optional-body use in
  the JSON and text parser branches and to require the new regression.
- Documented the parser fail-closed boundary in README and CHANGES.

## Verification

- The new focused regression failed before the production fix with XML and JSON
  `TypeError`s plus a `None` text body.
- The focused regression passed after the parser fix.
- `python -m py_compile setup.py splunktornado/auth.py scripts/check_docs_plans.py`
  passed.
- `python scripts/check_docs_plans.py` passed.
- `python -m unittest discover -s tests` passed with 37 tests.
- `make check` passed in the pinned Python 3.12 environment.
- External-working-directory `make check` passed in the same pinned
  environment.

## Risk

The change is limited to responses that expose a supported `Content-Type` with
`body=None`. Valid non-empty XML, JSON, and text responses keep the existing
parser behavior, and no live Splunk service or credentials were exercised.
