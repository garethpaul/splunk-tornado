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
- Treat Python 2 and older Tornado APIs as legacy constraints

Next priorities:

- Add tests with mocked Tornado HTTP clients and Splunk responses
- Import and validate JSON parsing dependencies explicitly
- Return clearer errors for auth failures and retry paths
- Document supported Tornado and Splunk API versions

Contribution rules:

- One PR = one focused auth, request, parser, test, or documentation change.
- Do not commit Splunk credentials, hostnames, or session keys.
- Keep retries bounded and observable.
- Add fixtures for response parsing changes.

## Security And Responsible Use

Splunk services can expose operational logs and sensitive data. This mixin
should keep credentials local to settings, avoid session-key leakage, and make
all upstream request paths explicit.

## What We Will Not Merge (For Now)

- Credential or session-key logging
- Unbounded retries
- Hidden proxying to arbitrary Splunk paths
- Live-service-only tests
