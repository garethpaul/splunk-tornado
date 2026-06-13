# Session Key Whitespace Validation

## Status: Planned

## Context

The shared login parser rejects missing session keys and values containing CR or
LF before synchronous or asynchronous authentication state changes. It still
accepts whitespace-only text and values with leading or trailing spaces or
tabs, producing unusable or ambiguous `Authorization` header values.

## Priority

Splunk session keys are opaque credentials and should be preserved exactly, not
silently normalized. A login key is valid only when it is nonblank and already
equal to its stripped form before the existing header safety check runs.

## Objectives

- Reject whitespace-only login session keys.
- Reject leading or trailing whitespace without modifying the server value.
- Preserve exact interior characters for valid keys and retain CR/LF rejection.
- Apply the boundary through the shared extraction helper used by synchronous
  and asynchronous login flows.
- Add offline regression, fail-closed static, and documentation coverage.

## Implementation Units

### U1. Validate login key whitespace

**Files:** `splunktornado/auth.py`, `tests/test_auth.py`

Require `session_key.strip()` to be nonempty and equal to the original parsed
text before passing the key through `request_headers` and returning it.

### U2. Preserve the shared contract

**Files:** `scripts/check_docs_plans.py`, `README.md`, `VISION.md`,
`SECURITY.md`, `CHANGES.md`

Require the trim-stability guard, shared helper use, synchronous and
asynchronous regressions, completed plan evidence, and a common session-key
whitespace validation phrase.

## Verification

- Focused and complete offline unit tests.
- Full pinned `make check` locally and from an external working directory,
  including wheel/sdist build, installation smoke tests, compatibility checks,
  and vulnerability audit.
- Focused hostile mutations plus Python compilation, package artifact, secret,
  generated-file, and `git diff --check` audits.

## Scope Boundary

This change does not rotate credentials, change Authorization header syntax,
alter retry counts, normalize valid keys, or claim live Splunk compatibility.
