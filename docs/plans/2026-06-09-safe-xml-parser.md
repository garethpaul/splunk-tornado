# Safe XML Response Parser

## Status: Completed

## Context

`splunk-tornado` parses Splunk XML responses with `lxml.etree.fromstring`.
Because Splunk responses can include operational data, XML parsing should avoid
external entity resolution and network access even when responses are mocked or
proxied through internal services.

## Objectives

- Preserve XML response parsing for Splunk APIs.
- Disable external entity resolution and network access in the lxml parser.
- Add unit and static coverage to the existing `make check` gate.

## Work Completed

- Added `SplunkMixin.xml_parser()` using `XMLParser(resolve_entities=False,
  no_network=True)`.
- Passed the safe parser to `et.fromstring` in `parse_response`.
- Added mocked parser-call coverage and an external-entity response test.
- Extended `scripts/check_docs_plans.py` to reject unsafe XML parser drift.
- Documented the XML parser guard in README, VISION, and CHANGES.

## Verification

- `python3 -m py_compile setup.py splunktornado/auth.py`
- `python3 scripts/check_docs_plans.py`
- `python3 -m unittest discover -s tests`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Narrow broad parser exceptions to XML, JSON, and decode-specific failures.
- Add explicit content-type normalization for Splunk responses with charset
  parameters.
