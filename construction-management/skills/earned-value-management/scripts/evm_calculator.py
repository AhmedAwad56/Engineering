#!/usr/bin/env python3
"""Earned Value + Earned Schedule calculator.

CSV columns: period,pv,ev,ac  (cumulative by default; --incremental if per-period)
  Rows with blank ev/ac are treated as future periods (PV baseline only).

Usage:
  python3 evm_calculator.py evm.csv --bac 12500000 [--incremental] [--json]
"""
import argparse
import csv
import json
import sys


def f(v):
    v = (v or "").replace(",", "").strip()
    return float(v) if v else None


def load(path, incremental):
    rows = []
    with open(path, newline="", encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            r = {k.strip().lower(): (v or "").strip() for k, v in r.items() if k}
            try:
                rows.append({"period": r.get("period", str(len(rows) + 1)),
                             "pv": f(r.get("pv")) or 0.0, "ev": f(r.get("ev")), "ac": f(r.get("ac"))})
            except ValueError as e:
                sys.exit(f"Bad number in row {len(rows) + 2}: {e}")
    if not rows:
        sys.exit("No data rows.")
    if incremental:
        cpv = cev = cac = 0.0
        for r in rows:
            cpv += r["pv"]
            r["pv"] = cpv
            if r["ev"] is not None:
                cev += r["ev"]
                r["ev"] = cev
            if r["ac"] is not None:
                cac += r["ac"]
                r["ac"] = cac
    return rows


def div(a, b):
    return a / b if b else None


def earned_schedule(pv_series, ev):
    """ES in periods: C + (EV - PV_C)/(PV_{C+1} - PV_C), PV_0 = 0."""
    pv = [0.0] + pv_series
    c = 0
    for i in range(1, len(pv)):
        if pv[i] <= ev + 1e-9:
            c = i
        else:
            break
    if c >= len(pv) - 1:
        return float(c)
    step = pv[c + 1] - pv[c]
    return c + ((ev - pv[c]) / step if step else 0.0)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv")
    ap.add_argument("--bac", type=float, help="Budget at completion (default: final cumulative PV)")
    ap.add_argument("--incremental", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    rows = load(a.csv, a.incremental)
    pv_series = [r["pv"] for r in rows]
    bac = a.bac if a.bac else pv_series[-1]
    # Planned duration = first period where cumulative PV reaches BAC
    pd = next((i + 1 for i, v in enumerate(pv_series) if v >= bac - 1e-6), len(pv_series))

    out = []
    for idx, r in enumerate(rows, start=1):
        if r["ev"] is None or r["ac"] is None:
            continue
        pv, ev, ac = r["pv"], r["ev"], r["ac"]
        cpi, spi = div(ev, ac), div(ev, pv)
        es = earned_schedule(pv_series, ev)
        spit = div(es, idx)
        m = {"period": r["period"], "PV": pv, "EV": ev, "AC": ac,
             "CV": ev - ac, "SV": ev - pv, "CPI": cpi, "SPI": spi,
             "pct_complete": 100 * ev / bac if bac else None,
             "pct_spent": 100 * ac / bac if bac else None,
             "EAC1_BAC_over_CPI": div(bac, cpi) if cpi else None,
             "EAC2_AC_plus_remaining": ac + (bac - ev),
             "EAC3_CPI_x_SPI": ac + div(bac - ev, (cpi or 0) * (spi or 0)) if cpi and spi else None,
             "TCPI_to_BAC": div(bac - ev, bac - ac),
             "ES_periods": es, "SV_t_periods": es - idx, "SPI_t": spit,
             "forecast_duration_periods": div(pd, spit) if spit else None}
        m["ETC_EAC1"] = m["EAC1_BAC_over_CPI"] - ac if m["EAC1_BAC_over_CPI"] else None
        m["VAC_EAC1"] = bac - m["EAC1_BAC_over_CPI"] if m["EAC1_BAC_over_CPI"] else None
        out.append(m)

    if not out:
        sys.exit("No periods with both EV and AC.")
    last = out[-1]

    def rag(cpi, spi):
        vals = [x for x in (cpi, spi) if x is not None]
        if not vals:
            return "N/A"
        worst = min(vals)
        return "GREEN" if worst >= 0.95 else ("AMBER" if worst >= 0.90 else "RED")

    status = rag(last["CPI"], last["SPI_t"] or last["SPI"])
    notes = []
    if last["TCPI_to_BAC"] and last["TCPI_to_BAC"] > 1.10:
        notes.append(f"TCPI {last['TCPI_to_BAC']:.2f} > 1.10: completing within BAC is unrealistic; re-forecast EAC.")
    if last["pct_complete"] and last["pct_complete"] > 60 and last["SPI"] and last["SPI_t"] and last["SPI"] - last["SPI_t"] > 0.03:
        notes.append("Past 60% complete: classic SPI is converging to 1.0; rely on SPI(t).")
    if last["pct_complete"] and last["pct_complete"] >= 20 and last["CPI"] and last["CPI"] < 1:
        notes.append("Past 20% complete with CPI < 1: history suggests cumulative CPI will not recover by more than ~10%.")

    if a.json:
        print(json.dumps({"BAC": bac, "planned_duration_periods": pd, "status": status,
                          "periods": out, "notes": notes}, indent=2))
        return

    def g(x, p=2):
        return "-" if x is None else f"{x:,.{p}f}"

    print(f"BAC {bac:,.0f} | Planned duration {pd} periods | Status {status}\n")
    print(f"{'Period':<10}{'PV':>14}{'EV':>14}{'AC':>14}{'CV':>13}{'SV':>13}{'CPI':>6}{'SPI':>6}{'SPI(t)':>7}{'%Comp':>7}")
    for m in out:
        print(f"{str(m['period']):<10}{m['PV']:>14,.0f}{m['EV']:>14,.0f}{m['AC']:>14,.0f}{m['CV']:>13,.0f}"
              f"{m['SV']:>13,.0f}{g(m['CPI']):>6}{g(m['SPI']):>6}{g(m['SPI_t']):>7}{g(m['pct_complete'], 1):>7}")
    print("\nFORECAST (latest period)")
    print(f"  EAC1  BAC/CPI                 {g(last['EAC1_BAC_over_CPI'], 0):>16}")
    print(f"  EAC2  AC+(BAC-EV)             {g(last['EAC2_AC_plus_remaining'], 0):>16}")
    print(f"  EAC3  AC+(BAC-EV)/(CPIxSPI)   {g(last['EAC3_CPI_x_SPI'], 0):>16}")
    print(f"  ETC (EAC1)                    {g(last['ETC_EAC1'], 0):>16}")
    print(f"  VAC (EAC1)                    {g(last['VAC_EAC1'], 0):>16}")
    print(f"  TCPI to BAC                   {g(last['TCPI_to_BAC']):>16}")
    print(f"  Earned schedule               {g(last['ES_periods'])} periods (SV(t) {g(last['SV_t_periods'])})")
    print(f"  Forecast duration             {g(last['forecast_duration_periods'])} periods vs planned {pd}")
    if notes:
        print("\nNOTES")
        for n in notes:
            print("  - " + n)


if __name__ == "__main__":
    main()
