# Make Root Override Protection

## Status: Completed

## Context

The Makefile derives repository paths from its own location, but environment
and command-line assignments can replace `ROOT`. A hostile or stale value can
redirect compilation, tests, package builds, and dependency audits away from
the checked-out source while still invoking this repository's Makefile.

## Priority

Verification paths are a trust boundary. The repository must authoritatively
select its own root while preserving the intentional `PYTHON` tool override.

## Objectives

- Protect the repository-derived root from environment and command-line
  assignments.
- Preserve declaration order, the Python override, and all public aliases.
- Exercise lint, test, build, verify, audit, and check from repository and
  external working directories under hostile root values.
- Add mutation-sensitive source, documentation, and completed-plan contracts.
- Retain the pinned package, vulnerability audit, and hosted Python matrix.

## Work Completed

- Marked the Makefile root assignment as an explicit GNU Make override.
- Extended the fail-closed checker to require one protected declaration, its
  ordering, the alias graph, README indexing, and this plan's evidence.
- Kept authentication behavior, package metadata, dependencies, and workflow
  policy unchanged.

## Verification

- The pinned Python 3.12 `make check` passed documentation contracts, all 33
  offline tests, wheel and source-distribution builds, and pip-audit with no
  known vulnerabilities; the isolated environment also passed `pip check`.
- All six public Make aliases passed from both repository and external working
  directories with hostile environment and command-line `ROOT` assignments,
  for 24 bounded precedence cases.
- The explicit `PYTHON` override remained effective across compilation, tests,
  package builds, and the dependency audit.
- Seven declaration, duplicate, placement, alias, path, README, and plan
  mutations were rejected for the intended reason.
- Built wheel and source distributions contained the expected metadata,
  package sources, documentation, and offline tests.
- Exact diff, protected-source, generated-artifact, high-confidence secret, and
  `git diff --check` audits passed. Only explicitly named validation-created
  build, distribution, and bytecode paths were removed; the pre-existing
  ignored egg-info directory was preserved.

All hosted Python versions remain required on both canonical events at the
exact implementation head.

## Scope Boundary

This change does not alter authentication, request behavior, package metadata,
dependency versions, or workflow permissions.
