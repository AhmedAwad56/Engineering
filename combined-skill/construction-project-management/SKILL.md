---
name: construction-project-management
description: All-in-one project and construction management toolkit with 26 modules. Construction covers CPM scheduling, critical path and float, BOQ cost estimating, earned value (CPI/SPI/EAC), variations and change orders, EOT and delay claims, FIDIC 2017/1999 and NEC4 contract administration, notices and time bars, RFIs and submittals, site HSE (RAMS, incidents, LTIFR) and quality (ITP, NCR, daily reports). Project management covers project plans, risk registers, RACI, status reports, portfolio health, scrum, Jira and Confluence. Commercial and operations covers tenders and RFPs, contracts and SOWs, procurement, subcontractor scorecards, manpower planning, process mapping, meetings, budget variance, lessons learned and what-if scenarios. Use this skill for any construction, engineering or project management question, whether it's a programme, cost, claim, contract clause, site safety or quality issue, tender, status report or project risk, even if the user doesn't name a specific method.
---

# Construction & Project Management Toolkit

This skill bundles 26 modules. **Don't try to answer from this file alone.** Pick the module or modules that match the request, read their `MODULE.md`, and follow them. Each module is self-contained, with its own `scripts/`, `references/` and `assets/`.

## How to use

1. Match the request to one or more modules using the routing table below. Many real questions span two modules. For example, "the consultant is late approving our chiller submittal" involves `rfi-submittal-management` and then `contract-administration`, and possibly `variations-and-claims`.
2. Read `modules/<group>/<module>/MODULE.md` in full before responding.
3. When a module tells you to run a script (`scripts/x.py`) or read a file (`references/y.md`), the path is **relative to that module's folder**. Scripts use only the Python 3 standard library. If Python isn't available, apply the formulas and method described in the MODULE.md by hand and say that you did so.
4. When a module refers to another skill by name (for example "hand over to `contract-administration`"), look that name up in the table below and read that module.

## Routing table

### Construction (`modules/construction/`)

| Module | Use when the user… |
|---|---|
| `construction-scheduling` | has a programme/schedule, activities with predecessors, P6/MS Project, critical path, float, look-ahead, or asks "when will we finish" |
| `cost-estimating-boq` | needs a BOQ priced, a unit rate built up, a tender or cost estimate, markups/contingency, or an estimate reviewed |
| `earned-value-management` | gives planned/earned/actual cost, or asks about CPI, SPI, EAC, cost to complete, S-curves, or being over budget/behind schedule |
| `variations-and-claims` | has a variation/change order, EOT, delay or disruption claim, concurrency, prolongation or head-office overhead, or asks "can we claim?" |
| `contract-administration` | mentions FIDIC, NEC, a sub-clause, the Engineer/PM, notices, time bars, IPCs/payment, DAAB, or needs a contractual letter |
| `rfi-submittal-management` | needs to draft an RFI or submittal, or has a document register, approval codes or slow consultant responses |
| `site-hse-quality` | asks about safety, RAMS/JSA, permits, incidents, LTIFR/TRIR, ITP, inspection requests, NCRs, snagging or daily reports |

### Project management (`modules/project-management/`)

| Module | Use when the user… |
|---|---|
| `senior-pm` | needs a project charter, risk register (EMV/Monte Carlo), RACI, resource plan, portfolio health or executive report |
| `team-communications` | wants a status report, weekly or 3P update, leadership update or incident summary |
| `meeting-analyzer` | provides meeting transcripts for analysis or coaching |
| `scrum-master` | asks about sprints, velocity, retrospectives or agile team health (useful for design/BIM teams) |
| `jira-expert` | is configuring Jira, writing JQL, workflows or dashboards |
| `confluence-expert` | is structuring Confluence spaces or documentation |
| `atlassian-admin` | handles Atlassian users, permissions or SSO |
| `atlassian-templates` | needs Jira/Confluence templates or blueprints |

### Commercial (`modules/commercial/`)

| Module | Use when the user… |
|---|---|
| `rfp-responder` | is responding to a tender/RFP/RFQ/pre-qualification, or making a bid/no-bid decision |
| `contract-and-proposal-writer` | needs a proposal, SOW, general contract or NDA drafted. For FIDIC/NEC administration use `contract-administration` |
| `procurement-optimizer` | wants spend analysis, supplier rationalisation or purchasing-cycle bottlenecks |

### Operations & finance (`modules/operations/`)

| Module | Use when the user… | Construction adaptation |
|---|---|---|
| `vendor-management` | scores or audits vendors or SLAs | subcontractor/supplier performance scorecards |
| `capacity-planner` | plans headcount or utilisation | manpower histograms, staffing plans |
| `process-mapper` | documents a process or finds bottlenecks | IR/MIR/RFI/submittal approval cycles |
| `meetings` | plans agendas or turns notes into actions | progress meetings, minutes and action logs |
| `weekly-review` | closes open loops weekly | the PM's weekly close-out |
| `financial-analyst` | does budget variance, forecasts or DCF | project cash flow, budget vs actual, investment appraisal |
| `postmortem` | runs a lessons-learned review or 5 Whys | project close-out lessons learned, incident root cause |
| `scenario-war-room` | models compound what-if risks | combined delay, cost and resource shocks |

The operations modules were written for software/SaaS businesses. Translate their examples to construction terms (SaaS vendors become subcontractors, ARR becomes cash flow, sprints become look-ahead programmes).

## Principles across all modules

- **Contracts:** clause numbers and periods are for unamended FIDIC/NEC forms. Always ask about or flag Particular Conditions and amendments, and recommend legal advice for high-value disputes, while still giving the substantive answer.
- **Evidence:** in construction, the record is everything. Link advice to documents: daily reports, letters, programmes and registers.
- **Numbers:** use the module's script (or show the formula) rather than doing mental arithmetic on schedules, estimates or EVM.
- **Currency and region:** don't assume USD or Sat–Sun weekends. Ask, or use what the user provides (Fri–Sat weekends are common in the GCC).

Licence: the modules in project-management, commercial and operations come from alirezarezvani/claude-skills (MIT, see THIRD_PARTY_LICENSE). The construction modules are original to this toolkit.
