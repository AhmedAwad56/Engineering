---
name: earned-value-management
description: Earned Value Management (EVM) and project cost control for construction: PV/EV/AC, CPI, SPI, cost and schedule variance, EAC/ETC/VAC forecasts, TCPI, earned schedule (SPI(t)), S-curves and monthly cost reports. Use this skill whenever the user mentions earned value, EVM, CPI, SPI, planned vs actual, cost overrun, budget at completion, forecast at completion, cost to complete, S-curve, cash flow vs progress, or asks "are we over budget / behind schedule" on a construction or engineering project, even if they only provide columns of planned, earned and actual cost.
---

# Earned Value Management

Turn progress and cost data into an honest picture of where the project stands and where it's heading.

## Inputs you need

| Term | Meaning | Common construction source |
|---|---|---|
| BAC | Budget at Completion | Approved control budget (contract value less margin, or cost budget) |
| PV | Planned Value (BCWS) | Baseline programme cost-loaded S-curve |
| EV | Earned Value (BCWP) | % complete × budget, measured by BOQ quantities installed, not by hours spent |
| AC | Actual Cost (ACWP) | Cost ledger plus accruals for work done but not yet invoiced |

Missing accruals are the most common reason construction EVM gives a falsely good CPI. Ask whether AC includes accrued subcontractor and material costs.

## Workflow

1. Put the cumulative data by period into a CSV with columns `period,pv,ev,ac`. If the figures are per-period rather than cumulative, pass `--incremental`. See `assets/sample_evm.csv`.
2. Run the calculator:
   ```bash
   python3 scripts/evm_calculator.py evm.csv --bac 12500000
   ```
   It outputs CV, SV, CPI, SPI, three EAC methods, ETC, VAC, TCPI and earned schedule metrics (ES, SPI(t), forecast duration) for each period.
3. Interpret the results rather than just reporting numbers:
   - **CPI < 0.95 or SPI < 0.90:** the project needs a recovery plan.
   - **Cumulative CPI rarely improves by more than 10% after 20% complete** (a well-known DoD finding). Treat optimistic forecasts that assume a sudden recovery with scepticism.
   - **SPI converges to 1.0 at the end** even on late projects, which makes classic SPI unreliable after roughly 60% complete. Use SPI(t) from earned schedule instead.
   - **TCPI > 1.10:** the remaining work would need to be performed 10% more efficiently than planned, which is usually unrealistic, so re-forecast.
4. Find the cause. EVM tells you what is happening but not why. Break variances down by trade, section or subcontract, and link them to the causes: productivity, rates, quantities, rework, variations not yet budgeted, or delays.

## Choosing the EAC method

| Method | Formula | Use when |
|---|---|---|
| EAC1 | BAC / CPI | Past cost performance will continue (the typical default) |
| EAC2 | AC + (BAC − EV) | The variance was a one-off; the remaining work goes to budget |
| EAC3 | AC + (BAC − EV) / (CPI × SPI) | Schedule pressure is driving cost (acceleration, overtime) |
| Bottom-up | AC + re-estimated ETC | Late in the project or after major change. This is the most reliable |

Present a range from EAC2 to EAC3 and recommend one of them, explaining why.

## Construction-specific points

- **Approved variations** increase BAC. Pending variations should be shown separately as a risk or opportunity line, not included in BAC.
- **Front-loaded or unbalanced BOQ rates** distort EV if EV is based on contract value. Earn against the internal cost budget.
- **Materials on site:** decide whether they earn value on delivery or on installation, and apply the rule consistently.
- **Measure progress objectively.** Use quantities installed, weighted milestones (for example rebar 40%, formwork 30%, pour 30%) or units completed, not "percentage feels complete".

## Monthly cost report format

```
## Headline: CPI x.xx | SPI x.xx | SPI(t) x.xx | EAC range a–b | VAC c
## Status (RAG) and one-paragraph narrative
## Performance table (current period and cumulative)
## Forecast: EAC methods, recommended EAC, forecast completion (earned schedule)
## Top 5 variances by trade/section, with root cause
## Corrective actions: owner, due date
## Risks / pending variations not in BAC
```

If the user wants an S-curve chart, plot the cumulative PV, EV and AC against period, with BAC and EAC as horizontal reference lines.

## Files
- `scripts/evm_calculator.py`: the EVM and earned schedule calculator (Python 3 standard library).
- `assets/sample_evm.csv`: a 10-month sample.
