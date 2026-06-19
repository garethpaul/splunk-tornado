# Non-blocking asynchronous session refresh

Status: Completed

## Goal

Prevent an asynchronous Splunk 401 response from running the blocking login
request on Tornado's event loop while preserving the existing session-key and
single-retry behavior.

## Requirements

- Keep `request_session_key()` and synchronous request behavior unchanged.
- Refresh an expired session key through the existing bounded asynchronous
  request path when an async request receives HTTP 401.
- Retry the original request exactly once only when login succeeds with a
  non-empty session key.
- Return the original unauthorized response without a retry when login fails,
  returns invalid XML, or has no session key.
- Preserve request arguments, POST data, streaming callback, timeout, and the
  public final response callback contract.
- Keep credentials and session keys out of logs.

## Implementation Units

### U1. Add an asynchronous login helper

Files: `splunktornado/auth.py`

Start `/services/auth/login` with `async_request`, disable unauthorized retry
for the login request, parse its XML through the existing safe parser, and
deliver only a validated session key to an internal completion callback.

### U2. Resume or fail the original request

Files: `splunktornado/auth.py`

Replace the blocking refresh call in `_on_async_response` with the async helper.
On success, set the shared key and replay the original request with
`retry_on_unauthorized=False`; on failure, deliver the original 401 response.

### U3. Cover and enforce the flow

Files: `tests/test_auth.py`, `scripts/check_docs_plans.py`, `README.md`,
`SECURITY.md`, `CHANGES.md`

Cover login request construction, successful replay, invalid XML, missing key,
login transport failure, argument preservation, and the no-blocking-refresh
contract. Record the behavior and make the checker reject a synchronous refresh
inside the async response handler.

## Scope Boundaries

- Do not change synchronous login or request behavior.
- Do not add additional retries, background queues, credential storage, or a
  new public Future/coroutine API.
- Do not change the 1 MiB response limit, parser dispatch, or timeout defaults.
- Live Splunk integration remains outside this offline compatibility pass.

## Verification

- The 27-test focused suite passed async login construction, successful replay,
  invalid or missing key rejection, transport failure fallback, argument
  preservation, and the no-blocking-refresh contract.
- `make check` passed from the repository and an external working directory in
  a clean Python 3.12 environment with all pinned requirements.
- Wheel and source builds passed, and `pip-audit` reported no known
  vulnerabilities.
- Hostile mutations restoring blocking refresh, enabling login retries,
  replaying without a valid key, or skipping key validation were rejected by
  tests and static contracts.
- `git diff --check` passed.
