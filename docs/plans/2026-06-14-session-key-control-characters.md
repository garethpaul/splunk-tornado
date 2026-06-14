# Session Key Control Characters

## Status: Planned

## Context

Session keys now reject non-text values, CR/LF, blanks, and surrounding
whitespace before entering the Splunk Authorization header. Interior ASCII
controls such as tab, NUL, and DEL still pass that boundary and can reach the
HTTP client from direct callers or authentication XML.

## Priority

High authentication integrity. Untrusted credential material must not carry
HTTP control characters into request headers.

## Requirements

- Reject ASCII control characters (`0x00...0x1f` and `0x7f`) in session keys.
- Preserve `None` as the unauthenticated sentinel and preserve printable opaque
  key characters exactly.
- Keep the existing text, newline, blank, and surrounding-whitespace errors.
- Reuse `request_headers()` validation for synchronous and asynchronous login
  response parsing.
- Add offline regressions, fail-closed static contracts, and maintained docs.

## Scope Boundaries

- Do not change credential transport, login endpoints, retry policy, timeout,
  response parsing, dependency versions, or supported Python versions.

## Implementation Units

1. Extend the centralized header validator with an ASCII control-character
   check after the existing newline guard.
2. Add direct-header and XML-derived session-key regressions while preserving
   valid printable keys.
3. Extend static contracts and maintained documentation with completed
   verification evidence.

## Verification

- focused header and XML session-key regressions
- repository and external-directory `make check`
- pinned package build and dependency audit gates
- hostile control-range, header, XML, documentation, suite-count, and plan
  mutations
- generated-artifact, credential-pattern, and exact-diff audits

## Risks

- Validation is offline and does not exercise a live Splunk service or proxy.
- Printable but service-invalid session key formats remain Splunk's protocol
  responsibility.
