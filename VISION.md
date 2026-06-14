## Splunk Tornado Vision

Splunk Tornado is a legacy Python mixin for Tornado applications that handles
Splunk service authentication, session-key refresh, and synchronous or
asynchronous Splunk API requests.

The repository is useful as a compact example of integrating Tornado request
handlers with Splunk's session-key authentication scheme.

The goal is to preserve the integration idea while making credential handling,
session state, and Python/Tornado version assumptions explicit.

The current focus is:

Priority:

- Preserve the `SplunkMixin` request and session-key flow
- Keep Splunk username, password, and host path in application settings
- Avoid logging credentials or session keys
- Reject unsafe session-key values before building Authorization headers
- Reject non-text session-key values before header formatting
- Keep unauthorized request retries bounded per request
- Avoid retrying upstream requests when session refresh fails
- Preserve repeated Splunk query and form parameters during request encoding
- Parse XML responses without resolving external entities
- Normalize response content types before parser dispatch
- Dispatch parsers by exact response media type, not substring matches
- Keep parser exception handling narrow and observable
- Keep asynchronous requests compatible with Tornado's supported future API
- Keep every request and login refresh bounded by a positive finite transport
  timeout
- Keep async session refresh non-blocking and bounded to one replay
- Validate every login-provided session key before refresh state changes
- Preserve session-key whitespace validation without normalizing credentials
- Preserve session-key header whitespace validation for every credential source
- Preserve session-key control-character validation before header construction
- Bound buffered and streamed Splunk responses to 1 MiB before parser dispatch
- Keep completed maintenance plans under `docs/plans`
- Keep GitHub Actions running package builds, tests, and audits across the
  supported Python matrix on every push and pull request before review
- Treat Python 2 and older Tornado APIs as legacy constraints

Next priorities:

- Expand mocked Tornado HTTP client and Splunk response coverage
- Return clearer errors for auth failures and retry paths
- Document supported Tornado and Splunk API versions

Contribution rules:

- One PR = one focused auth, request, parser, test, or documentation change.
- Do not commit Splunk credentials, hostnames, or session keys.
- Keep retries bounded and observable.
- Preserve repeated request parameters when encoding Splunk API calls.
- Keep `.github/workflows/check.yml` aligned with dependency installation and
  the Python verification baseline.
- Add fixtures for response parsing changes.

## Security And Responsible Use

Canonical security policy and reporting:

- [`SECURITY.md`](SECURITY.md)

Splunk services can expose operational logs and sensitive data. This mixin
should keep credentials local to settings, avoid session-key leakage, and make
all upstream request paths explicit.

## What We Will Not Merge (For Now)

- Credential or session-key logging
- Unbounded retries
- Unbounded upstream response bodies
- XML parsing that can resolve external entities or use network access
- Bare parser exception handlers that can hide unrelated failures
- Hidden proxying to arbitrary Splunk paths
- Live-service-only tests

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
