# Splunk Tornado Modern Dependency and CI Baseline

Status: Completed

## Context

`splunk-tornado` has Python syntax, static docs/source, unit test, package-build,
and dependency-audit checks behind `make check`. The original requirements were
unpinned, the tested Tornado release was obsolete, and no hosted workflow
protected authentication, parser, retry, request-encoding, packaging, or
supply-chain guardrails.

## Objectives

- Verify the library across the supported Python 3.10, 3.12, and 3.14 matrix.
- Keep application installs on bounded, compatible Tornado and lxml majors.
- Build both wheel and source distributions reproducibly.
- Audit the reproducible dependency set for known vulnerabilities.
- Run the complete baseline in least-privilege GitHub Actions on every push and
  pull request.

## Work Completed

- Pinned Tornado 6.5.6 and lxml 6.1.1 for reproducible verification.
- Bounded package metadata to the verified Tornado 6 and lxml 6 lines and
  declared Python 3.10 or newer.
- Pinned the PEP 517 build backend, package builder, and pip-audit tooling.
- Added wheel and source-distribution builds plus dependency auditing to
  `make check`.
- Added a ten-minute Ubuntu 24.04 GitHub Actions matrix for Python 3.10, 3.12,
  and 3.14.
- Pinned Node 24 actions by full commit SHA, restricted permissions to read-only
  contents, disabled checkout credential persistence, enabled concurrency
  cancellation, and left push and pull-request coverage unfiltered.
- Extended `scripts/check_docs_plans.py` to protect the exact workflow,
  dependency, packaging, source, and documentation contracts.
- Added a hosted external-working-directory invocation of the full Makefile
  gate on every supported Python version.

## Verification

- `make check`
- `python3 scripts/check_docs_plans.py`
- `python3 -m pip check`
- wheel installation smoke test
- source-distribution installation smoke test
- `git diff --check`

## Follow-Up Candidates

- Add live Splunk integration coverage in an isolated test environment without
  placing service credentials in repository or pull-request workflows.
