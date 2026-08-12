# Project instructions

## Python Env

- Use `uv` for Python.
- Run Python commands with `uv run`.
- Add or remove dependencies with `uv add` or `uv remove`; do not edit dependency declarations manually.

## Validation

After changing code:

1. Run the relevant automated tests, if they exist.
2. Run one minimal runtime check that exercises the changed behavior
   (for example, an import check, CLI `--help`, or a small synthetic input).
3. In the final report, list:
   - commands run and their results;
   - checks not run, with the reason.

Do not state or imply that a change is verified unless the applicable checks passed.

## Data

- Treat files under `data/raw/` as immutable source data.
- Do not delete or overwrite GTFS, GTFS-RT, OSM, or SUMO source data.
- Do not commit large datasets, generated models, logs, or simulation outputs.
- Preserve raw GTFS-RT protobuf files before creating derived data.

## AWS and Terraform

- Do not run `terraform apply` or `terraform destroy` unless explicitly requested.
- Do not upload, modify, or delete S3 objects unless explicitly requested.
- Run `terraform fmt` and `terraform validate` after Terraform changes when available.
- Prefer reproducible configuration over manual AWS Console changes.

## Scope

- Ask before making a design change that affects data formats, graph definitions,
  observations, actions, rewards, or SUMO scenario assumptions.