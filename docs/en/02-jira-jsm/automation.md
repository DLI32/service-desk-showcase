# Automation Rule Essentials

Source: S4. These are historical project-level practices, with no assurance that they apply to every plan or workflow. Use `<JIRA_SITE_URL>` for the site and `<COORDINATOR_EMAIL>` for coordinator recipients.

## Reminders Must Preserve Evidence of Inactivity

Send follow-up reminders by email only, without comments or mentions. Comments may refresh `updated`, causing the rule to erase its own evidence of inactivity. Reporting covers Incident and Service request; the initial reminder rollout covered Incident only.

Historically, six rules ran every day at 09:00 (Asia/Shanghai):

| Rule | Window / Action |
|---|---|
| Daily coordinator summary | One email summarizing all tickets requiring follow-up |
| Initial reminder for inactivity on our side | One to two days; notify the assignee |
| Escalation for inactivity on our side | Four to five days; notify the assignee and copy the coordinator |
| Initial reminder while waiting for the customer | Two to three days; notify the assignee |
| Escalation while waiting for the customer | Five to six days; notify the assignee and copy the coordinator |
| Automatic closure | Transition from Resolved to Closed after seven days |

Use half-open windows to express exact time ranges, for example:

```jql
project = "<PROJECT_KEY>"
AND status = "In Progress"
AND updated > -2d AND updated <= -1d
```

This illustrates a window for one status only. Validate the actual status set, issue type names, and terminal-state exclusions in search first. With daily execution and an unchanged updated value, each window normally matches only once. Manual reruns, delays, and catch-up runs after downtime may cause duplicates or missed notifications; this window method does not guarantee persistent deduplication.

For automatic closure, verify that seven days have elapsed since entry into Resolved. Do not assume `updated` is the resolution time without validation. Also verify permitted workflow transitions, actor permissions, timing restarts after reopening, and execution audits. The source materials list only a first-run plan, with no proof of a successful first run.

## A Summary Email Grouped by Status

Overall Lookup → separate Lookups by status → variable rendering → assemble one HTML email. Columns are ticket link, summary, assignee, and inactive days. Construct links from `<JIRA_SITE_URL>` and the current issue key.

- Resolved tickets often already have a resolution. Do not let a global `resolution = Unresolved` condition exclude tickets pending closure.
- At the time, `{{#if}}` in variables made the entire section blank; a plain iteration template worked. Show zero tickets and an empty table when a section has no results.
- At the time, `{{updated.diff(now).days}}` produced positive inactive-day values. Verify direction and units in the target environment first.
- Explicitly display an empty assignee as “Unassigned.” Escape summaries using the template engine's supported method before inserting them into HTML.
- A Success audit result does not prove that the email content is correct. Inspect actual delivery, section counts, links, and the sign of day values.

## Populate the Assignment Group Automatically from Service

Route the Assignment group by Service when a ticket is created. Historical mappings included M365 → Infra-M365, VPN → Infra-Network, Laptop → Infra-DeskSide, Citrix → Infra-Server, Workday → APP-Workday, and Web App / Portal → APP-Web App.

Opening group identifies the reporter's group; Assignment group identifies the group responsible for resolution. They are not interchangeable. Use `<OPENING_GROUP_FIELD>` and `<ASSIGNMENT_GROUP_FIELD>` for field identifiers; do not copy another environment's custom field numbers. Validate the actual field values and the automation entries in ticket history.

Use the target environment's quotas and action billing rules rather than historical plan limits. Run a trial, inspect the emails, then observe normal scheduled execution. Changing rule configuration alone does not establish successful ongoing operation.
