# Trial Expiry and Archiving

Sources: S2–S4 and S6. This document retains the archiving method without publishing expiry dates, schedule identifiers, or resource inventories from the real environment.

## Close Out Dependencies Together

The contact center instance, Fabric capacity trial, and Notebook schedules have separate lifecycles. In the historical case, the call-record source expired first while the refresh schedule continued, leading to errors. Overwrite protection preserves old data; it cannot keep the data updating.

Record source-service expiry, capacity expiry, planned shutdown, and archive dates in a private operations checklist, allowing a validation window. Historical materials mention grace periods and deletion mechanisms, but these were not verified online during this compilation. Do not rely on a fixed number of days to preserve your work, and do not assume any automatic renewal or charging behavior.

## Pre-Expiry Archive Checklist

1. Export Notebook source and parameter documentation, clearing cell outputs and secret values.
2. Back up model, report, and necessary configuration definitions, recording formats and object dependencies. Definition backups do not contain model data.
3. Export private snapshots of facts, derived tables, event logs, and status intervals. Record time zone, schema, refresh point, row counts, and checksums.
4. Save measures, relationships, date definitions, Automation text, and recovery steps. For configuration references, record only secret reference names, not secrets.
5. In an isolated environment, verify that backups are parseable, fields are complete, and key baselines can be reproduced.
6. Stop schedules whose dependencies are about to become unavailable. Revoke unused credentials and expanded instance permissions, and record the last successful refresh and data cutoff time.

Do not put report definition backups, real CSV files, raw API responses, PDFs, or screenshots in the public repository. Keep internal archives in controlled storage. Public sharing should include only rewritten documentation, fictional examples, and generic code.

## What Remains Usable After Expiry

Jira Automation is decoupled from Fabric. Unavailable capacity does not automatically stop Jira rules; separately check their quotas, identities, and schedule status. Dashboards should show the data cutoff time so that old figures are not mistaken for live data.

Moving to paid capacity is a separate purchasing decision. Confirm costs, data recovery capabilities, and the pause strategy first. This project performs no purchasing, renewals, or remote operations.
