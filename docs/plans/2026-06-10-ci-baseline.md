# Splunk Tornado Modern Dependency and CI Baseline

## Status: Completed

## Context

`splunk-tornado` has Python syntax, static docs/source, unit test, and packaging
checks behind `make check`. Its requirements were unpinned, the tested local
Tornado release was obsolete, and no hosted workflow enforced authentication,
parser, retry, request-encoding, or dependency-security guardrails.

## Objectives

- Verify the library on Python 3.12 with current Tornado and lxml releases.
- Keep application installs on bounded compatible major versions.
- Audit the reproducible CI dependency set for known vulnerabilities.
- Run the complete baseline in least-privilege GitHub Actions.

## Work Completed

- Pinned Tornado 6.5.6 and lxml 6.1.1 for reproducible verification.
- Bounded package metadata to the verified Tornado 6 and lxml 6 lines.
- Pinned setuptools and pip-audit development tools and added auditing to
  `make check`.
- Added a five-minute GitHub Actions job with read-only contents permission and
  immutable Node 24 action references.
- Extended `scripts/check_docs_plans.py` to protect dependency, workflow, and
  documentation contracts.

## Verification

- `make check`
- `python3 scripts/check_docs_plans.py`
- `python3 -m pip check`
- `git diff --check`

## Follow-Up Candidates

- Replace the legacy `setup.py check` packaging path with a modern build
  backend after defining package release compatibility requirements.
