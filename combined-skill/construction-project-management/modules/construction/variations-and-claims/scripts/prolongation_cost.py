#!/usr/bin/env python3
"""Prolongation cost calculator: site overheads + head-office overhead formulas.

Site (time-related) overheads:
  delay_days x (monthly site overhead / 30.4)  or  actual daily rate via --site-overhead-daily

Head-office overhead & profit (only where actual loss is not provable):
  Hudson:   (tender HO&P % / 100) x (contract sum / contract period) x delay
  Emden:    (actual company HO&P % / 100) x (contract sum / contract period) x delay
  Eichleay: (contract billings / total company billings) x company overhead in period
            / days of performance x delay days

Usage:
  python3 prolongation_cost.py --delay-days 64 --site-overhead-monthly 185000
     [--contract-sum 42000000 --contract-days 730]
     [--tender-hoohp-pct 7] [--hoohp-pct 6.2]
     [--company-overhead 9500000 --company-turnover 160000000
      --contract-billings 30000000 --performance-days 794]
     [--json]
"""
import argparse
import json


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--delay-days", type=float, required=True, help="Compensable delay (calendar days)")
    ap.add_argument("--site-overhead-monthly", type=float, default=0.0)
    ap.add_argument("--site-overhead-daily", type=float, default=0.0, help="Overrides monthly if given")
    ap.add_argument("--contract-sum", type=float, default=0.0)
    ap.add_argument("--contract-days", type=float, default=0.0, help="Original contract period (days)")
    ap.add_argument("--tender-hoohp-pct", type=float, default=None, help="HO&P %% in tender (Hudson)")
    ap.add_argument("--hoohp-pct", type=float, default=None, help="Actual company HO&P %% from accounts (Emden)")
    ap.add_argument("--company-overhead", type=float, default=0.0, help="Company HO overhead over the performance period (Eichleay)")
    ap.add_argument("--company-turnover", type=float, default=0.0, help="Total company billings over the period (Eichleay)")
    ap.add_argument("--contract-billings", type=float, default=0.0, help="This contract's billings over the period (Eichleay)")
    ap.add_argument("--performance-days", type=float, default=0.0, help="Actual days of performance incl. delay (Eichleay)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    res = {"delay_days": a.delay_days}
    daily = a.site_overhead_daily or (a.site_overhead_monthly / 30.4 if a.site_overhead_monthly else 0.0)
    res["site_overhead_daily"] = daily
    res["site_overheads"] = daily * a.delay_days

    ho = {}
    notes = []
    if a.contract_sum and a.contract_days:
        per_day = a.contract_sum / a.contract_days
        if a.tender_hoohp_pct is not None:
            ho["Hudson"] = a.tender_hoohp_pct / 100 * per_day * a.delay_days
        if a.hoohp_pct is not None:
            ho["Emden"] = a.hoohp_pct / 100 * per_day * a.delay_days
    if a.company_overhead and a.company_turnover:
        billings = a.contract_billings or a.contract_sum
        perf = a.performance_days or ((a.contract_days + a.delay_days) if a.contract_days else 0)
        if billings and perf:
            allocated = billings / a.company_turnover * a.company_overhead
            ho["Eichleay"] = allocated / perf * a.delay_days
            res["eichleay_allocated_overhead"] = allocated
    res["head_office_overhead"] = ho

    notes.append("Formulas are a fallback: tribunals prefer actual recorded HO costs and proof the contractor "
                 "was prevented from taking other work (lost opportunity).")
    if "Hudson" in ho:
        notes.append("Hudson uses the TENDER percentage; widely criticised as it assumes the tender margin was achievable.")
    if "Emden" in ho:
        notes.append("Emden uses the company's ACTUAL HO&P % from audited accounts; generally preferred in UK/Commonwealth practice.")
    if "Eichleay" in ho:
        notes.append("Eichleay is used mainly in US federal contracts and for suspension/standby periods.")
    notes.append("Only claim prolongation for compensable (Employer-risk) delay; exclude concurrent periods unless the contract apportions.")
    res["notes"] = notes

    if a.json:
        print(json.dumps(res, indent=2))
        return

    print(f"Compensable delay: {a.delay_days:g} days")
    print(f"Site overheads:    {daily:,.2f}/day x {a.delay_days:g} = {res['site_overheads']:,.2f}")
    if ho:
        print("\nHead-office overhead & profit (formula methods):")
        for k, v in ho.items():
            print(f"  {k:<10}{v:>16,.2f}   -> total with site OH {res['site_overheads'] + v:,.2f}")
    else:
        print("\n(No HO overhead formula inputs given.)")
    print("\nNotes:")
    for n in notes:
        print("  - " + n)


if __name__ == "__main__":
    main()
