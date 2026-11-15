# Fabric CLI and PBIR Management Workflow

Sources: S6, S8, and S9; selected-subset export also draws on S5. S6 is a draft plan, and S8 records some corrections. Update (2026-11-14): model and report updateDefinition operations were successfully applied in the demo environment and passed readback comparison (each pushed twice, 0 differences). All 20 date slicers are live. The workflow below still applies.

## Definition Management Workflow

1. Establish a baseline for the current data and filter context. Export model, report, and Notebook definitions outside the repository.
2. Check model format, compatibility level, storage mode, and relationship support. Pass the model prerequisite checks first.
3. Modify only explicitly identified parts locally. TMDL is a definition format, while the definition API is a transport interface; they can be used together.
4. Export again before deployment and compare with the editing baseline. If concurrent changes are found, merge them and revalidate.
5. Submit the complete definition. Editing only a portion does not mean submitting only some parts.
6. Independently retrieve the result after a long-running operation completes. After an update, use getDefinition again for readback and compare each part.
7. Complete necessary model processing/refresh and data reconciliation before changing reports. A successful definition update does not establish that data has been calculated or pages are correct.

Generic command pattern:

```bash
fab api -X post "workspaces/${WORKSPACE_ID}/reports/${REPORT_ID}/getDefinition" -i '{"format":"PBIR"}'
```

Use your own installation paths for `fab` and `az`. Commands with the same name may belong to other tools, so confirm the executable first. See [scripts/fabric](../../../scripts/fabric/README_EN.md) for the rewritten generic scripts, which have no fixed workspace or account.

## Long-Running Operations and Readback

Historical responses used a Location pointing to a redirect host, so checking against a fixed API address failed. The rewritten script polls on the same public API origin using `x-ms-operation-id`; it does not forward access tokens to arbitrary redirect destinations. After a successful get operation, retrieve `/result`. For update, wait for completion, then issue an independent get for readback. Do not automatically resubmit after a polling timeout; check the original operation's status first.

Normalize JSON before hashing and retain original bytes for non-JSON content. The server may add default properties or normalize text. Inspect differences rather than automatically rolling back.

## Targeted PBIR Changes

| Part Pattern | Purpose |
|---|---|
| definition/report.json | Report settings and resource references; preserve where possible |
| definition/pages/pages.json | Page order; leave unchanged unless adding or removing pages |
| definition/pages/<PAGE_ID>/page.json | Page dimensions and background |
| definition/pages/<PAGE_ID>/visuals/<VISUAL_ID>/visual.json | Layout, styling, field bindings, and interactions |
| StaticResources/... | Resources such as themes and icons; additions must be included in parts |

`patch_pbir.py` replaces only existing properties whose original values match. The part and keys in a plan must come from your own definition. It does not generate slicers, validate the complete PBIR schema, or guess formatting property paths.

Copying an entire visual may also copy filters, sorting, drill behavior, sync groups, and interactions. New objects need unique names, matching paths, correct field bindings, and removal of old references. Copying a slicer does not establish cross-page synchronization.

## Raw Data Export of Selected Subsets

Historically successful flow: date slicers filter issue keys → Power BI button → Power Automate → parameterized Notebook → two CSV files. The flow passes the currently selected set of keys rather than start/end dates directly to the Notebook; event rows are filtered by the same keys.

1. Put the issue key in the button's data area first, then create the flow through the visual's embedded Edit option.
2. Inspect the trigger schema and actual click body to confirm they contain `Power BI values`. At the time, attempts to repair the old flow created without fields failed; the binding was ultimately replaced with a new flow.
3. Add Apply to each after the trigger, iterating over `triggerBody()?['entity']?['Power BI values']`. Read the issue key inside the loop; this was the schema-anchoring approach used at the time.
4. Use Select to extract the key list, then Compose to build the complete request body first. HTTP Body should reference only that output; avoid directly assembling incomplete JSON containing dynamic tokens.
5. POST pattern: `/v1/workspaces/<WORKSPACE_ID>/items/<NOTEBOOK_ID>/jobs/instances?jobType=RunNotebook`.

Parameter request body pattern:

```json
{"executionData":{"parameters":{"export_keys":{"value":"<SELECTED_KEYS>","type":"string"}}}}
```

Notebook parameter semantics: an empty string means all records, comma-separated keys specify a set, and `__NONE__` represents a valid empty selection. Empty selections produce headers only. Parsing failures or missing trigger fields must fail rather than accidentally exporting all records. This public project includes no actual flow definitions or CSV files.

Historical acceptance results: a ten-ticket selection produced ten validation rows and thirty-two event rows; the full set produced nineteen and seventy rows; an empty selection produced headers only in both files. Validate all three scenarios with actual clicks. A connector once reported an error after about one minute even though the Notebook had executed successfully. This is a historical observation, not grounds to treat every connector failure as normal. Check submission, Monitor, output timestamps, and row sets together.

During rollback, restore the report before the model to avoid report references to removed fields. Definition backups do not contain data, credentials, or schedules. Retain old bindings and recovery steps for the export flow, and retest a full export with an actual click.
