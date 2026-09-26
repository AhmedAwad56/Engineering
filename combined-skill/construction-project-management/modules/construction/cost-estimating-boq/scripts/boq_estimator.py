#!/usr/bin/env python3
"""BOQ pricing and markup calculator.

CSV columns: section,item,description,unit,qty, and either
  rate                         (all-in unit rate), or
  labour,material,plant,subcon (component unit rates, summed)

Markup order: Direct -> +Prelims% of D -> +Contingency% of (D+P)
  -> +Escalation (annual % x half duration) -> +OH&P% -> +VAT%

Usage:
  python3 boq_estimator.py boq.csv [--prelims 10] [--contingency 5]
      [--escalation 4 --escalation-months 18] [--ohp 8] [--vat 5]
      [--gfa 5000] [--currency USD] [--json]
"""
import argparse
import csv
import json
import sys
from collections import OrderedDict

COMPONENTS = ("labour", "material", "plant", "subcon")


def num(v, field, ref):
    v = (v or "").replace(",", "").strip()
    if v == "":
        return 0.0
    try:
        return float(v)
    except ValueError:
        sys.exit(f"Item {ref}: invalid {field} '{v}'")


def load(path):
    items = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        for i, row in enumerate(csv.DictReader(f), start=2):
            row = {k.strip().lower(): (v or "").strip() for k, v in row.items() if k}
            ref = row.get("item") or f"row{i}"
            qty = num(row.get("qty"), "qty", ref)
            comps = {c: num(row.get(c), c, ref) for c in COMPONENTS}
            if "rate" in row and row["rate"] != "":
                rate = num(row["rate"], "rate", ref)
            else:
                rate = sum(comps.values())
            items.append({"section": row.get("section") or "General", "item": ref,
                          "description": row.get("description", ""), "unit": row.get("unit", ""),
                          "qty": qty, "rate": rate, "amount": qty * rate,
                          "components": {c: comps[c] * qty for c in COMPONENTS}})
    if not items:
        sys.exit("No BOQ items found.")
    return items


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv")
    ap.add_argument("--prelims", type=float, default=0.0, help="%% of direct cost (0 if prelims priced in BOQ)")
    ap.add_argument("--contingency", type=float, default=0.0, help="%% of direct + prelims")
    ap.add_argument("--escalation", type=float, default=0.0, help="Annual escalation %%")
    ap.add_argument("--escalation-months", type=float, default=0.0, help="Construction duration in months")
    ap.add_argument("--ohp", type=float, default=0.0, help="Head office overhead & profit %%")
    ap.add_argument("--vat", type=float, default=0.0, help="VAT / sales tax %%")
    ap.add_argument("--gfa", type=float, default=0.0, help="Gross floor area (m2) for cost/m2")
    ap.add_argument("--currency", default="")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    items = load(a.csv)
    direct = sum(i["amount"] for i in items)
    prelims = direct * a.prelims / 100
    base = direct + prelims
    contingency = base * a.contingency / 100
    sub1 = base + contingency
    # Spend spread over the duration: escalate to mid-point
    esc_years = (a.escalation_months / 12.0) / 2.0
    escalation = sub1 * ((1 + a.escalation / 100) ** esc_years - 1)
    sub2 = sub1 + escalation
    ohp = sub2 * a.ohp / 100
    net = sub2 + ohp
    vat = net * a.vat / 100
    total = net + vat

    sections = OrderedDict()
    for i in items:
        sections[i["section"]] = sections.get(i["section"], 0.0) + i["amount"]
    comp_tot = {c: sum(i["components"][c] for i in items) for c in COMPONENTS}

    ranked = sorted(items, key=lambda x: -x["amount"])
    pareto, run = [], 0.0
    for i in ranked:
        if direct <= 0 or run / direct >= 0.8:
            break
        run += i["amount"]
        pareto.append({"item": i["item"], "description": i["description"], "amount": i["amount"],
                       "share_pct": 100 * i["amount"] / direct if direct else 0,
                       "cumulative_pct": 100 * run / direct if direct else 0})

    flags = []
    for i in items:
        if i["qty"] == 0:
            flags.append((i["item"], "Zero quantity (item included? rate-only?)"))
        if i["rate"] == 0:
            flags.append((i["item"], "Zero rate (unpriced item)"))
        if not i["unit"]:
            flags.append((i["item"], "Missing unit"))
        if i["qty"] < 0 or i["rate"] < 0:
            flags.append((i["item"], "Negative value (credit/omission?) - confirm intent"))

    summary = OrderedDict([
        ("Direct cost", direct), (f"Preliminaries ({a.prelims:g}%)", prelims),
        (f"Contingency ({a.contingency:g}%)", contingency),
        (f"Escalation ({a.escalation:g}%/yr, {a.escalation_months:g} mo)", escalation),
        (f"OH&P ({a.ohp:g}%)", ohp), ("Total excl. VAT", net),
        (f"VAT ({a.vat:g}%)", vat), ("TOTAL", total)])

    if a.json:
        print(json.dumps({"summary": summary, "sections": sections, "components": comp_tot,
                          "cost_per_m2": total / a.gfa if a.gfa else None,
                          "pareto": pareto, "flags": [{"item": x, "issue": y} for x, y in flags]}, indent=2))
        return

    cur = f" {a.currency}" if a.currency else ""
    w = 44
    print("ESTIMATE SUMMARY" + (f" ({a.currency})" if a.currency else ""))
    print("-" * (w + 18))
    for k, v in summary.items():
        if k == "TOTAL":
            print("-" * (w + 18))
        print(f"{k:<{w}}{v:>18,.2f}")
    if a.gfa:
        print(f"{'Cost per m2 GFA (incl. VAT)':<{w}}{total / a.gfa:>18,.2f}")
        print(f"{'Cost per m2 GFA (excl. VAT)':<{w}}{net / a.gfa:>18,.2f}")

    print("\nCOST BY SECTION (direct)")
    for s, v in sections.items():
        pct = 100 * v / direct if direct else 0
        print(f"  {s[:40]:<42}{v:>18,.2f}{pct:>7.1f}%")

    if any(comp_tot.values()):
        print("\nCOST BY RESOURCE (items priced by component)")
        for c, v in comp_tot.items():
            print(f"  {c.title():<42}{v:>18,.2f}")

    print(f"\nTOP COST DRIVERS (items making up ~80% of direct cost: {len(pareto)} of {len(items)})")
    for p in pareto:
        print(f"  {p['item']:<8}{p['description'][:34]:<36}{p['amount']:>16,.2f}{p['share_pct']:>7.1f}%{p['cumulative_pct']:>7.1f}%")

    if flags:
        print("\nFLAGS")
        for x, y in flags:
            print(f"  - {x}: {y}")


if __name__ == "__main__":
    main()
