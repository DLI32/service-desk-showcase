# Sources, Evidence, and Sanitization Boundaries

This compilation was prepared solely from the designated local materials listed below, read individually. No other files referenced by those materials were read, and no online verification was performed. Filenames in the table are for traceability only; the originals are not included.

| ID | Source File |
|---|---|
| S1 | aliyun-ivr-spec-2026-11-11.md |
| S2 | 阿里云云联络中心IVR建造复盘-2026-11-12.md |
| S3 | 电话SLA-API自动刷新复盘-2026-11-13.md |
| S4 | jsm-sla-lifecycle-retrospective.md |
| S5 | RawData选段导出-联动实现总结.md |
| S6 | codex-cli-optimize.md |
| S7 | jsm-sla-showcase/SPEC.md |
| S8 | fabric_definition.py (original script; used only for its approach) |
| S9 | patch_pbir.py (original script; used only for its approach) |

## Output-to-Source Mapping

| Output | Sources and Compilation Scope |
|---|---|
| [README_EN.md](../../README_EN.md) | Architecture, purpose, and evidence boundaries from S1–S9 |
| [docs/en/01-aliyun-contact-center/ivr-guide.md](01-aliyun-contact-center/ivr-guide.md) | S1 prompts and targets; S2 final implementation and validation |
| [docs/en/01-aliyun-contact-center/telephony-sla-api.md](01-aliyun-contact-center/telephony-sla-api.md) | S3 metrics, refresh, and troubleshooting; S2 telephone intake context |
| [docs/en/02-jira-jsm/sla-showcase.md](02-jira-jsm/sla-showcase.md) | S7 design specification; unresolved SLA issues recorded in S4 lifecycle materials; S6 later demo snapshot |
| [docs/en/02-jira-jsm/lifecycle-monitor.md](02-jira-jsm/lifecycle-monitor.md) | S4 data model, definitions, and acceptance |
| [docs/en/02-jira-jsm/csat.md](02-jira-jsm/csat.md) | S6 metrics and date-filtering requirements; explicitly retained gaps where evidence of collection configuration is insufficient |
| [docs/en/02-jira-jsm/automation.md](02-jira-jsm/automation.md) | S4 emails, window method, automatic closure, and automatic group population |
| [docs/en/03-fabric/cli-pbir.md](03-fabric/cli-pbir.md) | S6 implementation draft; S8 long-running operation corrections; S9 status before actual patching; S5 selected-subset export |
| [docs/en/03-fabric/date-slicers.md](03-fabric/date-slicers.md) | S6 model and slicer plan; S8–S9 subsequent blocked status |
| [docs/en/03-fabric/trial-archive.md](03-fabric/trial-archive.md) | S2–S4 expiry and schedules; S6 backup and rollback boundaries |
| [scripts/fabric/fabric_definition.py](../../scripts/fabric/fabric_definition.py) | Rewritten from the approaches in S6 and S8; adds independent subcommands, parameterization, baseline checks, and restricted error output |
| [scripts/fabric/patch_pbir.py](../../scripts/fabric/patch_pbir.py) | Rewritten from the approaches in S6 and S9; parameter validation, original-value matching, and preservation of unchanged payloads |
| [scripts/fabric/README_EN.md](../../scripts/fabric/README_EN.md) | S6 and S8–S9 plus the actual parameters of the rewritten scripts |
| [LICENSE](../../LICENSE) | Standard MIT text added in this compilation, naming project contributors as copyright holders |
| [.gitignore](../../.gitignore) | Python, system, private configuration, and backup exclusions added in this compilation |
| [docs/en/SOURCES.md](SOURCES.md) | Source mapping and sanitization notes for this compilation |

## Sanitization Rules

Eight categories of information were handled, with actual content replaced by placeholders or omitted according to context:

1. Email addresses and recipient identities → `<EMAIL>`, `<COORDINATOR_EMAIL>`.
2. Telephone numbers, test inbound numbers, extensions, and allowlisted number suffixes → `<PHONE>`, `<TEST_NUMBER>`; no partial numbers retained.
3. Keys, access tokens, passwords, and access-key identifiers → `<SECRET_REF>` and similar placeholders; no real values retained.
4. Cloud accounts, login names, RAM identities, tenant and organization identifiers → `<ALIYUN_ACCOUNT>` and similar placeholders.
5. Instance, workspace, report, model, Notebook, schedule, and flow identifiers → semantic placeholders.
6. Jira sites, ticket-system addresses, and personal domains → `<JIRA_SITE_URL>`; original domains not retained.
7. Call identifiers, issue keys, custom fields, and page/visual identifiers → semantic field names or placeholders; no real object numbers retained.
8. Support tickets, orders, agent employee numbers, personal paths, and real-name entity information → removed or generalized.

All account-related materials and comparisons involving another cloud platform were omitted from this compilation. No original files, report definition backups, PDFs, or screenshots were packaged. Public service API addresses, brands, generic table names, dates, prompts, metrics, and algorithms were retained.

## Evidence Boundaries Users Must Recheck

- S7 gives both 141 and 142 as sample totals. Only the explicit 95/141 calculation is retained; no meaning is inferred for the other figure.
- S4's 82 tickets and S6's 87 tickets are different snapshots. The lifecycle email's 81 tickets include pending-closure items and differ from the set of 76 open tickets.
- S6 is an unimplemented plan; S9 explicitly records that model prerequisites had not yet been met. The date workflow and PBIR patch must not be treated as a successful implementation report.
- CSAT has snapshot metrics only. Invitations, collection, and special-status handling must be verified in your own environment.
- Permissions, free quotas, trial grace periods, and deletion policies were not verified in real time during this compilation; recheck them against the actual environment when deploying.

## Screenshot Sources

The three report screenshots were captured in the Fabric reading view on 2026-11-15 (Telephony SLA, JSM dashboard overview, CSAT and VoC analysis) and reviewed one by one: they contain no email addresses, phone numbers, personal names, or real call identifiers. The images live in docs/assets/.
