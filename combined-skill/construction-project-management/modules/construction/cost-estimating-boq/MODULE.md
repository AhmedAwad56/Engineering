---
name: cost-estimating-boq
description: Construction cost estimating and Bill of Quantities (BOQ) expert: quantity take-off structure, unit rate build-up (labour, material, plant, subcontract), preliminaries, contingency, escalation, overhead & profit, tender pricing and estimate review. Use this skill whenever the user mentions a BOQ / bill of quantities, cost estimate, unit rate, rate analysis, tender price, pricing a project, quantity surveying, QS, cost plan, budget for a building or civil job, markups, contingency, or asks "how much will it cost to build", even if they only paste a list of items with quantities.
---

# Cost Estimating & BOQ

Help estimators and quantity surveyors produce estimates that are traceable (every number has a source), complete (nothing is left out) and correctly marked up.

## Estimate classes

Before pricing, establish which class of estimate is needed, because it sets the expected accuracy and how much contingency is reasonable:

| AACE class | Design maturity | Typical method | Accuracy range |
|---|---|---|---|
| 5 | 0–2% | Cost/m², analogues | −30% / +50% |
| 4 | 1–15% | Elemental / parametric | −20% / +30% |
| 3 | 10–40% | Semi-detailed BOQ | −15% / +20% |
| 2 | 30–75% | Detailed BOQ, unit rates | −10% / +15% |
| 1 | 65–100% | Full take-off, tender | −5% / +10% |

State the class and range in every estimate summary, because a single-point number without a range misleads decision-makers.

## Workflow

1. **Structure the BOQ.** Use the user's measurement standard if one is given: POMI (common in the Middle East), NRM2 (UK), CESMM4 (civil) or MasterFormat/UniFormat (US). Otherwise use sections such as Preliminaries, Substructure, Frame, Upper floors, Roof, External walls, Internal finishes, MEP, External works.
2. **Build up the rates.** For each significant item, calculate:
   ```
   Unit rate = Labour (hrs/unit × all-in hourly cost)
             + Material (qty/unit × price × (1 + waste%))
             + Plant (hrs/unit × hourly rate)
             + Subcontract (quoted rate)
   ```
   Typical waste allowances: concrete 3–5%, rebar 3–5% (plus laps if not measured), blockwork 5%, tiles 7–10%, timber 10–15%.
3. **Price the estimate** with the calculator:
   ```bash
   python3 scripts/boq_estimator.py boq.csv --prelims 10 --contingency 5 --escalation 4 --escalation-months 18 --ohp 8 --vat 5
   ```
   The CSV has columns `section,item,description,unit,qty,rate`. You can replace `rate` with the component columns `labour,material,plant,subcon`, and the script will sum them. See `assets/sample_boq.csv`.
4. **Review the output:**
   - the Pareto list (the roughly 20% of items that make up about 80% of the cost), where the estimating effort should go;
   - flagged items with zero quantity, zero rate or missing units;
   - cost per m² GFA (use `--gfa`) as a benchmark sanity check.

## Markup order

The calculator applies markups in this order. If the user's company does it differently, say so and adjust the percentages:

1. **Direct cost (D)**, the sum of the measured items.
2. **Preliminaries / general conditions:** % of D, typically 8–15%. Use a priced prelims section instead if you have one.
3. **Contingency:** % of (D + prelims). Use 3–5% for a detailed tender or 10–20% for an early estimate. Contingency covers known unknowns; it isn't a place to hide profit.
4. **Escalation:** annual rate applied to half the construction duration, because spending is spread across the period.
5. **Head-office overhead and profit (OH&P):** typically 5–12%.
6. **VAT or sales tax.**

## Estimate review checklist

When reviewing someone else's estimate, check:
- Quantities against the drawings, checking the top 20 items at least.
- Missing scope: temporary works, dewatering, testing and commissioning, as-builts, insurances, bonds, permits, utility connections, design fees (for design-build), and attendance on nominated subcontractors.
- Unit rates against recent tenders or published indices, adjusted for location and date.
- That prelims match the programme duration, since time-related prelims × months must reconcile.
- That the contingency is justified by a risk register, not just a flat percentage.
- Currency and exchange-rate assumptions for imported items.

## Output format

```
## Estimate summary (Class X, accuracy −y% / +z%)
table: Direct cost / Prelims / Contingency / Escalation / OH&P / VAT / TOTAL, plus cost per m²

## Cost by section
## Top cost drivers (Pareto)
## Assumptions & exclusions   <- always include; this is what protects the estimator
## Risks & opportunities
```

## Files
- `scripts/boq_estimator.py`: the BOQ pricing and markup calculator.
- `assets/sample_boq.csv`: a small sample BOQ.
- `references/rate-buildup-guide.md`: worked rate build-ups (concrete, rebar, blockwork) and labour all-in rate composition. Read it when asked to build or check a unit rate.
