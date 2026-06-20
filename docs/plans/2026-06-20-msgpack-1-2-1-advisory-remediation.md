# msgpack 1.2.1 Advisory Remediation

Status: Completed

## Context

The exact Python 3.12 verification environment resolved `msgpack 1.1.2`
through `pip-audit` and CacheControl. A fresh dependency audit reported
`GHSA-6v7p-g79w-8964` and identified `msgpack 1.2.1` as the fixed release.

## Work Completed

- Added an exact `msgpack 1.2.1` development requirement.
- Extended the canonical documentation checker so removing or changing the pin
  fails the shared gate.
- Documented the transitive verification-tool boundary in the README, security
  guidance, and change history.

## Verification

- Installed the exact runtime and development requirements in a fresh Python
  3.12 virtual environment.
- The repository and external-directory `make check` passed.
- pip-audit reported no known vulnerabilities.
- Six hostile pin, downgrade, plan, index, advisory, and status mutations were
  rejected by the canonical checker.
- The offline authentication suite, package build, documentation checker, and
  generated-artifact and credential-pattern audits passed.

## Risks

- The audit resolves the current public package index and can report newly
  published advisories independently of repository changes.
- No live Splunk service, credentials, proxy, TLS, or network timing were used.
