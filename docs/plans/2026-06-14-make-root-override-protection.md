# Make Root Override Protection

## Status: Planned

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

## Planned Work

- Mark the Makefile root assignment as an explicit GNU Make override.
- Extend the fail-closed checker to require one protected declaration, its
  ordering, the alias graph, README indexing, and this plan's evidence.
- Keep authentication behavior, package metadata, dependencies, and workflow
  policy unchanged.

## Verification Plan

- Run focused contracts, offline tests, package builds, and full `make check`.
- Run every public alias from repository and external working directories with
  hostile environment and command-line root assignments.
- Reject declaration, ordering, alias, path, documentation, and plan mutations.
- Audit package artifacts, generated files, secrets, protected source, and the
  exact diff.
- Require all hosted Python versions on both canonical events at the exact
  implementation head.

## Scope Boundary

This change does not alter authentication, request behavior, package metadata,
dependency versions, or workflow permissions.
