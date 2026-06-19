# Bounded Synchronous Request Timeout

## Status: Completed

## Context

`async_request` applies a 20-second Tornado request timeout and preserves custom
timeouts across its unauthorized retry. `sync_request` configures response-size
limits and closes its client, but supplies no request timeout, allowing a
blocking Splunk request or login refresh to wait indefinitely.

## Priority

Every synchronous network path must have a bounded default and retain a
caller-provided timeout across the single authentication retry.

## Requirements

- R1. Add a 20-second default timeout to `sync_request`, matching the existing
  asynchronous default.
- R2. Pass the timeout to Tornado for GET and POST requests.
- R3. Preserve a custom timeout across the one unauthorized retry.
- R4. Ensure synchronous login requests inherit the bounded default.
- R5. Preserve response-size limits, client cleanup, parser behavior, query and
  POST encoding, callback behavior, and retry count.
- R6. Add offline regression tests, static contracts, hostile mutations,
  documentation, and full `make check` verification.

## Scope Boundaries

- Do not change asynchronous request behavior or timeout defaults.
- Do not add retries, backoff, cancellation APIs, or live Splunk dependencies.
- Do not change the 1 MiB response cap, authentication fields, or package
  dependency ranges.

## Implementation Units

### Synchronous transport timeout

**Files:** `splunktornado/auth.py`

- Add a named synchronous timeout parameter, pass it to the blocking fetch,
  and preserve it during unauthorized replay.

### Regression coverage and maintenance record

**Files:** `tests/test_auth.py`, `scripts/check_docs_plans.py`, `README.md`,
`SECURITY.md`, `VISION.md`, `CHANGES.md`,
`docs/plans/2026-06-12-bounded-synchronous-request-timeout.md`

- Cover default and custom timeout forwarding plus retry preservation.
- Reject missing transport propagation or a retry that resets the timeout.

## Verification Plan

- focused synchronous request tests
- `python -m unittest discover -s tests -p 'test_auth.py' -v`
- `make check`
- focused timeout mutations
- external-working-directory `make check`
- `git diff --check`

## Work Completed

- Added a 20-second synchronous timeout after the existing positional retry
  parameter to preserve public call compatibility.
- Passed the timeout to Tornado for GET, POST, and login requests and retained
  custom values across the single unauthorized retry.
- Added offline coverage for default forwarding, custom retry propagation,
  login inheritance, and legacy positional retry control.
- Extended static contracts and maintenance documentation.

## Verification

- Two focused synchronous timeout tests passed.
- The full 31-test offline authentication suite passed.
- Five focused hostile timeout, retry, positional-order, and test-coverage
  mutations were rejected; one mutation exposed and closed an initially broad
  checker search that also matched the async block.
- `make check` passed in an isolated pinned Python 3.12 environment, including
  static contracts, 31 tests, wheel/sdist builds, package compatibility, and
  `pip-audit` with no known vulnerabilities.
- The same full gate passed from an external working directory.
- Plan-aware correctness, security, reliability, testing, maintainability, and
  API-contract review found and fixed parameter-order compatibility before
  reporting no remaining actionable findings.
- `git diff --check` passed.

## Remaining Risks

- Offline fake-client tests do not exercise a live slow Splunk endpoint or
  operating-system socket behavior.
