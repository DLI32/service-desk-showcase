# Generic Fabric Definition Scripts

Source approaches: S6, S8, and S9; see the [source mapping](../../docs/en/SOURCES.md). These have been rewritten as Python standard-library scripts without fixed accounts, resource identifiers, or installation paths. Python 3.9 or later is required. Network subcommands also require an authenticated Azure CLI with appropriate permissions. Only offline validation was performed during this compilation; no network subcommands were run.

## Private Working Directory

Keep all backups, plans, and candidate JSON files outside the repository. Set the following environment variables in your own terminal; there are no default resource values: `WORKSPACE_ID`, `REPORT_ID`, `MODEL_ID`, `NOTEBOOK_ID`, `PRIVATE_DIR`. `PRIVATE_DIR` must point to an existing private directory. Use `--az /path/to/az` to specify the CLI.

Run from the repository root:

```bash
python3 scripts/fabric/fabric_definition.py --help
python3 scripts/fabric/patch_pbir.py --help

python3 scripts/fabric/fabric_definition.py get reports \
  --workspace "${WORKSPACE_ID}" --item "${REPORT_ID}" \
  --output "${PRIVATE_DIR}/report-before.json"
```

`kind` supports `reports`, `semanticModels`, and `notebooks`, using PBIR, the default model format, and ipynb respectively. Output files are created exclusively and do not overwrite existing files. Definitions, Notebook source, and outputs may contain private information and must not be published directly.

## Offline Comparison and Patching

```bash
python3 scripts/fabric/fabric_definition.py compare \
  "${PRIVATE_DIR}/report-before.json" "${PRIVATE_DIR}/report-candidate.json"

python3 scripts/fabric/patch_pbir.py \
  --source "${PRIVATE_DIR}/report-before.json" \
  --plan "${PRIVATE_DIR}/patch-plan.json" \
  --output "${PRIVATE_DIR}/report-candidate.json"
```

The plan format below is illustrative only. Confirm part paths, properties, and old values against your own definition:

```json
[
  {
    "part": "definition/pages/<PAGE_ID>/visuals/<VISUAL_ID>/visual.json",
    "keys": ["position", "x"],
    "old": 20,
    "new": 40
  }
]
```

String keys identify object properties; integers identify array indices. Only existing properties are modified, and both the old value and its JSON type must match. Repeated modifications to the same property are prohibited. Input files are not modified, and unselected part payloads remain unchanged. The script does not add visuals, repair references, or validate the PBIR schema.

`compare` compares SHA-256 hashes of decoded payloads by part path. JSON is normalized by sorting; text/binary content uses original bytes. Exit codes are 0 for identical payloads, 1 for differences, and 2 for input errors. Comparison covers payloads only, not outer definition metadata. Difference output may contain private part paths; sanitize logs before sharing.

## Deployment and Readback: Modifies Remote Resources

First follow the [CLI workflow](../../docs/en/03-fabric/cli-pbir.md) to complete backups, model prerequisite checks, and candidate review, then run:

```bash
python3 scripts/fabric/fabric_definition.py update reports \
  --workspace "${WORKSPACE_ID}" --item "${REPORT_ID}" \
  --input "${PRIVATE_DIR}/report-candidate.json" \
  --baseline "${PRIVATE_DIR}/report-before.json" \
  --readback "${PRIVATE_DIR}/report-readback.json"
```

Before submission, the script reads the remote definition again and compares it with the baseline, stopping if the payload has changed. Concurrent changes can still occur between checking and submitting; this does not replace a collaboration lock or change window. Use the latest baseline for the corresponding target. The script does not infer which target a file belongs to.

The script submits the complete definition, polls using a same-origin operation identifier, then independently calls getDefinition and saves the readback after the update completes. The default request timeout is sixty seconds and the total polling limit is thirty minutes, adjustable with `--timeout` / `--poll-timeout`. It refuses to follow HTTP redirects and does not output access tokens, API response bodies, or authentication stderr.

On errors, the script does not automatically resubmit or roll back. In particular, after a submission timeout, check private service records first to determine whether execution occurred. Readback differences produce exit code 2 and require review of server normalization or content changes. Successful deployment still requires additional validation of model processing, data, page interactions, and exports.

For rollback, use the original definition as input and the latest current definition as baseline, choosing a new readback path. Restore the report before the model. The script does not back up or restore data, credentials, capacity, connections, or schedules.
