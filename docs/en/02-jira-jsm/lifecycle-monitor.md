# Lifecycle Monitor: Identify Open Tickets That Are Not Progressing

Source: S4. JSM manages SLA clocks and reminders, the Notebook precomputes follow-up status, and Power BI displays current actions and trends.

## Four Categories and Their Clocks

| Category | Definition |
|---|---|
| Unassigned | Empty assignee, restricted to statuses requiring follow-up |
| Inactivity on our side | In a status requiring action on our side, with no update for at least one day |
| Customer follow-up due | Waiting for customer, with no update for at least two days |
| Pending closure | Resolved but not Closed |

Flags are independent: one ticket may match multiple categories, so they cannot be added to obtain a unique ticket total. Waiting for customers is listed separately and is not counted as assignee inactivity. Inactivity buckets are: less than one day, one to two days, two to three days, three to seven days, seven to fourteen days, and fourteen days or more. Inclusive lower bounds and exclusive upper bounds are recommended; make the boundaries explicit.

Use Jira's native `updated` as the primary inactivity clock; change history alone misses activities such as comments. Time in status starts at the latest event entering the current status and is not the same as inactivity time. Terminal states include Closed, Canceled, and other terminal states in the actual workflow; Resolved may still belong to the pending-closure set.

## Data Layer

| Table | Grain and Responsibility |
|---|---|
| jsm_sla_facts | One row per ticket: current state, official SLA, updated_at, issuetype |
| jsm_assignment_log | One row per field change; retain assignee, status, team, opening group, assignment group, and priority |
| jsm_incident_daily | Daily snapshot: derived hours, ticket age, time in status, four category flags, and buckets |
| jsm_status_intervals | Each status entry/exit interval and its duration |

Historical practice used `/rest/api/3/search/jql` with `nextPageToken` / `isLast` pagination. Expanded changelog data is not guaranteed to be complete; retrieve per-ticket history to fill gaps when truncated. Do not continue using an obsolete search path and assume `startAt` retrieves everything.

Centralize derived definitions in the Notebook rather than repeating the logic in reports. Generate daily snapshots in an explicit business time zone and write repeated refreshes on the same day idempotently using the snapshot key. Do not apply UTC-to-local conversion again to timestamps that are already local and timezone-naive.

## Pages and Queues

Daily Follow-up displays six KPIs, inactivity buckets, action lists, a group matrix, and assignee distribution, using the latest report_date. Trends displays daily trends, the oldest tickets, average time in status, and event drillthrough. The drillthrough table requires `jsm_assignment_log` in the model, with a many-to-one relationship to the facts table by issue key.

The six coordinator queues cover unassigned tickets, breached SLA, overdue customer follow-up, high priority, inactive tickets in progress, and Resolved tickets not yet closed. Validate JQL counts in search before saving queues. Actual issue type names may have system prefixes; do not guess status names from experience.

## Historical Acceptance Snapshot

| Item | Count |
|---|---:|
| Total tickets | 82 |
| Open | 76 |
| Unassigned | 73 |
| Inactivity on our side | 63 |
| Customer follow-up due | 2 |
| Pending closure | 5 |
| Longest inactivity | 22.9 days |

The change log contained 25 events across 18 tickets; there were 13 status intervals. Status sections in the summary email totaled 81 tickets, including five pending closure, which differs from the 76 open tickets. These figures represent different sets and are not expected to add up directly.

Validation reconciled Jira queues, the reloaded report, individual ticket history, and actual emails. The initial unassigned count was one too high because Canceled had not been excluded. The increase in inactivity on our side came from tickets naturally crossing the one-day threshold. The first day's trend has only one point; do not fabricate a historical line.
