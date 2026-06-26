# Supported Authentication Versions

Status: Completed

## Context

The package metadata and hosted matrix define supported Python and Tornado
versions, but the public docs do not distinguish that tested client matrix from
compatibility with live Splunk Enterprise or Splunk Cloud releases. The mixin
implements the legacy `/services/auth/login` session-key flow and does not
implement the JWT authentication-token flow available in Splunk 7.3 and newer.

## Requirements

- State the tested Python, Tornado, and lxml package baseline from checked-in
  metadata and hosted workflows.
- Describe the exact Splunk REST authentication surface implemented by source.
- Avoid claiming a live Splunk server version matrix that mocked tests do not
  execute.
- Clarify that Splunk JWT authentication tokens are outside the current API.
- Link to official Splunk REST authentication documentation.

## Scope Boundaries

- Do not change authentication, retry, request, parser, or packaging behavior.
- Do not invent minimum or maximum Splunk Enterprise or Cloud versions.
- Do not claim live-service verification.

## Work Completed

- Added a public compatibility section separating tested client dependencies
  from the source-backed Splunk session-key protocol boundary.
- Reconciled the version-documentation roadmap and indexed this plan.
- Added static documentation checks for the compatibility boundary.

## Verification Results

- Repository and external-directory `make check` passed with 37 unit tests,
  wheel and source-distribution builds, 35 Make authority cases, and a clean
  `pip-audit` result.
