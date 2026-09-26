---
name: construction-scheduling
description: Construction planning and scheduling expert: CPM network calculation (ES/EF/LS/LF, total and free float, critical path), baseline programme review, look-ahead planning, progress updating and schedule quality checks (DCMA 14-point style). Use this skill whenever the user mentions a construction programme or schedule, Primavera P6, MS Project, critical path, float, Gantt chart, activity list with predecessors, baseline, 3-week or 6-week look-ahead, programme submission to the Engineer / Project Manager, recovery or acceleration schedule, or asks "when will the project finish" for a building, civil, infrastructure or MEP job, even if they don't say "CPM".
---

# Construction Scheduling (CPM)

Help planners and project managers build, check and explain construction programmes. The goal is a programme that is logically sound, contractually defensible and useful on site, rather than just a bar chart.

## When a user gives you activities

1. Get the activity data into a CSV with columns `id,name,duration,predecessors` (durations in working days). The predecessor syntax is `A` (finish-to-start), `A:SS+2`, `B:FF-1` or `C:SF`, with several predecessors separated by `;`. See `assets/sample_activities.csv`.
2. Run the calculator rather than doing CPM arithmetic by hand, because mental float calculations on more than about 10 activities are error-prone:
   ```bash
   python3 scripts/cpm_scheduler.py activities.csv --start 2026-10-01 --weekend Fri,Sat
   ```
   - `--weekend` sets the non-working days: `Sat,Sun` is the default, and `Fri,Sat` is common in the GCC.
   - `--holidays 2026-12-02,2026-12-03` excludes public holidays.
   - `--json` gives machine-readable output, for example if you want to chart it afterwards.
3. Explain the results in site language:
   - the project duration and the finish date;
   - the critical path as a chain, for example Mobilisation → Excavation → Raft → Columns L1 → …;
   - near-critical paths (total float ≤ 10 days), which is where the next delay will come from;
   - activities with large float, which you can use for resource levelling.
4. Report the logic problems the script flags: open ends, dangling activities, negative lags and very long durations. Explain why each one matters (see the checks below).

## Schedule quality checks

When reviewing someone's programme, whether a P6 export, an Excel file or a pasted list, check these points. They follow the DCMA 14-point assessment, adapted for construction:

| Check | Threshold | Why it matters |
|---|---|---|
| Missing logic (open ends) | < 5% of activities | Delays won't flow through the network, so the critical path is unreliable |
| Leads (negative lags) | 0 | They hide overlap assumptions and are frequently challenged in delay claims |
| Lags | < 5% of relationships | A lag is unexplained time; use an activity instead (e.g. "concrete curing 7d") |
| Relationship types | ≥ 90% FS | Too much SS/FF usually means the logic hasn't been thought through |
| Hard constraints | < 5% | They override logic and create artificial float or negative float |
| High float | TF > 44 days on < 5% | Usually a sign of missing successors |
| Negative float | 0 in the baseline | The baseline must be achievable |
| Long durations | > 20 working days on < 5% | These can't be progressed or measured objectively, so split them |
| Critical path test | — | Adding 10 days to a critical activity must move the finish by 10 days |

## Building a construction programme

When asked to create a programme from scratch, structure the WBS like this:

1. **Milestones.** Commencement, access dates, sectional completions, Taking-Over / Completion.
2. **Pre-construction.** Mobilisation, permits, design approvals, long-lead procurement (for example lifts, switchgear, chillers and façade typically take 12–26 weeks).
3. **Construction by zone or level.** Substructure → superstructure → envelope → MEP first fix → finishes → MEP second fix → T&C.
4. **Commissioning and handover.** Testing, snagging, as-builts and O&M manuals.

Always include submittal and approval durations for key materials (typically 14–28 days of review per round). Missing procurement logic is the most common reason construction programmes fail.

## Look-ahead planning

For a 3- or 6-week look-ahead, filter to activities with ES in the window or in progress, and add:
- constraints to clear before each activity starts (drawings, material, labour, permits, predecessor work, access);
- the responsible person and the constraint-clear date.

This follows Last Planner principles: only activities whose constraints have cleared go into the weekly work plan. Track PPC (Percent Plan Complete = completed planned tasks ÷ planned tasks).

## Progress updates and delays

- Update against a fixed data date. Record actual start and finish dates and remaining duration, not just percentage complete.
- Compare the updated finish date with the baseline and identify which activities consumed the float.
- For entitlement to extension of time, hand over to the `variations-and-claims` skill, which covers delay analysis methods.

## Output format

When presenting a schedule analysis, use this structure:

```
## Programme summary
Start / Finish / Duration (working days) / Calendar

## Critical path
A → B → C ... (with durations)

## Near-critical activities (TF ≤ 10d)
table

## Logic issues found
table: issue / activities / why it matters / fix

## Recommendations
```

## Files
- `scripts/cpm_scheduler.py`: the CPM calculator (Python 3 standard library only).
- `assets/sample_activities.csv`: a sample 12-activity building job.
- `references/scheduling-reference.md`: relationship types, float definitions, typical durations and productivity rates. Read it if the user needs duration estimates.
