# Splunk Tornado CI Baseline

## Status: Completed

## Context

`splunk-tornado` has Python syntax, static docs/source, unit test, and packaging
checks behind `make check`. The repository needs those checks to run in GitHub
Actions so auth, parser, retry, and request-encoding guardrails are checked
before review.

## Objectives

- Run the existing `make check` wrapper in GitHub Actions.
- Install checked-in Python dependencies from `requirements.txt`.
- Make the workflow presence part of the Python verification contract.

## Work Completed

- Added `.github/workflows/check.yml` to install dependencies and run
  `make check` on pushes, pull requests, and manual dispatches.
- Set up Python 3.12 in CI.
- Extended `scripts/check_docs_plans.py` to require the CI workflow and this
  completed plan.
- Updated README, VISION, SECURITY, and CHANGES with the CI baseline.

## Verification

- `make check`
- `python3 scripts/check_docs_plans.py`
- `git diff --check`

## Follow-Up Candidates

- Add a small compatibility matrix if the legacy Tornado APIs need to remain
  validated on older Python versions.
