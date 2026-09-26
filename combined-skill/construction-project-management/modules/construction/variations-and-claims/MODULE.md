---
name: variations-and-claims
description: Construction variations (change orders), extension of time (EOT) and delay/disruption claims expert: variation valuation, EOT entitlement, delay analysis methods (TIA, windows, as-planned vs as-built, collapsed as-built), concurrency, prolongation cost, head-office overhead formulas (Hudson, Emden, Eichleay), disruption/loss of productivity, and drafting or reviewing claim submissions and responses. Use this skill whenever the user mentions a variation, change order, VO, site instruction with cost/time impact, EOT, delay claim, prolongation, disruption, acceleration, concurrent delay, liquidated damages exposure, compensation event quotation, or needs to write or assess a claim, even if they only describe an event on site and ask "can we claim for this?".
---

# Variations & Claims

Help contractors, consultants and employers turn site events into well-substantiated variations and claims, or assess ones received. A claim succeeds on **entitlement** (a contract clause), **causation** (the event caused the delay or cost) and **quantum** (a properly calculated amount), all supported by contemporaneous records.

## Step 1: Establish the contract basis first

Ask for, or confirm:
- the form of contract and edition, for example FIDIC Red Book 2017, FIDIC 1999, NEC4 ECC or a bespoke contract, and **any particular conditions or amendments**, because bespoke amendments frequently change time bars;
- the event date, when the party became aware of it, and what notices have already been sent.

Then check time bars immediately using the `contract-administration` skill (`notice_tracker.py`). A strong claim can be lost to a missed 28-day notice, so this comes before any analysis.

## Step 2: Entitlement

Map the event to the clause that gives entitlement. The common FIDIC 2017 grounds for EOT are in Cl 8.5:

| Event | FIDIC 2017 | FIDIC 1999 | NEC4 ECC (CE 60.1) |
|---|---|---|---|
| Variation / change | 13 | 13 | 60.1(1) |
| Late drawings or instructions | 1.9 | 1.9 | 60.1(3), (6) |
| Delayed site access | 2.1 | 2.1 | 60.1(2) |
| Unforeseeable physical conditions | 4.12 | 4.12 | 60.1(12) |
| Employer / other contractor delays | 4.6, 8.5(e) | 4.6, 8.4(e) | 60.1(5) |
| Authority delays | 8.6 | 8.5 | Not a standard CE. Possibly 60.1(19) prevention, or via Z-clauses |
| Suspension | 8.9 | 8.9 | 60.1(4) |
| Exceptionally adverse climate | 8.5(c) (time only) | 8.4(c) | 60.1(13), a 1-in-10-year test |
| Exceptional Events / Force Majeure | 18.4 | 19.4 | 60.1(19) |
| Change in Laws | 13.6 | 13.7 | X2 (if selected) |

Clause numbers are for the unamended standard forms. Always verify them against the actual contract.

## Step 3: Causation, using delay analysis

Choose a method that suits the records available and the timing (prospective or retrospective). The SCL Delay and Disruption Protocol (2nd ed.) is the reference point. See `references/delay-analysis-methods.md` for step-by-step guidance on:
- Time Impact Analysis (TIA), which is prospective and preferred for contemporaneous EOT claims;
- windows or watershed analysis;
- as-planned vs as-built;
- impacted as-planned, which is simple but weak for retrospective use;
- collapsed as-built (but-for).

For a TIA, model the event as a fragnet, insert it into the latest accepted programme update, and run it with the `construction-scheduling` skill (`cpm_scheduler.py`) before and after. The movement in the completion date is the EOT.

**Concurrency:** under the SCL Protocol approach, true concurrent delay usually gives EOT but no prolongation cost. Some jurisdictions and contracts apportion instead, and FIDIC 2017 Cl 8.5 defers to the Particular Conditions. State which approach you are using.

## Step 4: Quantum

**Variations** (FIDIC 12.3 / 13.3; NEC 63):
1. Use BOQ rates where the work is of a similar character and executed under similar conditions.
2. Otherwise use rates derived from the BOQ rates.
3. Otherwise build a new rate from cost plus a reasonable profit (FIDIC 2017 uses 5% unless the contract states otherwise).
4. Use daywork only if instructed.

NEC4 values a compensation event on Defined Cost plus Fee, forecast for prospective events, and doesn't use BOQ rates unless Option B/D and agreed.

**Prolongation (time-related costs)** is claimed for compensable delay only. Run:
```bash
python3 scripts/prolongation_cost.py --site-overhead-monthly 185000 --delay-days 64 \
  --contract-sum 42000000 --contract-days 730 --hoohp-pct 7 \
  --company-overhead 9500000 --company-turnover 160000000
```
The script outputs site overheads for the delay period and head-office overhead under the Hudson, Emden and Eichleay formulas, with notes on when each formula is accepted. Actual recorded costs are always better than formulas, so use formulas only when actual loss can't reasonably be proven.

Other heads of claim include disruption (measured-mile productivity comparison), acceleration, financing charges, escalation during the extended period, and extended bond and insurance costs.

## Step 5: Write the submission

Use the structure in `references/claim-structure.md`. The key principles are:
- Keep it factual and chronological, with every statement tied to an exhibit (letter reference, minutes, daily report, photo or programme).
- Avoid adjectives and emotion; engineers and adjudicators respond to evidence.
- Keep entitlement, causation and quantum clearly separated.
- For employer-side assessment, go through the same three tests and state which parts are accepted, rejected or need more particulars.

## Records checklist

Daily reports (labour, plant, weather, work done), instructions and RFIs with response dates, programme updates, progress photos (dated), minutes, correspondence register, cost records, and the timesheets of affected resources. Advise the user to start collecting these from the day the event occurs.

## Files
- `scripts/prolongation_cost.py`: time-related cost and HO overhead formula calculator.
- `references/delay-analysis-methods.md`: delay analysis methods, concurrency and float ownership.
- `references/claim-structure.md`: claim, EOT and variation submission templates, and a response template for the Engineer or Employer.
