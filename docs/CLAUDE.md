# CLAUDE.md

## Mission

Build a reproducible, open-data, MicroRail-inspired railway rescheduling research system. GTFS and OSM provide the source data, GROSS generates the upstream SUMO scenario, and this repository owns the canonical scenario contracts, deterministic simulator, policies, learning, and evaluation.

This is research software, not a safety-certified railway control system.

## Read before changing code

Read these files completely, in order:

1. `docs/requirements.md`
2. `docs/technical-requirements.md`
3. `docs/technology-decisions.md`
4. `docs/implementation-audit.md`, if present
5. Relevant source, schemas, tests, and any `AGENTS.md`

Inspect the repository and tests before editing. Preserve unrelated user changes.

## Non-negotiable semantic boundaries

- Do not equate OSM nodes, SUMO edges, rail signals, GROSS clusters, signal blocks, or driveways with real track circuits.
- Use `verified_track_circuit` only when an explicit source verifies real track-circuit boundaries.
- The default open-data resource profile is `open_block`, based on SUMO signal blocks or driveways.
- Mechanically subdivided resources are `synthetic_section`, never real track circuits.
- Mark derived values as `observed`, `derived`, `assumed`, or `unknown` and retain source IDs or an assumption ID.
- Do not fabricate signals, blocks, switch states, platform use, rolling-stock data, freight services, operational rules, formation times, or release times.
- GROSS is an upstream scenario generator. It is not the RL environment and does not establish real interlocking fidelity.
- Teleportation is a failure category, not a valid completed railway solution.
- Action masking does not prove formal deadlock freedom. Keep an independent feasibility validator.
- Report modeled feasibility accurately; do not imply operational certification.

## Required implementation order

1. Repository and schema audit
2. Typed canonical contracts
3. Tiny synthetic scenario
4. Deterministic event simulator
5. Resource reservation and release
6. Candidate routes and action masking
7. Independent feasibility validation
8. FCFS baseline and metrics
9. GROSS adapter
10. Open-data corridor validation
11. Gymnasium adapter
12. Graph observations
13. GNN-DDQN
14. Multi-seed evaluation and ablations

Do not start with neural-network training. Do not skip a gate whose acceptance criteria have not passed.

## Architecture rules

- Keep external parsing, domain models, simulation, environment adapters, policies, learning, and evaluation in separate modules.
- The simulator consumes the versioned Canonical rail scenario, not GROSS/SUMO XML directly.
- Domain and simulator modules must not depend on PyTorch, PyTorch Geometric, Gymnasium, cloud SDKs, or plotting libraries.
- The independent validator must not import policy or action-mask implementations.
- Stable IDs must derive from semantic content, not incidental list or dictionary order.
- Put assumptions and thresholds in validated configuration, not scattered constants.
- Schema-breaking changes require a schema-version update and a decision record.

## Python environment

- Use `uv` for Python.
- Run Python commands with `uv run`.
- Add or remove dependencies with `uv add` or `uv remove`.
- Do not hand-edit dependency declarations or `uv.lock`.
- Prefer the minimum new dependency needed for the task.
- Keep CPU-only tests working even when GPU training is supported.

Typical commands, only when configured by the repository:

```bash
uv sync --frozen
uv run pytest
uv run ruff format --check .
uv run ruff check .
uv run mypy src
```

Do not invent commands or claim checks passed if the tools are not configured.

## Code quality

- Make small, reviewable changes and avoid unrelated refactors.
- Use type hints for public and domain interfaces.
- Add concise docstrings that explain semantics, units, and invariants.
- Prefer explicit immutable domain objects where practical.
- Include units in names or types for time, distance, and speed.
- Use structured logging. Avoid ad-hoc `print` in library code.
- Fail closed on missing required inputs, invalid topology, empty route sets, or schema mismatch.
- Record fallback, repair, exclusion, and confidence instead of silently continuing.
- Never catch broad exceptions merely to suppress failures.

## Data rules

- Treat `data/raw/` as immutable source data.
- Do not delete or overwrite GTFS, GTFS-RT, OSM, or SUMO source data.
- Preserve raw GTFS-RT protobuf files before deriving tables.
- Do not commit large datasets, generated scenarios, models, checkpoints, replay buffers, logs, maps, or simulation outputs.
- Automated tests use tiny synthetic fixtures.
- Every real-data artifact must be traceable to source URL/reference, retrieval time, SHA-256, size, service date, and attribution/license metadata.
- Never store credentials, bearer URLs, signed URLs, or personal data in manifests or logs.

## Security rules

- Treat every external data file, archive, manifest, config, path/URI, GROSS output, and checkpoint as untrusted unless an explicit trusted-artifact policy says otherwise.
- Follow the complete security contract in `docs/technical-requirements.md`; do not replace it with ad-hoc checks in individual adapters.
- Centralize finite input, decompression, element, subprocess, and captured-log limits in validated `SecurityLimits` configuration. Unbounded defaults are forbidden.
- Disable XML DTD, external entities, XInclude, and network access; use bounded streaming parsing. Use safe YAML loading and `allow_pickle=False` for NPZ.
- Resolve paths and archive members against allowlisted roots before reading or writing. Validate remote schemes, hosts, redirects, size, and timeout; verify an expected hash when available, otherwise quarantine and validate before atomic promotion.
- Invoke subprocesses with validated argv, `shell=False`, a minimal environment, fixed working directory, timeout, and bounded output.
- Never load an untrusted pickle or full training checkpoint. Prefer weights-only model loading and validate manifest, hash, schema, keys, dtypes, shapes, and parameter count.
- Add malicious-fixture tests for each implemented trust boundary and prove rejection causes no state/output mutation and no secret leakage.
- If a required security limit or trust decision is not yet defined, stop at the current gate and report the exact missing decision instead of choosing an unbounded fallback.

## GROSS rules

- Initial upstream commit: `d1134079021eab78fb40fb1e30580809d396f00e`.
- Initial SUMO compatibility baseline: `1.26.0`.
- Run GROSS as an external checkout or container and record the commit, image digest, and `sumo --version`.
- Do not vendor or redistribute GROSS source until its license is explicitly confirmed.
- Preserve and inspect GROSS logs, repairs, unrouted trips, mapping fallbacks, teleports, and deadlocks.
- Do not assume one `railsignal-block-output` run covers unused driveways; measure movement coverage.

## Domain invariants

All implementations and tests must preserve:

1. Simulation time is monotonic.
2. Conflicting trains never reserve or occupy the same exclusive resource simultaneously.
3. A resource is not reused before release.
4. Route resource sequences are connected and ordered.
5. Stop order and relevant times are monotonic.
6. `WAIT` is available at a normal decision point.
7. Masked actions do not mutate state.
8. Identical scenario, config, policy, and seed produce identical traces and metrics.
9. Early arrivals do not create negative delay objective values.
10. Completion, timeout, deadlock, conflict, invalid input, teleport, and error remain separate outcomes.

## Change control

Before changing any of the following, document the current behavior, proposed behavior, evidence, migration, and expected test changes, then ask for user approval:

- graph or resource semantics;
- observation features or normalization;
- action set, candidate generation, or ordering;
- objective or reward;
- reservation, release, deadlock, or teleport semantics;
- SUMO/GROSS compatibility profile;
- dataset split or primary evaluation metric.

Do not use an implementation convenience as justification for a scientific semantic change.

## Testing and validation

After changing code:

1. Run the relevant automated tests.
2. Run configured format, lint, and type checks relevant to the change.
3. Run one minimal runtime check that exercises the changed behavior.
4. Run `git diff --check` and inspect the final diff.
5. Confirm raw data and unrelated files were not changed.

Simulator changes require tests for event ordering, reservation/release, masks, independent validation, objective, termination, and same-seed repeatability. Learning changes require tests for masks in both action selection and DDQN targets, terminal bootstrap behavior, checkpoint completeness, and a tiny overfit sanity check.

Do not state or imply that behavior is verified unless the applicable checks passed. In the final report, list exact commands and results, plus checks not run and why.

## Git rules

- Inspect `git status` before and after work.
- Preserve all pre-existing changes.
- Do not commit generated data or secrets.
- Keep changes scoped to the requested task.
- Do not rewrite history, force-push, reset, or discard user changes.
- Do not create a commit unless explicitly requested.

## AWS and Terraform

- Cloud infrastructure supports scale-out; it is not a core domain dependency.
- Do not run `terraform apply` or `terraform destroy` unless explicitly requested.
- Do not upload, modify, or delete S3 objects unless explicitly requested.
- Run `terraform fmt` and `terraform validate` after Terraform changes when available.
- Prefer SSM; do not add SSH ingress by default.
- Do not place credentials in Terraform, user data, code, logs, or outputs.
- Scale instance and storage only after measuring peak CPU, RAM, disk, and I/O.

## Required final response

Lead with the outcome, then report:

- files changed;
- requirements or decision IDs addressed;
- assumptions added or unresolved;
- exact validation commands and results;
- checks not run and reasons;
- known gaps and the next valid gate;
- whether raw data, cloud resources, S3 objects, or unrelated user changes were modified.
