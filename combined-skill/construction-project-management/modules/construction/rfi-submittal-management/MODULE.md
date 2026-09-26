---
name: rfi-submittal-management
description: RFI (Request for Information), technical submittal, material approval, shop drawing and document control management for construction projects: drafting RFIs, submittal transmittals, review codes (A/B/C/D), register set-up, ageing and overdue analysis, turnaround KPIs by discipline, resubmission tracking, and linking late responses to delay claims. Use this skill whenever the user mentions an RFI, technical query (TQ), submittal, material submittal, shop drawings, method statement approval, document register, transmittal, consultant review comments, approval status codes, or complains that the consultant is slow to respond, even if they just paste a log or spreadsheet of documents.
---

# RFI & Submittal Management

Good information flow keeps a site moving. Late RFI responses and repeated submittal rejections are two of the most common root causes of construction delay, and the register is the evidence for any later claim.

## Writing a good RFI

A good RFI gets a fast answer because it is easy to answer:

```
RFI No.: [Project]-RFI-[Discipline]-[nnn]      Date:           Required by: [date + reason]
To: [Engineer / Consultant]                    Discipline: STR / ARCH / MEP / CIV
Subject: [Specific: "Conflict: beam B12 level vs duct route at Level 3, grid C/4"]
References: Drawing no./rev, spec section, BOQ item, photos
Question: One clear question per RFI. Describe the conflict or gap factually.
Proposed solution: The Contractor's suggestion, which often halves the response time
Impact if not answered by [date]: The activity affected (programme ID) and whether it is on or near the critical path
Cost/time implication: "None anticipated" / "May constitute a Variation: rights reserved under Sub-Clause 1.9 / 13"
```

Avoid RFIs that ask the consultant to do the Contractor's own coordination, and bundled questions. Say why the "required by" date matters by linking it to the programme; this also supports a FIDIC 1.9 (delayed drawings or instructions) claim later.

## Submittals

**Typical review codes.** These vary by project, so confirm them with the user:

| Code | Meaning | Action |
|---|---|---|
| A | Approved | Proceed |
| B | Approved as noted | Proceed, incorporating the comments; resubmit for record if required |
| C | Revise and resubmit | Don't proceed; resubmit |
| D | Rejected | Don't proceed; a new submittal is required |

**Submittal package checklist:** transmittal; compliance statement (specification clause by clause); technical datasheets; samples or mock-up reference; test certificates; country of origin; warranty; the manufacturer's authorisation; previous approvals on similar projects; and the programme date by which approval is needed to meet procurement lead time.

Most rejections come from missing compliance statements or deviations that aren't declared. Declare deviations openly; hidden deviations cost more later.

## Register analysis

Keep the register as a CSV: `id,type,discipline,title,date_submitted,date_required,date_responded,status,revision,code,critical`. Then run:
```bash
python3 scripts/register_analyzer.py register.csv --today 2026-09-26 --review-days 14
```
The script outputs:
- open items by ageing bucket (0–7, 8–14, 15–28, over 28 days);
- **overdue** items (past `date_required`, or past the contractual review period if none is given), with critical-path items listed first;
- average and 90th-percentile turnaround by discipline and type;
- first-time approval rate and resubmission rate (items at revision ≥ 1 or code C/D);
- a list of candidate items for a delay notice (critical and overdue).

See `assets/sample_register.csv`.

## Turning the analysis into action

- **Weekly meeting agenda:** overdue critical items first, each with an owner and a target date.
- **Escalation letter** for late responses: cite the items, the dates required, the programme activities affected and the clause (FIDIC 1.9 or 4.4 review period; NEC4 13.3 period for reply, where a late reply is CE 60.1(6)). Hand over to `contract-administration` for the notice.
- **Resubmission rate above 30% for a discipline:** review the quality of the Contractor's submissions, or hold a pre-submission meeting with the consultant.
- **Consultant turnaround consistently beyond the contract review period:** this is evidence for an EOT claim (see `variations-and-claims`).

## Numbering convention (suggested)

`[PROJ]-[TYPE]-[DISC]-[NNNN]-[REV]`, for example `TWR-MS-STR-0012-R1`. Types: RFI, MS (material submittal), SD (shop drawing), MET (method statement), ITP, PQ (pre-qualification), SAM (sample).
