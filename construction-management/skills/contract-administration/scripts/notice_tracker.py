#!/usr/bin/env python3
"""Contract notice & time-bar tracker for FIDIC 2017, FIDIC 1999 and NEC4 ECC.

Each event you log triggers one or more contractual deadlines. The tracker
computes due dates and flags OVERDUE / DUE SOON items.

CSV columns: id,contract,event_type,trigger_date,done_date,description
  contract:   FIDIC2017 | FIDIC1999 | NEC4
  event_type: see --list
  done_date:  optional - date the resulting action was completed
              (applies to the FIRST obligation of the event, usually the notice)

Rules are for UNAMENDED standard forms. Amended contracts: pass --rules custom.json
with the same structure as RULES below (it is merged over the defaults).

Usage:
  python3 notice_tracker.py events.csv [--today 2026-09-26] [--soon 7] [--rules x.json] [--json]
  python3 notice_tracker.py --list
"""
import argparse
import csv
import datetime as dt
import json
import sys

# (obligation, days, party responsible, clause, consequence if missed)
RULES = {
    "FIDIC2017": {
        "claim_event": [
            ["Notice of Claim", 28, "Claiming Party", "20.2.1", "TIME-BARRED: no entitlement to EOT / payment"],
            ["Fully detailed Claim", 84, "Claiming Party", "20.2.4", "Notice of Claim deemed lapsed unless Engineer/DAAB decides otherwise"]],
        "fully_detailed_claim_received": [
            ["Engineer: agreement or determination", 42, "Engineer", "3.7.3", "Deemed rejection; either Party may refer to DAAB"]],
        "engineer_determination": [
            ["Notice of Dissatisfaction (NOD) with determination", 28, "Either Party", "3.7.5", "Determination becomes final and binding"]],
        "nod_on_determination": [
            ["Refer dispute to DAAB", 42, "Dissatisfied Party", "21.4.1", "NOD deemed lapsed / no longer valid"]],
        "daab_referral": [
            ["DAAB decision", 84, "DAAB", "21.4.3", "Either Party may give NOD (21.4.4)"]],
        "daab_decision": [
            ["NOD with DAAB decision", 28, "Either Party", "21.4.4", "DAAB decision becomes final and binding"]],
        "nod_on_daab_decision": [
            ["Amicable settlement period ends (arbitration may commence)", 28, "Both Parties", "21.5", "Arbitration may start on/after this date"]],
        "variation_instruction": [
            ["Contractor's Variation proposal / particulars", 28, "Contractor", "13.3.1", "Engineer may proceed to value; weakens Contractor position"]],
        "statement_submitted": [
            ["Engineer issues IPC", 28, "Engineer", "14.6", "Contractor may give notice / suspend (16.1) after further notice"],
            ["Employer pays IPC", 56, "Employer", "14.7(b)", "Financing charges (14.8); suspension/termination rights"]],
        "commencement_date": [
            ["Initial programme", 28, "Contractor", "8.3", "Breach; Engineer may withhold / Contractor loses programme protections"]],
        "programme_submitted": [
            ["Engineer's Notice on programme compliance", 21, "Engineer", "8.3", "Programme deemed compliant (Contractor proceeds per it)"]],
        "taking_over_certificate": [
            ["Statement at Completion", 84, "Contractor", "14.10", "Payment delay; claims risk"]],
        "performance_certificate": [
            ["Draft Final Statement", 56, "Contractor", "14.11", "Engineer may prepare / payment delay"]],
    },
    "FIDIC1999": {
        "claim_event": [
            ["Notice of claim", 28, "Contractor", "20.1", "TIME-BARRED: Employer discharged from liability"],
            ["Fully detailed claim", 42, "Contractor", "20.1", "Claim may be reduced for prejudice (20.1 last para)"]],
        "detailed_claim_received": [
            ["Engineer approves/disapproves with comments", 42, "Engineer", "20.1", "Contractor may refer to DAB"]],
        "dab_referral": [
            ["DAB decision", 84, "DAB", "20.4", "Either Party may give NOD"]],
        "dab_decision": [
            ["Notice of dissatisfaction with DAB decision", 28, "Either Party", "20.4", "DAB decision final and binding"]],
        "nod_on_dab_decision": [
            ["Amicable settlement period ends (arbitration may commence)", 56, "Both Parties", "20.5", "Arbitration may start on/after this date"]],
        "statement_submitted": [
            ["Engineer issues IPC", 28, "Engineer", "14.6", "Contractor rights under 16.1"],
            ["Employer pays IPC", 56, "Employer", "14.7(b)", "Financing charges (14.8)"]],
        "commencement_date": [
            ["Programme", 28, "Contractor", "8.3", "Breach"]],
        "programme_submitted": [
            ["Engineer notice of non-compliance", 21, "Engineer", "8.3", "Contractor proceeds per programme"]],
        "taking_over_certificate": [
            ["Statement at Completion", 84, "Contractor", "14.10", "Payment delay"]],
        "performance_certificate": [
            ["Draft final statement", 56, "Contractor", "14.11", "Payment delay"]],
    },
    "NEC4": {
        "compensation_event": [
            ["Contractor notifies compensation event", 56, "Contractor", "61.3", "TIME-BARRED unless PM should have notified it"]],
        "ce_notified_by_contractor": [
            ["PM replies (is/is not a CE)", 7, "Project Manager", "61.4", "Contractor may notify failure; deemed accepted 2 weeks after that"]],
        "quotation_instructed": [
            ["Contractor submits quotation", 21, "Contractor", "62.3", "PM may assess the CE itself (64.1)"]],
        "quotation_submitted": [
            ["PM reply to quotation", 14, "Project Manager", "62.3", "Contractor may notify failure; deemed accepted 2 weeks after (62.6)"]],
        "pm_failure_notified": [
            ["Deemed acceptance if PM still silent", 14, "Project Manager", "61.4 / 62.6 / 64.4", "Notification/quotation treated as accepted"]],
        "programme_submitted": [
            ["PM accepts or gives reasons for not accepting", 14, "Project Manager", "31.3", "Contractor may notify failure; deemed accepted 1 week after (31.3)"]],
        "assessment_date": [
            ["PM certifies payment", 7, "Project Manager", "51.1", "Late certification; interest (51.3)"],
            ["Client pays", 21, "Client", "51.2", "Interest on late payment (51.3)"]],
    },
}


def parse_date(s, field, ref):
    if not s:
        return None
    try:
        return dt.date.fromisoformat(s.strip())
    except ValueError:
        sys.exit(f"Event {ref}: invalid {field} '{s}' (use YYYY-MM-DD)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv", nargs="?")
    ap.add_argument("--today", default=None)
    ap.add_argument("--soon", type=int, default=7, help="Days ahead to flag as DUE SOON")
    ap.add_argument("--rules", help="JSON file with custom/amended rules merged over defaults")
    ap.add_argument("--list", action="store_true", help="List contracts and event types")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    rules = {k: dict(v) for k, v in RULES.items()}
    if a.rules:
        with open(a.rules, encoding="utf-8") as fh:
            for c, evs in json.load(fh).items():
                rules.setdefault(c.upper(), {}).update(evs)

    if a.list:
        for c, evs in rules.items():
            print(c)
            for e, obs in evs.items():
                print(f"  {e:<32}" + "; ".join(f"{o[0]} ({o[1]}d, cl {o[3]})" for o in obs))
        return
    if not a.csv:
        ap.error("events CSV required (or --list)")

    today = dt.date.fromisoformat(a.today) if a.today else dt.date.today()
    items = []
    with open(a.csv, newline="", encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            r = {k.strip().lower(): (v or "").strip() for k, v in r.items() if k}
            ref = r.get("id") or "?"
            c = r.get("contract", "").upper().replace(" ", "").replace("-", "")
            ev = r.get("event_type", "").lower()
            if c not in rules:
                sys.exit(f"Event {ref}: unknown contract '{r.get('contract')}' (use {', '.join(rules)})")
            if ev not in rules[c]:
                sys.exit(f"Event {ref}: unknown event_type '{ev}' for {c}. Run --list.")
            trig = parse_date(r.get("trigger_date"), "trigger_date", ref)
            if not trig:
                sys.exit(f"Event {ref}: trigger_date required")
            done = parse_date(r.get("done_date"), "done_date", ref)
            for n, (obl, days, party, clause, conseq) in enumerate(rules[c][ev]):
                due = trig + dt.timedelta(days=days)
                d = done if n == 0 else None
                if d:
                    status = "DONE" if d <= due else "DONE LATE"
                elif today > due:
                    status = "OVERDUE"
                elif (due - today).days <= a.soon:
                    status = "DUE SOON"
                else:
                    status = "OPEN"
                items.append({"id": ref, "contract": c, "event": ev, "description": r.get("description", ""),
                              "obligation": obl, "party": party, "clause": clause, "trigger": trig.isoformat(),
                              "due": due.isoformat(), "days_left": (due - today).days,
                              "done": d.isoformat() if d else None, "status": status,
                              "if_missed": conseq})

    order = {"OVERDUE": 0, "DONE LATE": 1, "DUE SOON": 2, "OPEN": 3, "DONE": 4}
    items.sort(key=lambda x: (order[x["status"]], x["due"]))

    if a.json:
        print(json.dumps({"today": today.isoformat(), "items": items}, indent=2))
        return

    print(f"Notice & time-bar register as at {today.isoformat()}  (standard-form periods; verify amendments)\n")
    print(f"{'Status':<10}{'Due':<12}{'Left':>5}  {'ID':<8}{'Clause':<10}{'Party':<17}Obligation")
    print("-" * 110)
    for i in items:
        left = "" if i["status"].startswith("DONE") else str(i["days_left"])
        print(f"{i['status']:<10}{i['due']:<12}{left:>5}  {i['id']:<8}{i['contract'][:5] + ' ' + i['clause']:<10}"
              f"{i['party'][:16]:<17}{i['obligation']}")
        if i["status"] in ("OVERDUE", "DUE SOON", "DONE LATE"):
            print(f"{'':<37}-> {i['description'][:60]}")
            print(f"{'':<37}   If missed: {i['if_missed']}")


if __name__ == "__main__":
    main()
