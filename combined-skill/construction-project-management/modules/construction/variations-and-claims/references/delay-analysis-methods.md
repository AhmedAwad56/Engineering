# Delay Analysis Methods

These methods follow the SCL Delay and Disruption Protocol (2nd ed., 2017) and AACE RP 29R-03. Choose the method according to (a) when the analysis is done, (b) the quality of the programme and records, and (c) the value of the claim.

## Contents
1. Method selection
2. Time Impact Analysis (TIA)
3. Windows analysis
4. As-planned vs as-built
5. Impacted as-planned
6. Collapsed as-built
7. Concurrency
8. Float ownership
9. Disruption (measured mile)

## 1. Method selection

| Method | Timing | Needs | Strength | Weakness |
|---|---|---|---|---|
| TIA | Prospective (during the project) | Accepted programme updates, fragnets | Contract-compliant; the SCL default for EOT during a project | Theoretical, since it predicts delay |
| Windows | Retrospective | Regular updated programmes | Tracks the real critical path over time | Needs good-quality updates |
| As-planned vs as-built | Retrospective | Baseline + as-built dates | Simple and factual | Weak at proving causation on complex jobs |
| Impacted as-planned | Either | Baseline only | Cheap | Ignores actual progress and contractor delay, so it's often rejected |
| Collapsed as-built | Retrospective | A detailed as-built programme with logic | Uses actual events | Rebuilding the logic is subjective |

## 2. Time Impact Analysis: steps

1. Take the most recent accepted programme update before the event, with its data date.
2. Create a fragnet: new activities representing the event, with durations and logic ties to the affected activities.
3. Insert the fragnet and reschedule (use `cpm_scheduler.py` in the construction-scheduling skill).
4. The EOT is the shift in the completion date (or Key Date or Section date).
5. Check for float absorption. A delay on an activity with 15 days' total float that is itself 10 days long gives no EOT.
6. Document the assumptions, the fragnet logic and the before and after programmes as exhibits.

## 3. Windows analysis

- Divide the project into windows, for example monthly or between major milestones.
- For each window, compare the critical path and completion date at the start and end of the window.
- Identify which delay events on the critical path caused the slippage in each window, and attribute them to the Employer, the Contractor or a neutral cause.
- Sum the attributions across windows.

## 4. As-planned vs as-built

Compare the planned and actual start and finish dates of activities on the as-built critical path. Explain each variance with the records. This is best used as a supporting method or on simple linear projects.

## 5. Impacted as-planned

Insert only the Employer delay events into the baseline programme. This shows theoretical delay and ignores the Contractor's own progress. Use it only when no updates exist, and acknowledge the weakness.

## 6. Collapsed as-built (but-for)

Build an as-built programme with logic, then remove the Employer delay events. The resulting earlier completion date shows what would have happened "but for" the Employer delays.

## 7. Concurrency

True concurrency means two or more delay events of approximately equal causative potency, one Employer-risk and one Contractor-risk, affecting completion at the same time.

- **SCL Protocol / English law (e.g. Walter Lilly, North Midland):** EOT is granted, but there's no prolongation cost for the concurrent period.
- **Apportionment (e.g. Scotland: City Inn):** time and/or cost is split. Some Middle East civil codes point to apportionment as well.
- **FIDIC 2017 Cl 8.5:** concurrency is dealt with under the rules in the Special Provisions, and if there are none, "as appropriate taking due regard of all relevant circumstances".
- **NEC4:** CEs are assessed on their effect on planned Completion. Contractor delays already reflected in the Accepted Programme reduce the CE's effect.

Always check the governing law. Some civil-law jurisdictions don't enforce contractual time bars strictly, or apply good-faith principles.

## 8. Float ownership

- The SCL default is that float belongs to the project, so the first party to use it benefits.
- NEC4: float other than terminal float is available to whoever needs it first. Terminal float belongs to the Contractor.
- The contract may say otherwise. Check the programme clauses.

## 9. Disruption: measured mile

Compare productivity (output per labour hour) in an unimpacted period or area with productivity in the impacted period for the same activity type:

```
Loss = (Actual hours in impacted period) − (Output in impacted period ÷ unimpacted productivity)
Claim = Lost hours × all-in labour rate (+ plant if applicable)
```

Industry studies such as MCAA factors and Leonard are secondary evidence only. Use them when no measured mile exists.
