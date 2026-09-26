---
name: contract-administration
description: Construction contract administration under FIDIC (2017 and 1999 Red/Yellow/Silver) and NEC4 ECC: notices and time bars, Engineer's / Project Manager's instructions, determinations, payment applications and certificates (IPC), programme submissions, early warnings, compensation events, DAAB/adjudication steps, taking-over and final account, plus drafting contractual letters. Use this skill whenever the user mentions FIDIC, NEC, a sub-clause number, the Engineer or Project Manager, a contractual notice or letter, time bar, interim payment, retention, performance security, taking-over certificate, defects notification period, DAAB/DAB, or asks "what does the contract say / what is the deadline / how should we reply", even if they don't name the contract form.
---

# Contract Administration (FIDIC / NEC4)

Keep the project contractually compliant: the right notice, to the right person, under the right clause, before the deadline. Many construction disputes turn on procedure rather than merit, so good administration is how parties protect value.

## First, identify the contract

Confirm the form, edition and amendments. The Particular Conditions (FIDIC) or Z clauses (NEC) override the standard form, and bespoke amendments frequently change time bars. If you don't know the amendments, say so and present standard-form answers as a default for the user to verify.

| Form | Administrator | Main claims clause | Dispute route |
|---|---|---|---|
| FIDIC 2017 Red/Yellow/Silver | Engineer (Silver: Employer's Representative) | 20.2 (both parties) | 3.7 → DAAB 21.4 → amicable 21.5 → arbitration 21.6 |
| FIDIC 1999 Red/Yellow | Engineer | 20.1 (Contractor); 2.5 (Employer) | DAB 20.4 → amicable 20.5 → arbitration 20.6 |
| NEC4 ECC | Project Manager + Supervisor | 60–66 compensation events | Option W1/W2 adjudication → tribunal (W3 for dispute avoidance) |

Reference details for each form are in:
- `references/fidic-2017.md`: the key obligations and periods, and what's new compared with 1999.
- `references/nec4-ecc.md`: the key periods, the CE process, early warnings, programme rules and main Option differences.

Read only the reference file for the contract in question.

## Deadline tracking

Keep an event log (CSV: `id,contract,event_type,trigger_date,done_date,description`) and run:
```bash
python3 scripts/notice_tracker.py events.csv --today 2026-09-26
python3 scripts/notice_tracker.py --list        # event types per contract
```
The tracker calculates every resulting deadline, including the knock-on steps (for example Notice of Claim → Fully Detailed Claim → Engineer's determination → NOD → DAAB). It flags items as **OVERDUE** or **DUE SOON** and says what happens if each one is missed. For amended contracts, pass a `--rules custom.json` override. See `assets/sample_events.csv`.

When items are overdue, advise on the next step. For example, if a FIDIC 2017 Notice of Claim is late, argue under 20.2.5 that the Engineer should waive the late notice (the relevant circumstances include prejudice to the other party and prior knowledge), and send the notice immediately anyway.

## Drafting contractual letters

Every contractual letter should:
1. **Quote the clause** it's issued under in the subject line.
2. **State the facts** briefly with dates and references.
3. **State the contractual consequence or request** clearly: "This is a Notice under Sub-Clause 20.2.1", "We request the Engineer's instruction under 1.9", or "We notify a compensation event under clause 61.3".
4. **Reserve rights** without over-using boilerplate.
5. **Comply with the communication requirements** (FIDIC 1.3; NEC4 13): in writing, to the named address, and identified as a Notice where required. Under FIDIC 2017, a Notice must be identified as a Notice and can't be buried in progress reports.

Keep letters short and neutral in tone. Someone who wasn't on the project should be able to read the letter in two years' time and understand it.

## Payment cycle (typical)

- **FIDIC:** Statement (14.3) monthly → IPC within 28 days (14.6) → payment within 56 days of the Statement (14.7). Retention is deducted per the Contract Data, with half released at taking-over (14.9). Advance payment is recovered by instalments (14.2).
- **NEC4:** assessment at each assessment date (≤ 5 weeks apart), PM certifies within 1 week (50–51), and payment is due within 3 weeks of the assessment date. Under Options A/B the Price for Work Done to Date is based on the activity schedule or BOQ; under C/D/E it is Defined Cost + Fee.

When reviewing a payment application or certificate, reconcile the previous certified amount, work done this period, variations, materials on site, retention, advance recovery, contra-charges and delay damages, and explain every difference.

## Registers to maintain

Correspondence (in/out), notices and claims (use the tracker), instructions/variations, RFIs and submittals (see the `rfi-submittal-management` skill), early warnings / risk register (NEC), payment, programme submissions, and the defects list.

## Hand-offs
- Claim analysis and quantum → `variations-and-claims`
- Programme questions → `construction-scheduling`
- Drafting NDAs, SOWs and general contracts → `contract-and-proposal-writer`

Note: you are not a lawyer. For disputes of significant value or questions of governing law, recommend that the user takes legal advice, but still give them the substantive standard-form answer.
