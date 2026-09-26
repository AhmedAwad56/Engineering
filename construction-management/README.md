# Construction Management Skills

These are custom Claude skills for construction project delivery. Each skill has a `SKILL.md` with the instructions, plus scripts that run with only the Python 3 standard library (no packages to install), sample data and reference material.

| Skill | What it does | Script |
|---|---|---|
| [construction-scheduling](skills/construction-scheduling) | CPM calculation, critical path, float, schedule quality checks (DCMA), look-aheads | `cpm_scheduler.py` |
| [cost-estimating-boq](skills/cost-estimating-boq) | BOQ pricing, rate build-up, markups, Pareto of cost drivers, estimate review | `boq_estimator.py` |
| [earned-value-management](skills/earned-value-management) | CPI/SPI, EAC methods, TCPI, earned schedule, monthly cost report | `evm_calculator.py` |
| [variations-and-claims](skills/variations-and-claims) | Variations, EOT, delay analysis (TIA/windows), concurrency, prolongation and HO overhead | `prolongation_cost.py` |
| [contract-administration](skills/contract-administration) | FIDIC 2017/1999 and NEC4 notices, time bars, payment cycle, contractual letters | `notice_tracker.py` |
| [rfi-submittal-management](skills/rfi-submittal-management) | RFI/submittal drafting, review codes, register ageing and turnaround KPIs | `register_analyzer.py` |
| [site-hse-quality](skills/site-hse-quality) | RAMS/JSA, permits, incidents, LTIFR/TRIR, ITP, NCR, daily reports | `hse_kpi.py` |

## How the skills connect

```
RFI / submittal late ──► contract-administration (notice, time bar)
                               │
site event ───────────────────►├──► variations-and-claims ──► construction-scheduling (TIA fragnet)
                               │                          └─► cost-estimating-boq (rates, prelims)
progress + cost ──► earned-value-management ──► monthly report
daily reports / NCRs (site-hse-quality) ──► evidence for claims
```

## Quick start

Try any script on its sample data:

```bash
python3 skills/construction-scheduling/scripts/cpm_scheduler.py skills/construction-scheduling/assets/sample_activities.csv --start 2026-10-04 --weekend Fri,Sat
python3 skills/cost-estimating-boq/scripts/boq_estimator.py skills/cost-estimating-boq/assets/sample_boq.csv --prelims 10 --contingency 5 --ohp 8 --vat 5 --gfa 9500
python3 skills/earned-value-management/scripts/evm_calculator.py skills/earned-value-management/assets/sample_evm.csv --bac 12500000
python3 skills/contract-administration/scripts/notice_tracker.py skills/contract-administration/assets/sample_events.csv --today 2026-09-26
python3 skills/rfi-submittal-management/scripts/register_analyzer.py skills/rfi-submittal-management/assets/sample_register.csv --today 2026-09-26
python3 skills/site-hse-quality/scripts/hse_kpi.py skills/site-hse-quality/assets/sample_hse.csv
```

On Windows, use `python` or `py` instead of `python3`.

## Important

The contract periods and clause references are for the **unamended** FIDIC and NEC4 standard forms. Particular Conditions and Z clauses often change them, so always check the actual contract. These skills support professional judgment; they don't replace legal advice.
