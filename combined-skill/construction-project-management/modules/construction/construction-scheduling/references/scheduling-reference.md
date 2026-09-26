# Scheduling Reference

## Contents
1. Relationship types
2. Float definitions
3. Indicative durations and productivity rates
4. Programme submission checklist

## 1. Relationship types

| Type | Meaning | Construction example |
|---|---|---|
| FS | B starts after A finishes | Formwork striking FS+7 after concrete pour (it's better to model curing as an activity) |
| SS | B starts after A starts (+lag) | Blockwork SS+20 after the frame, once the lower floors are ready |
| FF | B finishes after A finishes (+lag) | Plastering FF+5 after blockwork |
| SF | B finishes after A starts | Rare. Temporary power must run until permanent power starts |

## 2. Float definitions

- **Total float (TF) = LS − ES.** The time an activity can slip without delaying completion. Under FIDIC and NEC the question of who "owns" float is contract-specific. NEC4 treats float that isn't terminal float as available to the Contractor for planning, and the SCL Protocol's default is that float belongs to the project.
- **Free float (FF).** The time an activity can slip without delaying any successor's early start.
- **Negative float.** The programme can't meet a constraint or completion date, so recovery is needed.
- **Terminal float (NEC).** The gap between planned Completion and the Completion Date. It belongs to the Contractor.

## 3. Indicative durations and productivity rates

These are rough planning rates only. They vary widely with region, crew size, method and access, so always ask for or confirm the contractor's own rates.

| Work | Typical rate |
|---|---|
| Bulk excavation (machine) | 300–800 m³/day per excavator |
| Rebar fixing | 1.0–1.5 t per gang of 4 per day |
| Formwork (slab, conventional) | 8–15 m² per carpenter per day |
| Concrete placing (pump) | 30–60 m³/hr |
| Typical RC floor cycle (mid-rise) | 7–14 days per floor |
| Blockwork | 8–12 m² per mason per day |
| Internal plaster | 15–25 m² per plasterer per day |
| Ceramic tiling | 6–10 m² per tiler per day |
| Painting (2 coats) | 40–60 m² per painter per day |
| Lift supply lead time | 12–26 weeks after approval |
| LV switchgear / chillers | 12–24 weeks |
| Material submittal review | 14–28 days per round; allow 2 rounds for critical items |

## 4. Programme submission checklist (FIDIC 8.3 / NEC4 31.2)

- Order and timing of work, including design, procurement, manufacture, delivery, construction, testing and commissioning.
- Review periods for submittals and design by the Engineer or Project Manager.
- Sequence and timing of inspections and tests.
- Sectional completion dates and key access dates.
- Resource histograms (labour, major plant).
- A supporting report: method statements, assumptions, calendars and the critical path narrative.
- NEC4 additionally requires: starting date, access dates, Key Dates, Completion Date, planned Completion, float and time risk allowances, health and safety requirements, and the procedures set out in the contract.
