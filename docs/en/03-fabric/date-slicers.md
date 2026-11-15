# DimDate and Date Slicers

> Implementation status update (2026-11-14): Route A has been implemented in the demo environment and verified in the browser—a physical `created_date` column in the Lakehouse facts table, a DimDate calculated table with a single-direction relationship, 20 date slicers (5 each on Overview/CSAT/Raw Data/Trends/Daily), and measures displaying 0 for dates without data. Figures are unchanged (CSAT 4.40/5/45.5%). The prerequisite checks below remain for reuse in another environment.

Sources: S6 plan and subsequent status in S8–S9. The goal is consistent creation-date filtering. An early attempt to use a Direct Lake calculated column in a relationship was blocked; switching to a physical date column in the Lakehouse (Route A) resolved it.

## Pass the Model Prerequisite Checks First

Check the current model's storage mode, date-object support, and actual relationship paths. Prefer converting `created` to a physical `created_date DATE` in the Notebook/Lakehouse using the agreed time zone. A physical date column resolves granularity issues but does not automatically guarantee support for a calculated calendar and relationships.

If the current model does not support the target calculated table/relationship, evaluate a physical date dimension or another supported model mode, then reconcile the figures again. The materials do not establish that these alternatives were completed. Stop report deployment if the prerequisites have not been met.

Use the following example only in a model supporting DAX calculated tables. Adjust the range to the actual earliest/latest tickets and planning horizon:

```dax
DimDate =
ADDCOLUMNS (
    CALENDAR ( DATE ( 2026, 1, 1 ), DATE ( 2030, 12, 31 ) ),
    "Year", YEAR ( [Date] ),
    "Month", MONTH ( [Date] ),
    "WeekISO", WEEKNUM ( [Date], 21 ),
    "Day", DAY ( [Date] ),
    "ISOYear", YEAR ( [Date] - WEEKDAY ( [Date], 2 ) + 4 )
)
```

Target relationship: `DimDate[Date]` one-to-many to `jsm_sla_facts[created_date]`, single-direction and active. Date keys must be unique, non-null, and complete; configure the date table as required by the model. Do not relate midnight date values directly to `created` values containing time components, or introduce bidirectional relationships to conceal filtering problems.

If the model supports DAX calculated columns, a date without time can also be derived from year/month/day, but confirm support first. The date's time-zone semantics must remain unchanged.

## Five Slicers and Their Pages

Use four dropdowns—year, month, ISO week number, and day—plus a Between date range, all from the same DimDate. To display only the two endpoint inputs for Between, refer to verified PBIR from your own version rather than guessing JSON properties. Calendar year and ISOYear may differ in weeks crossing a year boundary; make clear which year is paired with week filtering.

Prioritize Overview and CSAT. Design the two Lifecycle pages and Raw Data page according to their own date semantics. The latest report_date in Lifecycle is a snapshot date and must not be inadvertently replaced by creation date. If creation-date filtering is also supported, preserve the independent semantics of both.

CSAT defaults to ticket creation date, not response date. The four dropdowns and Between filter intersect. Configure and validate cross-page synchronization separately. Existing bookmarks may restore old filters and must be checked.

Counts can use a dedicated display measure:

```dax
Ticket Count Display = COALESCE ( [Ticket Count], 0 )
```

Here, `[Ticket Count]` stands for your own existing measure, with its deduplication and filter logic unchanged. Do not fill every average, rating, and rate with zero. For continuous date trends, also check the date axis and the display of items with no data.

## Acceptance

- Before making changes, save ticket, SLA, group, Lifecycle, and CSAT baselines at the same refresh point and filter context.
- Compare all dates, a single day, a single week, a week crossing a year boundary, dates without data, intersections of multiple slicers, and cleared filters.
- Check blank dates and out-of-range records. Make date-filter propagation to all measures explicit and preserve existing `ALL` / `REMOVEFILTERS` semantics.
- With no date restrictions, compare CSAT against the baseline from the same snapshot. Do not combine the 82-ticket and 87-ticket snapshots from different dates.
- For Raw Data exports, verify actual key and event sets rather than only page card figures.
- Test navigation, drill behavior, tooltips, synchronization, and bookmarks before declaring the deployment live.
