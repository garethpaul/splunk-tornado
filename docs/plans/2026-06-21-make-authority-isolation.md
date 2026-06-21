# Make Authority Isolation

## Status: Completed

## Context

The verification Makefile protected `ROOT` from direct assignment but still
derived it with a whitespace-sensitive expression. Caller-selected shells,
non-executing Make modes, preload files, and additional `-f` programs could
break or replace verification before the checked-in targets completed.

## Work Completed

- Derived the repository root from the loaded Makefile with quoting that
  preserves spaces, quotes, and backticks for absolute external invocation.
- Exported the authoritative root and consumed it through the recipe
  environment so path bytes are not reparsed as shell syntax.
- Fixed the recipe shell and shell flags while retaining the supported Python
  3.10, 3.12, and 3.14 interpreter selection contract.
- Rejected non-executing and error-ignoring Make modes, caller `MAKEFLAGS`,
  preload files, overridden Makefile metadata, and visible additional files
  before recipes can be bypassed or replaced.
- Added a bounded authority harness across every public target and pinned CI
  dispatch to `/usr/bin/make`.

## Verification

- `make root-test` passed 35 target/authority cases, one literal-dollar
  checkout case, one Python-value Make-syntax rejection, two `MAKEFILE_LIST`
  rejections and three contained GNU Make startup-boundary cases. The same
  harness also passed ten mode-flag rejections.
- The repository and external-directory `make check` passed with the pinned
  dependency set and all 37 offline tests.
- Hostile root and shell assignments did not redirect repository paths or
  execute a caller-selected shell.
- Ten focused source, workflow, harness, README, and completed-plan mutations
  were rejected by the static contracts.
- Static contracts, Python and shell syntax, package artifacts, dependency
  audit, `git diff --check`, and strict object validation passed.

## Trust Boundary

GNU Make can execute caller preload and additional-file parse expressions
before a checked-in Makefile can reject them. Those startup effects are
contained in the regression harness. Trusted automation must invoke only this
repository Makefile because visible additional files are rejected before recipes.

The caller-selected Python interpreter remains an explicit trust boundary so
the supported Python version matrix and isolated local environments continue
to work. Its raw value is frozen before Make expansion and passed through the
recipe environment as one quoted executable, but callers are responsible for
selecting a trusted interpreter.

## Scope Boundary

This change does not alter Splunk authentication, request behavior, package
metadata, dependency versions, or public Python APIs.
