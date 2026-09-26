#!/usr/bin/env python3
"""HSE KPI calculator for construction sites.

CSV columns: month,manhours,lti,mtc,rwc,fatalities,lost_days,near_misses,first_aid
  lti = lost time injuries (excluding fatalities), mtc = medical treatment cases,
  rwc = restricted work cases. Blank = 0.

  LTIFR    = LTI (incl. fatalities) x base / manhours      (base default 1,000,000)
  TRIR     = (fatal + LTI + RWC + MTC) x 200,000 / manhours
  Severity = lost days x 1,000,000 / manhours

Usage:
  python3 hse_kpi.py hse.csv [--ltifr-base 1000000] [--json]
"""
import argparse
import csv
import json
import sys

FIELDS = ("manhours", "lti", "mtc", "rwc", "fatalities", "lost_days", "near_misses", "first_aid")


def num(v):
    v = (v or "").replace(",", "").strip()
    return float(v) if v else 0.0


def kpis(t, base):
    mh = t["manhours"]
    lti_all = t["lti"] + t["fatalities"]
    rec = lti_all + t["rwc"] + t["mtc"]
    return {"LTIFR": lti_all * base / mh if mh else None,
            "TRIR": rec * 200000 / mh if mh else None,
            "severity_rate": t["lost_days"] * 1_000_000 / mh if mh else None,
            "recordables": rec,
            "near_miss_per_recordable": (t["near_misses"] / rec) if rec else None}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv")
    ap.add_argument("--ltifr-base", type=float, default=1_000_000)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    rows = []
    with open(a.csv, newline="", encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            r = {k.strip().lower(): v for k, v in r.items() if k}
            try:
                rows.append({"month": (r.get("month") or "").strip(), **{f: num(r.get(f)) for f in FIELDS}})
            except ValueError as e:
                sys.exit(f"Bad number: {e}")
    if not rows:
        sys.exit("No data.")

    cum = {f: 0.0 for f in FIELDS}
    out = []
    lti_free_mh = 0.0
    for r in rows:
        for f in FIELDS:
            cum[f] += r[f]
        # LTI-free man-hours since last LTI/fatality (month granularity)
        lti_free_mh = 0.0 if (r["lti"] + r["fatalities"]) else lti_free_mh + r["manhours"]
        out.append({"month": r["month"], "manhours": r["manhours"], "month_kpi": kpis(r, a.ltifr_base),
                    "cumulative_kpi": kpis(cum, a.ltifr_base), "lti_free_manhours": lti_free_mh})

    total = kpis(cum, a.ltifr_base)
    notes = []
    if cum["manhours"] >= 500_000 and cum["near_misses"] < 10:
        notes.append("Very few near misses for the exposure - likely under-reporting; promote near-miss reporting.")
    if cum["fatalities"]:
        notes.append("Fatality recorded - ensure regulatory notification and independent investigation.")

    if a.json:
        print(json.dumps({"months": out, "cumulative": total, "totals": cum, "notes": notes}, indent=2))
        return

    def g(x, p=2):
        return "-" if x is None else f"{x:.{p}f}"

    print(f"{'Month':<10}{'Man-hours':>12}{'LTI':>5}{'Rec':>5}{'LTIFR':>8}{'TRIR':>7}{'Sev':>8}   {'Cum LTIFR':>9}{'Cum TRIR':>9}{'LTI-free MH':>13}")
    for src, o in zip(rows, out):
        m, c = o["month_kpi"], o["cumulative_kpi"]
        print(f"{o['month']:<10}{o['manhours']:>12,.0f}{int(src['lti'] + src['fatalities']):>5}{int(m['recordables']):>5}"
              f"{g(m['LTIFR']):>8}{g(m['TRIR']):>7}{g(m['severity_rate'], 1):>8}   {g(c['LTIFR']):>9}{g(c['TRIR']):>9}"
              f"{o['lti_free_manhours']:>13,.0f}")
    print(f"\nCumulative: {cum['manhours']:,.0f} man-hours | LTIFR {g(total['LTIFR'])} (per {a.ltifr_base:,.0f}) | "
          f"TRIR {g(total['TRIR'])} (per 200,000) | Severity {g(total['severity_rate'], 1)} | "
          f"Near misses {int(cum['near_misses'])} | First aid {int(cum['first_aid'])}")
    for n in notes:
        print("  - " + n)


if __name__ == "__main__":
    main()
