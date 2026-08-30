# Pass CZ — OA re-probe of gated densify + freeze gate (2026-08-06)

## Judgment

Digital SESOI/hygiene path is closed. Highest ROI left: (1) check whether physical-gated sources leaked onto free OA; (2) if still dry, ship a one-command freeze gate so library pins can’t silently break the claim.

## A) OA re-probe

| Target | Result |
|--------|--------|
| Keil *Augustanus Opticus* | IA advanced search **empty** (retry after SSL glitch) |
| HAB Wiesel–August | diglib shell 200; no spectacle-token hit |
| Yale Spinelli Filza (Benedetto 1534) | catalog 403; IA hit `BeineckeMS850_47` = **Tomasso** Spinelli *Liber Taxarum* 1436 — **wrong person/century** |
| Gray *Devon Household Accounts* 1996 Pt.2 | IA `devonhouseholdac0000unse` **exists** but `access-restricted-item` / `printdisabled`; OCR/PDF **private** — borrow-gated, not free densify |

**Verdict: still dry for free unlock.** Gray is newly *findable* on IA but not freely readable; schedule controlled digital lending / physical borrow.

Cache: `data/raw/external_mine_2026-08-03_early/pass_cz/`.

## B) Freeze gate

Added `scripts/31_b1_freeze_gate.py` → remasures 25/27/29/30 and asserts:

- labor + output SESOI+5 PASS
- +15 FAIL
- sensitivity raw FAIL / clean PASS
- collision active = 0

Report: `outputs/tables/b1_freeze_gate_report.md` — **GATE PASS**.

## Next ROI

1. **Borrow** Gray IA item or physical DCRS/Wellcome (Bourchier / Bath accounts).
2. Yale Beinecke Spinelli Filza (not MS 850 Liber Taxarum).
3. Keil p.384 + HAB letters in library.
4. After any pin: `python3 scripts/31_b1_freeze_gate.py`.
