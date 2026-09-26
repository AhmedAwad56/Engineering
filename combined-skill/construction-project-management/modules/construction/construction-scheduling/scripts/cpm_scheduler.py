#!/usr/bin/env python3
"""CPM scheduler for construction programmes.

Input CSV columns: id,name,duration,predecessors
  predecessors: ';'-separated list. Each entry: ID[:TYPE][+/-LAG]
  TYPE in FS (default), SS, FF, SF. LAG in working days.
  Activity IDs must not contain ':', '+', '-' or spaces (use A10, not A-10).
  Examples: "A"  "A;B"  "A:SS+2"  "B:FF-1"  "C:FS+5"

Outputs ES/EF/LS/LF, total float, free float, critical path, logic warnings.
Durations and floats are in working days. Optional --start converts to dates.

Usage:
  python3 cpm_scheduler.py activities.csv [--start YYYY-MM-DD]
         [--weekend Sat,Sun] [--holidays YYYY-MM-DD,...] [--json]
"""
import argparse
import csv
import datetime as dt
import json
import re
import sys
from collections import defaultdict, deque

PRED_RE = re.compile(r"^\s*([^:+\-\s]+)\s*(?::\s*(FS|SS|FF|SF))?\s*([+-]\s*\d+(?:\.\d+)?)?\s*$", re.I)
DAYS = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}


def parse_preds(text, act_id):
    preds = []
    if not text or not text.strip():
        return preds
    for part in text.split(";"):
        if not part.strip():
            continue
        m = PRED_RE.match(part)
        if not m:
            sys.exit(f"Activity {act_id}: cannot parse predecessor '{part}'")
        pid, rtype, lag = m.groups()
        preds.append({"id": pid.strip(), "type": (rtype or "FS").upper(),
                      "lag": float(lag.replace(" ", "")) if lag else 0.0})
    return preds


def load(path):
    acts = {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            row = {k.strip().lower(): (v or "").strip() for k, v in row.items() if k}
            aid = row.get("id")
            if not aid:
                continue
            if aid in acts:
                sys.exit(f"Duplicate activity id: {aid}")
            try:
                dur = float(row.get("duration") or 0)
            except ValueError:
                sys.exit(f"Activity {aid}: invalid duration '{row.get('duration')}'")
            acts[aid] = {"id": aid, "name": row.get("name", ""), "duration": dur,
                         "preds": parse_preds(row.get("predecessors", ""), aid)}
    if not acts:
        sys.exit("No activities found.")
    return acts


def topo_order(acts, succs):
    indeg = {a: 0 for a in acts}
    for a in acts.values():
        for p in a["preds"]:
            indeg[a["id"]] += 1
    q = deque(sorted(a for a, d in indeg.items() if d == 0))
    order = []
    while q:
        n = q.popleft()
        order.append(n)
        for s in succs[n]:
            indeg[s["id"]] -= 1
            if indeg[s["id"]] == 0:
                q.append(s["id"])
    if len(order) != len(acts):
        loop = sorted(a for a, d in indeg.items() if d > 0)
        sys.exit("Logic loop detected involving: " + ", ".join(loop))
    return order


def compute(acts):
    succs = defaultdict(list)
    for a in acts.values():
        for p in a["preds"]:
            if p["id"] not in acts:
                sys.exit(f"Activity {a['id']}: unknown predecessor '{p['id']}'")
            succs[p["id"]].append({"id": a["id"], "type": p["type"], "lag": p["lag"]})
    order = topo_order(acts, succs)

    # Forward pass
    for aid in order:
        a = acts[aid]
        d = a["duration"]
        es = 0.0
        for p in a["preds"]:
            pr = acts[p["id"]]
            t, lag = p["type"], p["lag"]
            if t == "FS":
                c = pr["EF"] + lag
            elif t == "SS":
                c = pr["ES"] + lag
            elif t == "FF":
                c = pr["EF"] + lag - d
            else:  # SF
                c = pr["ES"] + lag - d
            es = max(es, c)
        a["ES"], a["EF"] = es, es + d

    finish = max(a["EF"] for a in acts.values())

    # Backward pass
    for aid in reversed(order):
        a = acts[aid]
        d = a["duration"]
        lf = finish
        for s in succs[aid]:
            sa = acts[s["id"]]
            t, lag = s["type"], s["lag"]
            if t == "FS":
                c = sa["LS"] - lag
            elif t == "SS":
                c = sa["LS"] - lag + d
            elif t == "FF":
                c = sa["LF"] - lag
            else:  # SF
                c = sa["LF"] - lag + d
            lf = min(lf, c)
        a["LF"], a["LS"] = lf, lf - d
        a["TF"] = a["LS"] - a["ES"]

    # Free float
    for aid in order:
        a = acts[aid]
        ff = finish - a["EF"]
        for s in succs[aid]:
            sa = acts[s["id"]]
            t, lag = s["type"], s["lag"]
            if t == "FS":
                slack = sa["ES"] - lag - a["EF"]
            elif t == "SS":
                slack = sa["ES"] - lag - a["ES"]
            elif t == "FF":
                slack = sa["EF"] - lag - a["EF"]
            else:
                slack = sa["EF"] - lag - a["ES"]
            ff = min(ff, slack)
        a["FF"] = max(ff, 0.0)
        a["critical"] = a["TF"] <= 1e-9
    return order, succs, finish


def warnings(acts, succs):
    w = []
    n_rel = sum(len(a["preds"]) for a in acts.values())
    no_pred = [a for a in acts if not acts[a]["preds"]]
    no_succ = [a for a in acts if not succs[a]]
    if len(no_pred) > 1:
        w.append(("Open start (no predecessor)", no_pred,
                  "Only the start milestone should lack a predecessor; others float freely."))
    if len(no_succ) > 1:
        w.append(("Open end (no successor)", no_succ,
                  "Only the finish milestone should lack a successor; delays here won't drive completion."))
    leads = [a["id"] for a in acts.values() for p in a["preds"] if p["lag"] < 0]
    if leads:
        w.append(("Negative lag (lead)", sorted(set(leads)),
                  "Leads hide overlap assumptions; replace with SS logic or split activities."))
    lags = [a["id"] for a in acts.values() for p in a["preds"] if p["lag"] > 0]
    if n_rel and len(lags) / n_rel > 0.05:
        w.append(("Lags on > 5% of relationships", sorted(set(lags)),
                  "Lags are unexplained time; model curing/approval periods as activities."))
    non_fs = sum(1 for a in acts.values() for p in a["preds"] if p["type"] != "FS")
    if n_rel and non_fs / n_rel > 0.10:
        w.append(("Less than 90% FS relationships", [f"{non_fs}/{n_rel} non-FS"],
                  "Heavy SS/FF use usually signals under-developed logic."))
    long_ = [a["id"] for a in acts.values() if a["duration"] > 20]
    if long_:
        w.append(("Duration > 20 working days", long_,
                  "Hard to progress objectively; split by zone/level."))
    high = [a["id"] for a in acts.values() if a["TF"] > 44]
    if high:
        w.append(("Total float > 44 days", high, "Often indicates missing successor logic."))
    # Finish of an activity not driven by anything (only SS/SF predecessors) = dangling finish
    dangling = [a["id"] for a in acts.values()
                if a["preds"] and a["duration"] > 0
                and all(p["type"] in ("SS", "SF") for p in a["preds"])
                and all(s["type"] in ("SS", "SF") for s in succs[a["id"]])]
    if dangling:
        w.append(("Dangling finish (start-linked only)", dangling,
                  "Nothing drives or depends on the finish; an overrun would not show on the critical path."))
    return w


def workday_calendar(start, weekend, holidays, n):
    days, d = [], start
    while len(days) < n + 2:
        if d.weekday() not in weekend and d not in holidays:
            days.append(d)
        d += dt.timedelta(days=1)
    return days


def fmt(x):
    return str(int(x)) if abs(x - round(x)) < 1e-9 else f"{x:.1f}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv")
    ap.add_argument("--start", help="Project start date YYYY-MM-DD (first working day on/after)")
    ap.add_argument("--weekend", default="Sat,Sun", help="Non-working weekdays, e.g. Fri,Sat")
    ap.add_argument("--holidays", default="", help="Comma-separated YYYY-MM-DD dates")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    acts = load(args.csv)
    order, succs, finish = compute(acts)

    cal = None
    if args.start:
        weekend = {DAYS[x.strip().lower()[:3]] for x in args.weekend.split(",") if x.strip()}
        hols = {dt.date.fromisoformat(h.strip()) for h in args.holidays.split(",") if h.strip()}
        cal = workday_calendar(dt.date.fromisoformat(args.start), weekend, hols, int(finish) + 1)

    def start_date(es):
        return cal[int(es)].isoformat() if cal else None

    def finish_date(ef, d):
        if not cal:
            return None
        idx = int(ef) - 1 if d > 0 else int(ef)
        return cal[max(idx, 0)].isoformat()

    rows = []
    for aid in sorted(order, key=lambda x: (acts[x]["ES"], acts[x]["EF"], x)):
        a = acts[aid]
        rows.append({"id": aid, "name": a["name"], "duration": a["duration"],
                     "ES": a["ES"], "EF": a["EF"], "LS": a["LS"], "LF": a["LF"],
                     "TF": a["TF"], "FF": a["FF"], "critical": a["critical"],
                     "early_start_date": start_date(a["ES"]),
                     "early_finish_date": finish_date(a["EF"], a["duration"])})
    crit = [r["id"] for r in rows if r["critical"]]
    near = [r["id"] for r in rows if not r["critical"] and r["TF"] <= 10]
    warns = warnings(acts, succs)

    result = {"project_duration_working_days": finish,
              "finish_date": finish_date(finish, 1) if cal else None,
              "critical_path": crit, "near_critical_tf_le_10": near,
              "activities": rows,
              "warnings": [{"issue": i, "activities": a, "why": y} for i, a, y in warns]}
    if args.json:
        print(json.dumps(result, indent=2))
        return

    print(f"Project duration: {fmt(finish)} working days"
          + (f"  |  Start {cal[0].isoformat()}  Finish {result['finish_date']}" if cal else ""))
    print()
    hdr = f"{'ID':<8}{'Name':<32}{'Dur':>5}{'ES':>6}{'EF':>6}{'LS':>6}{'LF':>6}{'TF':>6}{'FF':>6}  Crit"
    if cal:
        hdr += "  Start       Finish"
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        line = (f"{r['id']:<8}{r['name'][:31]:<32}{fmt(r['duration']):>5}{fmt(r['ES']):>6}{fmt(r['EF']):>6}"
                f"{fmt(r['LS']):>6}{fmt(r['LF']):>6}{fmt(r['TF']):>6}{fmt(r['FF']):>6}  {'*' if r['critical'] else ' '}   ")
        if cal:
            line += f"  {r['early_start_date']}  {r['early_finish_date']}"
        print(line)
    print()
    print("Critical path: " + " -> ".join(crit))
    if near:
        print("Near-critical (TF <= 10d): " + ", ".join(near))
    if warns:
        print("\nLogic warnings:")
        for i, a, y in warns:
            print(f"  - {i}: {', '.join(map(str, a))}\n      {y}")


if __name__ == "__main__":
    main()
