# B1 within-person letter rates (EXPLORATORY — not a SESOI test)

**Date:** 2026-08-12  
**Script:** `35_b1_within_person_rates.py` → `b1_within_person_rates.csv`

Question probed: after the first surviving spectacle evidence, does the
wearer's dated letter series continue / thicken ("burst") or thin out
("linger")? Complete edited corpora only; ±10y windows around the
evidence year, truncated at adulthood and death.

| person | letters | before win | after win | rate before | rate after | ratio | evid→last letter (y) |
|--------|--------:|-----------|-----------|------------:|-----------:|------:|---------------------:|
| alessandra_strozzi | 67 | 1455-1464 | 1465-1471 | 2.5 | 4.0 | 1.6 | 5 |
| ammannati | 741 | 1463-1472 | 1473-1479 | 38.6 | 45.0 | 1.17 | 6 |

Per-year counts: see `b1_within_person_rates_by_year.csv`.

## Hard caveats (do not skip)

1. Editorial/survival bias: complete editions still reflect what was
   kept; Alessandra's corpus is known to be denser late in life.
2. No control series — a non-wearer's rate drift over the same ages is
   unknown; aging alone changes letter volume.
3. Rates count letters, not near-work hours or quality; a signature
   equals an essay.
4. Evidence year is late (first surviving mention, not first wear), so
   genuine post-wear years leak into the before window.
5. n=2 persons. This is a design demo showing the data CAN support
   within-person analysis; expansion candidates: Mazzei→Datini corpus
   (130 dated letters; Mazzei's own occhiali self-reports are in the
   letters but he is not yet in the roster census), Ammannati tomo3,
   Lotto's libro di spese, Pepys diary (ends 1669 for eye fears —
   a NEGATIVE within-person case worth coding).

Verdict impact: none by itself. Use only to scope the future
within-person estimand (pre-registered rate ratio with control
series and editorial-density adjustment).
