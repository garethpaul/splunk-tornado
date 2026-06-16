# Tornado 6.5.7 Advisory Remediation

## Status: In Progress

## Context

The pinned package gate now fails because GitHub advisory
`GHSA-pw6j-qg29-8w7f`, published June 15, 2026, affects Tornado versions through
6.5.6. Reused `CurlAsyncHTTPClient` handles can retain per-request credentials.
Tornado 6.5.7 is the first patched release and is available from PyPI.

Although this package deliberately selects `SimpleAsyncHTTPClient` for its
bounded response policy, its declared runtime range still permits downstream
users to install the vulnerable version and use other Tornado clients in the
same process. The maintained floor and reproducible validation pin must move
together.

## Requirements

- Pin offline validation to Tornado 6.5.7.
- Raise the package runtime floor to `tornado>=6.5.7,<7`.
- Keep Python 3.10+, lxml, build, audit, response-limit, timeout, retry,
  credential-validation, and packaging behavior unchanged.
- Synchronize maintained README, security, changelog, and static contracts.
- Require `pip-audit` to report no known vulnerabilities for both repository
  and external-directory gates.
- Add mutation-sensitive contracts for the exact pin, runtime floor,
  documentation, advisory identity, and completed plan evidence.

## Scope Boundaries

- Do not redesign HTTP client selection, proxies, retries, session refresh,
  response parsing, callbacks, or public APIs.
- Do not change the Python, lxml, setuptools, build, or pip-audit versions.
- Do not exercise live Splunk credentials, services, TLS, proxies, or network
  timing.

## Verification Plan

- Preserve the pre-change `pip-audit` failure for Tornado 6.5.6 and
  `GHSA-pw6j-qg29-8w7f`.
- Install the updated pins in an isolated Python 3.12 environment.
- Run focused tests, then repository and external-directory `make check`.
- Inspect wheel and source-distribution metadata for the 6.5.7 runtime floor.
- Reject focused pin, floor, advisory, documentation, and plan-status
  mutations.
- Run exact diff, generated-artifact, credential-pattern, and clean-worktree
  audits before shipping.

## Verification Results

- Pending implementation and validation.

## Risks

- No live Splunk service or curl-backed proxy integration is exercised.
- Compatible future Tornado 6.x releases remain allowed by package metadata;
  CI and the pinned audit gate continue to verify the reviewed lower bound.
