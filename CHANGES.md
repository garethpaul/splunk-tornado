# Changes

## 2026-06-26 10:19 PDT - P1 - Do not replay streamed unauthorized responses

### Summary

Prevented async 401 refresh/retry when a streaming callback may already have
received unauthorized response bytes, while preserving one bounded replay for
buffered requests.

### Files changed

- `splunktornado/auth.py` — made streamed unauthorized responses terminal.
- `tests/test_auth.py` — separated buffered retry and streamed terminal cases.
- `scripts/check_docs_plans.py` — enforced source, test, and plan contracts.
- `README.md`, `SECURITY.md`, `VISION.md` — documented the byte-stream boundary.
- `docs/plans/2026-06-26-streaming-auth-retry.md` — recorded design and evidence.

### Tests

- 38 tests passed under Python 3.10.20, 3.12.3, and 3.14.6.
- Root and external-directory `make check` passed for all three versions;
  Python 3.10 used the clean official container for its nested audit environment.
- Two hostile source/test contract mutations were rejected.
- Hosted Check runs `28254051784` and `28254055539` passed the full Python
  3.10/3.12/3.14 matrix, and CodeQL run `28254054317` passed on implementation
  commit `593253b2f3b1a70e94bb5d34beeec594718f95a4`.

### Findings

- Tornado invokes `streaming_callback` for chunks before the final response is
  available, so replay cannot safely retract or separate already-emitted bytes.
- Buffered async 401 responses retain the existing non-blocking single retry.

### Blockers

- The uv-managed Python 3.10 interpreter lacks `ensurepip`, so local
  `pip-audit` nested-environment creation failed; the official 3.10.20
  container completed the exact gate instead.
- Codex review was attempted once and skipped after HTTP 401 failures on both
  WebSocket and HTTPS transports.

### Next action

- Require hosted Python 3.10/3.12/3.14 and CodeQL checks on the exact PR head,
  then merge that SHA and confirm default-branch health.

## 2026-06-26

- Documented the tested Python 3.10/3.12/3.14 and Tornado 6 client matrix
  separately from the legacy Splunk session-key REST protocol surface.
- Clarified that mocked tests do not establish a live Splunk server version
  matrix and that JWT authentication-token support is outside the current API.

## 2026-06-21

- Isolated repository verification from caller-controlled roots, shells,
  non-executing Make modes, preload metadata, and additional Makefiles while
  preserving the trusted Python-version override.
- Added bounded Make authority coverage and pinned hosted dispatch to the
  absolute GNU Make launcher.

## 2026-06-20

- Pinned transitive `msgpack 1.2.1` in the verification toolchain to remediate
  `GHSA-6v7p-g79w-8964` from `pip-audit`'s CacheControl dependency graph.
- Extended the canonical documentation checker so pin removal, downgrade, or
  missing advisory evidence fails the shared gate.

## 2026-06-19

- Made supported XML, JSON, and text responses with missing bodies use the
  parser's normalized empty body instead of raising or returning `None`.

## 2026-06-16

- Raised the pinned and declared Tornado floor to 6.5.7, the first release that
  fixes credential leakage advisory `GHSA-pw6j-qg29-8w7f`.

## 2026-06-14

- Added session-key control-character validation for direct and login-provided
  credentials before Authorization header construction.
- Added session-key header whitespace validation for caller-provided
  Authorization credentials and centralized login validation on that boundary.

## 2026-06-13

- Added shared session-key whitespace validation for synchronous and
  asynchronous login responses without normalizing credential values.
- Rejected disabled, non-finite, boolean, and malformed request timeouts before
  synchronous or asynchronous Tornado client construction while preserving
  positive finite custom values across bounded retries.

## 2026-06-12

- Added a 20-second default synchronous transport timeout and preserved custom
  timeouts across the single unauthorized retry.
- Capped synchronous, asynchronous, retried, and streamed Splunk responses at
  1 MiB in Tornado and rejected oversized custom response bodies before parser
  dispatch, with boundary, cleanup, streaming, and mutation coverage.
- Replaced blocking session refresh in the async 401 path with a non-blocking
  bounded login request that replays once only after a safe session key and
  otherwise returns the original unauthorized response.
- Centralized sync and async login response validation so missing or unsafe
  server-provided session keys are rejected before refresh state changes.

## 2026-06-10

- Bumped the package to 0.2.0 for the Python 3.10+, Tornado 6, and lxml 6
  compatibility baseline.
- Preserved callback delivery for asynchronous transport failures while moving
  to Tornado's future-returning HTTP client API.
- Replaced removed Tornado callback helpers with future-based async request
  completion while preserving the public response callback behavior.
- Added pinned PEP 517 wheel and source-distribution builds with Python >=3.10
  package metadata.
- Expanded GitHub Actions to fixed Ubuntu 24.04 runners across Python 3.10,
  3.12, and 3.14 on every push and pull request, with concurrency cancellation.
- Made the hosted matrix rerun `make check` from a temporary working directory
  to continuously enforce path-independent Make targets.
- Made all Makefile checks independent of the caller's working directory.
- Included the Markdown long description and requirement inputs in source
  distributions so wheel builds from the sdist do not fail.
- Added a least-privilege GitHub Actions workflow using pinned Node 24 actions
  and credential-free checkout to run the complete `make check` baseline.
- Pinned verified Tornado 6.5.6, lxml 6.1.1, setuptools 82.0.1, and pip-audit
  2.10.0 baselines, with bounded runtime package metadata and vulnerability
  auditing.
- Added a docs/source guard requiring the CI workflow and completed CI baseline
  plan to remain checked in.

## 2026-06-09

- Rejected non-text session-key values before constructing Splunk Authorization
  headers, with regression and static coverage.
- Preserved repeated Splunk query and POST parameters by centralizing request
  argument encoding with `doseq=True`, with regression coverage.
- Switched response parser dispatch to exact normalized media types, including
  `application/xml`, and added coverage for near-match content types.
- Rejected CR/LF-bearing session keys before constructing Splunk Authorization
  headers, with mocked regression coverage.
- Narrowed XML and JSON parser exception handling and added regression coverage
  for invalid parser payloads.
- Normalized Splunk response `Content-Type` casing before parser dispatch and
  added regression coverage for mixed-case JSON headers with parameters.
- Added a no-network, no-entity-resolution XML parser for Splunk XML responses.
- Added mocked and entity-response coverage plus a static source guard for safe
  XML parsing under `make check`.

## 2026-06-08

- Stopped sync requests from retrying 401 responses when session refresh fails
  to produce a replacement key, with mocked coverage.
- Bounded unauthorized Splunk request retries to one session-key refresh and
  added mocked sync/async coverage.
- Added `make check` as the shared repository verification alias.
- Made Tornado sync and async Splunk requests pass `raise_error=False` so 401
  responses reach the session refresh/retry path.
- Closed synchronous Tornado HTTP clients after each request and added mocked
  coverage for request kwargs, auth headers, response parsing, and client close.
- Added a Makefile verification gate for Python syntax checks, unit tests, and
  package metadata checks.
- Added tests for Splunk JSON response parsing and query parameter encoding.
- Fixed JSON parsing by importing Tornado's `escape` module explicitly.
- Made request URL/body encoding work on both Python 2 and Python 3 runtimes.
- Added runtime dependency metadata for Tornado and lxml.
- Added canonical `docs/plans` coverage and a docs-plan checker under
  `make check`.
