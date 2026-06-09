# Repeated Parameter Encoding

## Status: Completed

## Context

`SplunkMixin.request_url()` and request POST bodies encoded dictionaries with
plain `urlencode()`. List-valued Splunk parameters were serialized as one Python
list string instead of repeated query or form fields, which breaks APIs that
accept multiple values for the same argument.

## Objectives

- Preserve existing scalar query and POST parameter encoding.
- Encode list-valued request arguments as repeated fields.
- Share the encoding behavior across query strings, synchronous POST bodies,
  and asynchronous POST bodies.
- Add regression coverage and static checks so direct non-`doseq` encoding does
  not return.

## Work Completed

- Added `encode_args()` as the shared request argument encoder.
- Switched query strings and sync/async POST bodies to use the shared encoder.
- Added unit coverage for repeated query parameters.
- Added unit coverage for repeated synchronous POST parameters.
- Extended `scripts/check_docs_plans.py` to preserve repeated-argument
  encoding.
- Updated README, VISION, and CHANGES.

## Verification

- Negative: `make test` failed before the code fix because repeated parameters
  were encoded as a single list string.
- `python3 -m unittest discover -s tests`
- `python3 -m py_compile setup.py splunktornado/auth.py`
- `python3 scripts/check_docs_plans.py`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Add direct async HTTP client argument coverage if the test harness expands.
- Document supported Splunk request parameters that rely on repeated fields.
