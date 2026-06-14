# Session Key Header Whitespace

## Status: Planned

## Context

Login responses reject blank and trim-unstable session keys, but callers can
still pass the same values directly to `request_headers()`. Whitespace-only,
leading-space, trailing-space, and tab-surrounded keys can therefore reach the
Splunk Authorization header.

## Priority

High authentication boundary. Every session key source should pass through one
non-normalizing header validator before credential material enters a request.

## Requirements

- Preserve `None` as the explicit unauthenticated-header sentinel.
- Reject non-text, empty, whitespace-only, surrounding-whitespace, CR, and LF
  session key values before constructing Authorization headers.
- Preserve exact interior characters for valid opaque keys.
- Reuse the header validator for synchronous and asynchronous login responses.
- Add offline regressions, fail-closed static contracts, and maintained docs.

## Verification

- focused and complete offline unit tests
- repository and external-directory pinned `make check`
- hostile sentinel, type, blank, trim, newline, shared-helper, documentation,
  suite-count, and plan-status mutations
- wheel/sdist metadata and installation smoke tests
- generated-artifact, credential-pattern, and exact-diff audits
