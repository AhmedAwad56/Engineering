---
name: site-hse-quality
description: Construction site health, safety & environment (HSE) and quality management (QA/QC): method statements and risk assessments (RAMS/JSA), permits to work, toolbox talks, incident reports and investigations, HSE KPIs (LTIFR, TRIR, severity rate), Inspection & Test Plans (ITP), inspection requests, non-conformance reports (NCR), snag lists, daily site reports and quality/HSE plans aligned with ISO 45001, ISO 9001 and ISO 14001. Use this skill whenever the user mentions site safety, HSE, a near miss, accident or incident, lost time injury, risk assessment, method statement, work at height, lifting plan, permit to work, ITP, inspection request, NCR, quality inspection, snagging, daily report or site diary, even if they only describe a site situation and ask what to do.
---

# Site HSE & Quality

Help site teams do the work safely and right the first time, and record it properly. Every template here serves two purposes: it controls the work on the day, and it becomes evidence later for audits, claims or incident investigations.

## HSE

### Method statements & risk assessments (RAMS / JSA)

When drafting a risk assessment:
1. Break the task into steps in the order they happen on site.
2. For each step, list the hazards, who could be harmed, and the controls. Apply the **hierarchy of controls** in order: eliminate → substitute → engineering controls → administrative controls → PPE. PPE is the last line of defence, so a risk assessment that relies mostly on PPE is weak.
3. Score each hazard on a 5×5 matrix (likelihood × severity) before and after controls. The residual risk must be ≤ Medium (≤ 9) before work starts. High residual risk (≥ 15) means the task must be redesigned.
4. Cover the **high-risk activities** explicitly: work at height (over 2 m), lifting operations (lift plan and certified lifting gear), excavations (over 1.2 m: shoring or battering plus a permit), confined spaces, hot work, electrical isolation (LOTO), and work near live traffic or services.

Templates are in `references/hse-templates.md`: RAMS, JSA, permit-to-work checklist, toolbox talk and incident report.

### Incidents

- **Immediate:** make the area safe, give first aid, preserve the scene, and notify as required by local regulation and the contract. FIDIC 4.8 and 6.7 require the Contractor to report accidents; many jurisdictions have 24–72-hour reporting to the authority.
- **Investigation:** establish the facts, then the root cause (use 5 Whys or a fishbone diagram), then corrective and preventive actions with owners and dates. Look for system causes such as planning, supervision and competence, rather than stopping at "worker was careless".

### HSE KPIs

Monthly data (CSV: `month,manhours,lti,mtc,rwc,fatalities,lost_days,near_misses,first_aid`) goes through:
```bash
python3 scripts/hse_kpi.py hse.csv
```
The script outputs the monthly and cumulative LTIFR, TRIR, severity rate, near-miss ratio, and LTI-free man-hours. The standard formulas are:
- **LTIFR** = LTIs × 1,000,000 ÷ man-hours. This is the common base in the UK, Middle East and Australia; some clients use 200,000.
- **TRIR** = (fatalities + LTI + RWC + MTC) × 200,000 ÷ man-hours (OSHA base).
- **Severity rate** = lost days × 1,000,000 ÷ man-hours.

A low or zero near-miss count on a large site usually means under-reporting, not a safe site. Encourage reporting.

## Quality (QA/QC)

### Inspection & Test Plan (ITP)

An ITP lists every inspection and test for a work package, with: activity, reference spec clause, acceptance criteria, frequency, verifying document, and the inspection point for each party:
- **H (Hold):** the work can't proceed without inspection and sign-off.
- **W (Witness):** notify the inspector, who may attend; if they don't, the work proceeds.
- **R (Review):** document review only.
- **S (Surveillance):** random checks.

Place Hold points before any work that becomes inaccessible: rebar before pour, waterproofing before backfill, and services before ceiling close-up.

### Inspection requests (IR / WIR)

Submit with the notice period the contract requires, typically 24 hours. Record the result as Approved, Approved with comments, or Rejected, and give the NCR reference if rejected.

### Non-conformance reports (NCR)

Structure: description of the non-conformance against the requirement (spec, drawing, clause), root cause, proposed disposition (**rework / repair / use-as-is (needs the designer's approval) / reject**), corrective and preventive action, verification and close-out. Track NCR ageing. Open NCRs older than 30 days should be escalated.

### Daily site report

Record the date, weather (morning and afternoon, including rain hours and temperature), manpower by trade (own and subcontractor), plant on site and working or idle, work done by location, materials received, inspections carried out, instructions received, visitors, incidents and near misses, delays or disruptions (with cause), and photos.

Emphasise to the user that daily reports are the most important evidence in any delay or disruption claim, so they should be factual, complete and signed by both parties where possible.

## Files
- `scripts/hse_kpi.py`: HSE statistics calculator.
- `assets/sample_hse.csv`: 6 months of sample data.
- `references/hse-templates.md`: RAMS, JSA, permit, toolbox talk and incident report templates, and the 5×5 risk matrix.
- `references/quality-templates.md`: ITP, inspection request, NCR, snag list and daily report templates.
