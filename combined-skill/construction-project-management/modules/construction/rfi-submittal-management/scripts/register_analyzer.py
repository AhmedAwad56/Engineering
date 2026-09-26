#!/usr/bin/env python3
"""RFI / submittal register analyzer.

CSV columns (header names case-insensitive):
  id,type,discipline,title,date_submitted,date_required,date_responded,status,revision,code,critical
  - type: RFI, MS, SD, MET, ITP ... (free text)
  - status: Open / Closed (blank = Closed if date_responded else Open)
  - code: A/B/C/D review code (submittals)
  - critical: Y/N - affects a critical or near-critical activity

Usage:
  python3 register_analyzer.py register.csv [--today YYYY-MM-DD] [--review-days 14] [--json]
"""
import argparse
import csv
import datetime as dt
import json
import sys
from collections import defaultdict


def d(s):
    s = (s or "").strip()
    if not s:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d-%b-%Y", "%d %b %Y"):
        try:
            return dt.datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    sys.exit(f"Unrecognised date '{s}' (use YYYY-MM-DD)")


def pct(values, p):
    if not values:
        return None
    v = sorted(values)
    k = (len(v) - 1) * p
    lo, hi = int(k), min(int(k) + 1, len(v) - 1)
    return v[lo] + (v[hi] - v[lo]) * (k - lo)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv")
    ap.add_argument("--today")
    ap.add_argument("--review-days", type=int, default=14, help="Contractual review period if no date_required")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    today = dt.date.fromisoformat(a.today) if a.today else dt.date.today()

    rows = []
    with open(a.csv, newline="", encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            r = {k.strip().lower(): (v or "").strip() for k, v in r.items() if k}
            if not r.get("id"):
                continue
            sub, req, resp = d(r.get("date_submitted")), d(r.get("date_required")), d(r.get("date_responded"))
            if not sub:
                sys.exit(f"{r['id']}: date_submitted required")
            due = req or sub + dt.timedelta(days=a.review_days)
            status = (r.get("status") or ("Closed" if resp else "Open")).title()
            is_open = status != "Closed" and not resp
            try:
                rev = int((r.get("revision") or "0").upper().lstrip("R") or 0)
            except ValueError:
                rev = 0
            rows.append({"id": r["id"], "type": (r.get("type") or "?").upper(),
                         "discipline": (r.get("discipline") or "?").upper(), "title": r.get("title", ""),
                         "submitted": sub, "due": due, "responded": resp, "open": is_open,
                         "revision": rev, "code": (r.get("code") or "").upper(),
                         "critical": (r.get("critical") or "").upper().startswith("Y"),
                         "age": ((resp or today) - sub).days,
                         "late_days": ((resp or today) - due).days})
    if not rows:
        sys.exit("Register is empty.")

    open_rows = [x for x in rows if x["open"]]
    buckets = {"0-7": 0, "8-14": 0, "15-28": 0, ">28": 0}
    for x in open_rows:
        b = "0-7" if x["age"] <= 7 else "8-14" if x["age"] <= 14 else "15-28" if x["age"] <= 28 else ">28"
        buckets[b] += 1
    overdue = sorted([x for x in open_rows if x["late_days"] > 0],
                     key=lambda x: (not x["critical"], -x["late_days"]))
    responded_late = [x for x in rows if not x["open"] and x["responded"] and x["late_days"] > 0]

    turn = defaultdict(list)
    for x in rows:
        if x["responded"]:
            turn[(x["type"], x["discipline"])].append(x["age"])
    turnaround = [{"type": t, "discipline": dsc, "n": len(v), "avg_days": sum(v) / len(v),
                   "p90_days": pct(v, 0.9)} for (t, dsc), v in sorted(turn.items())]

    subs = [x for x in rows if x["type"] != "RFI"]
    coded = [x for x in subs if x["code"]]
    first_ok = [x for x in coded if x["revision"] == 0 and x["code"] in ("A", "B")]
    resub = [x for x in subs if x["revision"] >= 1 or x["code"] in ("C", "D")]
    by_disc_resub = defaultdict(lambda: [0, 0])
    for x in subs:
        by_disc_resub[x["discipline"]][1] += 1
        if x["revision"] >= 1 or x["code"] in ("C", "D"):
            by_disc_resub[x["discipline"]][0] += 1
    delay_candidates = [x for x in overdue if x["critical"]] + [x for x in responded_late if x["critical"]]

    res = {"today": today.isoformat(), "total": len(rows), "open": len(open_rows),
           "ageing_open": buckets, "overdue": len(overdue),
           "first_time_approval_rate": (len(first_ok) / len(coded)) if coded else None,
           "resubmission_rate": (len(resub) / len(subs)) if subs else None,
           "resubmission_by_discipline": {k: v[0] / v[1] for k, v in by_disc_resub.items() if v[1]},
           "turnaround": turnaround,
           "overdue_items": [{"id": x["id"], "type": x["type"], "discipline": x["discipline"], "title": x["title"],
                              "due": x["due"].isoformat(), "days_late": x["late_days"], "critical": x["critical"]}
                             for x in overdue],
           "delay_notice_candidates": [x["id"] for x in delay_candidates]}

    if a.json:
        print(json.dumps(res, indent=2))
        return

    print(f"REGISTER STATUS at {today.isoformat()}: {len(rows)} items, {len(open_rows)} open, {len(overdue)} overdue\n")
    print("Open items by age (days): " + "  ".join(f"{k}: {v}" for k, v in buckets.items()))
    if res["first_time_approval_rate"] is not None:
        print(f"First-time approval rate (code A/B at Rev 0): {100 * res['first_time_approval_rate']:.0f}%")
    if res["resubmission_rate"] is not None:
        print(f"Resubmission rate (submittals): {100 * res['resubmission_rate']:.0f}%")
        hi = [f"{k} {100 * v:.0f}%" for k, v in res["resubmission_by_discipline"].items() if v > 0.30]
        if hi:
            print("  Disciplines above 30%: " + ", ".join(hi))
    print("\nTURNAROUND (responded items)")
    print(f"  {'Type':<6}{'Disc':<8}{'N':>4}{'Avg d':>8}{'P90 d':>8}")
    for t in turnaround:
        flag = "  <- exceeds review period" if t["avg_days"] > a.review_days else ""
        print(f"  {t['type']:<6}{t['discipline']:<8}{t['n']:>4}{t['avg_days']:>8.1f}{t['p90_days']:>8.1f}{flag}")
    if overdue:
        print("\nOVERDUE OPEN ITEMS (critical first)")
        for x in overdue:
            print(f"  {'[CRIT] ' if x['critical'] else '       '}{x['id']:<22}{x['discipline']:<6}"
                  f"due {x['due'].isoformat()}  {x['late_days']:>3}d late  {x['title'][:45]}")
    if delay_candidates:
        print("\nDELAY NOTICE CANDIDATES (critical + late): " + ", ".join(res["delay_notice_candidates"]))
        print("  -> Check notice requirements with the contract-administration skill.")


if __name__ == "__main__":
    main()
