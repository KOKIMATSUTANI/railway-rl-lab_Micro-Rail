# Claude Code implementation prompt

Paste the prompt below into Claude Code from the repository root. It is intentionally phase-gated: the first run should establish semantics and a tested vertical slice, not attempt full-scale RL training.

---

You are implementing an open-data, MicroRail-inspired railway rescheduling research system in the current repository.

## Read first

Before editing anything, read these files completely:

1. `CLAUDE.md` if present; otherwise `docs/CLAUDE.md`
2. `docs/requirements.md`
3. `docs/technical-requirements.md`
4. `docs/technology-decisions.md`
5. Any existing `AGENTS.md`, `README.md`, architecture docs, schemas, tests, and relevant source files

Treat explicit repository instructions as authoritative. If an existing repository decision conflicts with the proposed documents, stop and report the conflict instead of silently choosing one.

## Project goal

Replace the non-public infrastructure and timetable data used by MicroRail with open GTFS and OSM/OpenRailwayMap data. Use GROSS to generate the upstream SUMO scenario, convert its outputs into a versioned canonical rail scenario, and implement the MicroRail-inspired rescheduling stack in this order:

1. repository and data-contract audit;
2. typed canonical scenario contracts;
3. tiny deterministic scenario;
4. event-driven simulator;
5. resource reservation and release;
6. predefined routes and deterministic action masking;
7. independent feasibility validation;
8. FCFS baseline and metrics;
9. GROSS output adapter;
10. open-data corridor validation;
11. Gymnasium adapter;
12. graph observation encoder;
13. GNN-DDQN;
14. multi-seed evaluation and ablations.

Do not start with neural-network training.

## Authoritative research boundaries

- MicroRail models real track circuits and route-lock section-release. GTFS, OSM, and GROSS do not normally provide verified track-circuit or interlocking data.
- Never equate an OSM node, SUMO edge, rail signal, or GROSS cluster with a real track circuit unless an explicit source proves that semantic identity.
- The default open-data resource profile is `open_block`: SUMO signal blocks or driveways are exclusive operational resources.
- If infrastructure is mechanically subdivided, call the result `synthetic_section`, not `track_circuit`.
- Every derived field must be marked `observed`, `derived`, `assumed`, or `unknown`, with source IDs or an assumption ID.
- GROSS is the scenario generator, not the RL environment and not evidence of real interlocking fidelity.
- A GROSS/SUMO teleport is not a valid completed railway solution. Record it as a failure category.
- Action masking may enforce modeled resource exclusivity, but it does not by itself prove formal deadlock freedom. Keep an independent validator.
- Do not fabricate platform assignments, signal blocks, switch states, rolling-stock characteristics, freight services, formation times, release times, or dispatching rules.

## GROSS integration baseline

- Upstream repository: `https://github.com/ethz-coss/GROSS`
- Initial pinned commit: `d1134079021eab78fb40fb1e30580809d396f00e`
- Initial SUMO compatibility baseline: `1.26.0`
- Run GROSS as an external checkout/container and consume its outputs through an adapter.
- Do not vendor or copy GROSS source into this repository until its licensing has been explicitly confirmed. At the pinned commit, no explicit LICENSE file was observed.
- Relevant output contract:
  - `sumo/final.net.xml.gz`
  - `sumo/stops.add.xml.gz`
  - `misc/mapping.xml.gz`
  - `misc/output_gtfs.xml.gz`
  - `routing/*_pairs.xml.gz`
  - `sim/*.rou.xml.gz`
  - GROSS logs and unrouted/repair reports

## Task for this run

Work only through Gate 0 and Gate 1 unless the user explicitly asks for a later gate.

### Gate 0: audit

Inspect the repository and report, with exact paths:

- current package layout and project root;
- existing GTFS, GTFS-RT, OSM, GROSS, SUMO, graph, RL, and Terraform code;
- existing schemas and the actual semantic meaning of current nodes and edges;
- existing tests and their current status;
- Python/dependency tooling;
- generated-data locations and `.gitignore` coverage;
- whether GROSS is already present, pinned, modified, or wrapped;
- current working-tree changes that must be preserved;
- gaps between the repository and the requirements.

Write the audit to `docs/implementation-audit.md`. Use an evidence table with columns `Claim`, `Evidence path`, `Status`, and `Required action`. Do not infer semantics from filenames alone.

Then present a short implementation plan. If the existing graph, observation, action, reward, simulator, or SUMO assumptions must change, stop after the audit and ask for approval with the exact proposed change.

### Gate 1: tiny deterministic vertical slice

If the audit finds no blocking semantic conflict, implement the smallest complete slice using synthetic fixtures only:

- one tiny directed rail graph;
- two trains requesting one mutually exclusive resource;
- one nominal route per train;
- `WAIT:30`;
- one alternative route if the existing domain model supports it without speculative redesign;
- a deterministic event queue;
- explicit reservation, occupation, and release;
- decision moments for train entry, resource/signal approach, dwell completion where applicable, and wait expiry;
- action candidates with stable IDs;
- deterministic action masks with reason codes;
- an independent feasibility validator that does not import the policy or mask implementation;
- a deterministic FCFS policy using the same candidates and mask;
- episode termination and total-delay metrics;
- an end-to-end CLI or minimal runtime entry point for the fixture.

Do not implement GNN, DDQN, replay buffers, large GROSS runs, AWS provisioning, or dashboards in Gate 1.

## Domain invariants

The implementation and tests must enforce all of the following:

1. Simulation time never moves backward.
2. Mutually exclusive resources cannot be reserved or occupied by conflicting trains at the same time.
3. A resource cannot be reused before release.
4. A route is an ordered, connected sequence of operational resources.
5. Planned and realized stop times are monotonic within their defined semantics.
6. `WAIT` is always available at a normal decision point.
7. Masked actions cannot mutate simulator state.
8. Identical scenario, policy, config, and seed produce the same event trace and metrics.
9. Early arrival does not reduce the reported objective below zero.
10. `COMPLETED`, `TIME_LIMIT`, `DEADLOCK`, `CONFLICT`, `INVALID_INPUT`, `TELEPORT_DETECTED`, and `ERROR` remain distinguishable.

## Engineering constraints

- Use `uv` for Python dependency management and execution.
- Use `uv add` or `uv remove`; do not manually edit dependency declarations.
- Preserve all existing user changes and avoid unrelated refactors.
- Keep raw GTFS, GTFS-RT, OSM, SUMO source data immutable.
- Do not commit large datasets, generated scenarios, models, replay buffers, logs, or experiment outputs.
- Use small synthetic fixtures in automated tests.
- Keep parsing/I/O, domain models, simulation, policies, learning, and evaluation in separate modules.
- Prefer immutable typed domain objects where practical.
- Add type hints and concise docstrings to public APIs.
- Use structured logging; do not rely on ad-hoc print statements in library code.
- Put assumptions in configuration and provenance, not scattered magic constants.
- Stable IDs must not depend on incidental list order.
- Do not download new large datasets or mutate cloud resources unless explicitly requested.

## Security constraints

Implement only the trust boundaries exercised by the current gate, but implement them according to the full contract in `docs/technical-requirements.md`.

- Treat external files, archives, manifests, paths/URIs, GROSS output, and checkpoints as untrusted by default.
- Put finite parser, decompression, archive, element, subprocess, and captured-log limits in one validated `SecurityLimits` configuration; never use an unbounded default.
- Disable XML DTD, external entities, XInclude, and network access and use bounded streaming parsing. Use safe YAML loading and disable pickle-backed NumPy loading.
- Resolve local paths and archive members against allowlisted roots. Validate remote schemes, hosts, redirects, byte limits, and timeouts; verify an expected hash when available, otherwise quarantine and validate before atomic promotion.
- Run subprocesses with validated argv, `shell=False`, minimal environment, fixed cwd, timeout, bounded logs, and checked exit status.
- Do not load untrusted pickle or full PyTorch checkpoints. Use weights-only loading for inference and validate artifact manifest, hash, schema, keys, dtypes, shapes, and parameter count.
- Redact credentials, authorization/cookies, signed URL queries, environment values, control characters, and input bodies from logs and exceptions.
- Add tiny malicious fixtures for each trust boundary introduced in this run. Rejection must not mutate state or outputs.
- Do not invent a security limit. If Gate 0 has insufficient measurements to choose one, define the typed field and test profile, record the unresolved production value, and stop before the affected real-data gate.

## AWS and Terraform safety

- Do not run `terraform apply` or `terraform destroy`.
- Do not create, modify, upload, or delete S3 objects.
- If Terraform files are changed, run `terraform fmt` and `terraform validate` when available.
- Do not open SSH ingress or add credentials to files, user data, logs, or outputs.

## Validation required

After each meaningful implementation step:

1. run the relevant automated tests;
2. run formatting/linting and static typing that the repository already configures;
3. run one minimal runtime check that exercises the changed behavior;
4. inspect `git diff --check` and the final diff;
5. confirm raw data and unrelated files were not changed.

For Gate 1, tests must include:

- unit tests for event ordering, reservation/release, masks, objective, and termination;
- at least one property-based invariant test if Hypothesis is already available or can be added without disrupting the project;
- one end-to-end integration test from fixture load through FCFS completion and metrics;
- a repeatability test comparing event traces under the same seed;
- a negative test proving the independent validator catches an injected conflict.
- malicious fixtures for every parser/path/archive/subprocess boundary added in Gate 1, including no mutation and log-redaction assertions.

## Required final report

Lead with the achieved outcome. Then include:

- files changed;
- requirements implemented by ID;
- assumptions introduced or left unresolved;
- exact commands run and their results;
- checks not run and why;
- known gaps and the next gate;
- confirmation that no raw data, cloud resources, S3 objects, or unrelated user changes were modified.

Do not claim that a behavior is verified unless its applicable checks passed.

---

## Follow-up prompt for Gate 2

Use this only after Gate 1 has passed:

> Continue with Gate 2 from `docs/requirements.md` and `docs/technical-requirements.md`. First inspect an actual completed GROSS scenario and write a schema-mapping report before implementing the adapter. Prove the semantic meaning of every imported node, edge, signal, stop, route, and exclusive resource from file contents and GROSS/SUMO documentation. Import into the existing canonical contracts without changing simulator semantics. Treat signal blocks/driveways as `open_block` resources; do not label them as track circuits. Produce coverage, fallback, repair, unrouted, teleport, and deadlock reports. Use a small corridor snapshot first, run the relevant tests and one no-perturbation smoke simulation, and stop before Gymnasium or RL changes unless Gate 2 acceptance criteria pass.
