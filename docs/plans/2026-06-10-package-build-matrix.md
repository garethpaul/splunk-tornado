# Package Build Matrix

Status: Completed

## Context

The baseline ran tests and dependency auditing on one moving Linux runner, but
it used the deprecated `setup.py check` command instead of building the package.
Make targets also failed when invoked outside the repository.

## Changes

- Added a pinned setuptools PEP 517 backend and `build` frontend.
- Replaced `setup.py check` with real wheel and source-distribution builds.
- Declared Python 3.10 or newer in package metadata.
- Expanded CI to Python 3.10, 3.12, and 3.14 on fixed Ubuntu 24.04 runners.
- Added concurrency cancellation and exact action-version comments.
- Anchored Makefile paths to the repository root.
- Added the long-description and requirement files to the source distribution
  after a clean wheel-from-sdist build exposed the missing README metadata.

## Verification

- `make check`
- `make -f /path/to/splunk-tornado/Makefile check` from outside the repository
- wheel and source-distribution content inspection
- negative workflow mutation checks
- `git diff --check`
- GitHub Actions matrix
