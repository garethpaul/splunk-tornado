# Splunk response body size limit

Status: Planned

## Goal

Prevent a Splunk endpoint from making the client buffer or parse an unbounded
response while preserving synchronous requests, asynchronous callbacks,
streaming callbacks, and the single unauthorized retry.

## Requirements

- Cap every Splunk HTTP response at 1 MiB before normal in-memory parsing.
- Apply the transport limit to synchronous, asynchronous, retried, and streamed
  requests without changing their public callback results for valid responses.
- Reject oversized custom or synthetic response bodies before XML, JSON, or
  text dispatch as a defense in depth.
- Preserve Tornado transport failures as callback-delivered responses and do
  not retry oversized responses as authentication failures.
- Document the limit and keep it enforced by the repository contract checker.

## Implementation Units

### U1. Bound the HTTP clients and parser

Files: `splunktornado/auth.py`

Use Tornado's client-level `max_body_size` for both blocking and non-blocking
clients. Give the mixin one named 1 MiB policy value, close per-request async
clients after their futures complete, and retain that same policy on the
single unauthorized retry. Check `response.body` length before parser dispatch
for responses created outside the bounded clients.

### U2. Cover success and rejection paths

Files: `tests/test_auth.py`

Verify the configured transport limit for sync and async clients, normal
responses at the boundary, oversized XML/JSON/text rejection, async client
cleanup, retry propagation, and unchanged streaming callback wiring.

### U3. Make the boundary durable

Files: `scripts/check_docs_plans.py`, `README.md`, `SECURITY.md`, `CHANGES.md`

Record the response limit and add static contracts that reject removal or
weakening of the policy, parser guard, client configuration, and completed
plan evidence.

## Scope Boundaries

- Do not change request timeouts, authentication semantics, response media-type
  dispatch, dependency versions, or the public callback shape.
- Do not add buffering around caller-provided streaming callbacks.
- Live Splunk credentials and service integration are outside this offline
  safety pass.

## Verification

- Focused response-limit and retry tests.
- Full `make check` from the repository and an external working directory.
- Hostile mutations removing the transport cap, parser guard, retry
  propagation, or async client cleanup must fail.
- `git diff --check`.

## Sources

- Tornado 6.5.6 HTTP client documentation: client-level `max_body_size` limits
  buffered and streamed response bodies.
- Tornado 6.5.6 release notes: `SimpleAsyncHTTPClient` applies the limit to the
  decompressed response size.
