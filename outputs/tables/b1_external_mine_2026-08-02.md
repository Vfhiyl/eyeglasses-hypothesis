# External mine 2026-08-02 (not home-flock rematch)

Directive: dig outside curated assets; do not reshuffle existing pins.

## Solid promotions

| person_id | Evidence | Class | years_after | hard |
|-----------|----------|-------|------------:|:----:|
| `stonley_richard` | Folger diary 1593-11-23 personal “ij pere of Spectacles” (+ 1594 repurchases) | england clerk | **5** | True |
| `pepys_samuel` | Pepys Diary 1666-12-24 green spectacles; writes by spectacles 12-29; Turlington 1668 | england clerk | **24** | True |
| `albrecht_prussia` | 1542 Königsberg→Gdańsk personal ocularia replacement order (Bieganowski) | hre ruler | **26** | False |

Caches: `data/raw/external_mine_2026-08-02/`. Chronos: `b1_stonley_richard_activity_chrono.csv`, `b1_albrecht_prussia_activity_chrono.csv`.

## Logged, not promoted

| person_id | Why held |
|-----------|----------|
| `lorkyn_thomas` | Death inventory (7 pairs) — years_after=0 path |
| `cole_william_bristol` | EMLO “monoptick spectacle **without glass**” = pinhole, wrong class |
| Charlett / Gregory 1707 | Already closed (wear-duration ask, not onset) |
| Wojciech Baza / Albertus Basa 1535 inventory | Identity/date conflict in secondary lit; thin |

## EMLO vocab sweep (this pass)

True glass-wear self-hits still dominated by already-rostered Lynnet/Wood/Sheldon. Cole was the only strong *new* name and fails class filter.

## Stonley densify controls

Ascham, Smith, Burghley, Nicholas Bacon, Wilson — england clerk/humanist birth±10.

## Albrecht densify controls

Joachim I Nestor, John II of Simmern, Charles V, Maria of Jever — hre ruler birth±10 (admin docs).

## Pass 2 promotions (still external)

| person_id | Evidence | Class | years_after | hard |
|-----------|----------|-------|------------:|:----:|
| `howard_william_naworth` | Ornsby Surtees 68: 1626 pairs + 1629 “for my Lord” silver setting | england humanist | **14** | True |
| `bourchier_henry_bath` | Gray Devon accounts: 1646 pairs for my Lord; 1647–48 repairs | england ruler | **8** | False |
| `cowper_william` | EE→Hesketh 1786-12-11 spectacles for reading occupations | england humanist | **14** | True |

## Remeasure after ingest (B1_SPARQL=0) — after Howard/Bath/Cowper

| Panel | n Δ | median Δ | boot 95% CI | SESOI +5/+15 |
|-------|----:|---------:|-------------|--------------|
| Labor primary | **46** | **+0.3** | [−3.5, 4.25] | FAIL |
| B1-Output strict span | **36** | **−1.5** | [−4.75, 4.0] | FAIL |

Cell reads (external promotions):

| person | Labor T / C / Δ | Output span Δ |
|--------|----------------:|--------------:|
| Stonley | 34 / 24 / **+10** | **+10** |
| Pepys | 12 / 20 / **−8** | **−7** |
| Albrecht | 33 / 15.5 / **+17.5** | no_delta |
| Howard Naworth | 32 / 19 / **+13** | **+6** |
| Bath | 22 / 10 / **+12** | no_delta |
| Cowper | 24 / 11 / **+13** | **+4** |

## Pass 3 promotions (still external)

| person_id | Evidence | Class | years_after | hard |
|-----------|----------|-------|------------:|:----:|
| `jeffreys_joyce` | Spicksley/Hubbard: June 1646 lost spectacles + tip 6d; also magnifying glass + spectacles | england merchant | **4** | False |
| `franklin_benjamin` | Whatley letters 1784/1785: double spectacles; “wear my Spectacles constantly” | england humanist (Anglo densify) | **6** | True |

Caches: `jeffreys_spicksley_spectacles_1646.md`, `franklin_whatley_double_spectacles_1784.md`. Chronos: `b1_jeffreys_joyce_activity_chrono.csv`, `b1_franklin_benjamin_activity_chrono.csv`.

### Logged, not promoted (pass 3)

| person_id | Why held |
|-----------|----------|
| `walpole_horace` | 1757 Scarlett green spectacles for inflammation; later recovered and read *without* spectacles — temporary, not durable optical onset |
| Samuel Johnson | Famous myope / “Blinking Sam”; contemporaries note he **never wore** spectacles |
| John Evelyn | Mentions tortoiseshell trade / Murano glass — no personal wear pin |
| Sarah Fell accounts | No spectacle hits in Fenny edition sweep |
| Lucy Gobert / Anne Lloyd / John Smith clothier | Death inventories — years_after=0 path |

## Remeasure after Jeffreys + Franklin (B1_SPARQL=0)

| Panel | n Δ | median Δ | boot 95% CI | SESOI +5/+15 |
|-------|----:|---------:|-------------|--------------|
| Labor primary | **48** | **+0.8** | [−3.0, 4.25] | FAIL |
| B1-Output strict span | **37** | **−1.0** | [−4.5, 6.0] | FAIL |

Cell reads (new):

| person | Labor T / C / Δ | Output span Δ |
|--------|----------------:|--------------:|
| Jeffreys | 30 / 28.5 / **+1.5** | no_delta (merchant ctrl textual elig=0) |
| Franklin | 39 / 16 / **+23** | **+20** (late onset + long post-45 life; Anglo densify cell) |

## Pass 4 promotions (still external)

| person_id | Evidence | Class | years_after | hard |
|-----------|----------|-------|------------:|:----:|
| `peale_charles_willson` | Diary 1788-08-25: bought 2 pr (9″/18″ focus), cut into bifocals for miniature painting (Letocha) | england artisan (Anglo densify) | **39** | True |
| `jefferson_thomas` | McAllister 1806-11-12 prior-wear + bifocal order; delivery Dec; →Peale 1807 “great advantage” | england humanist (Anglo densify) | **20** | True |

Caches: `peale_diary_bifocals_1788.md`, `jefferson_mcallister_spectacles_1806.md`. Chronos: `b1_peale_charles_willson_activity_chrono.csv`, `b1_jefferson_thomas_activity_chrono.csv`.

### Logged, not promoted (pass 4)

| person_id | Why held |
|-----------|----------|
| `hooke_robert` | Cooper late-life “new spectacles” paraphrase; no OA dated diary line. Micrographia nettle loupe ≠ refractive wear onset |

## Remeasure after Peale + Jefferson (B1_SPARQL=0)

| Panel | n Δ | median Δ | boot 95% CI | SESOI +5/+15 |
|-------|----:|---------:|-------------|--------------|
| Labor primary | **50** | **+1.25** | [−3.0, 6.5] | FAIL |
| B1-Output strict span | **38** | **−1.0** | [−4.0, 6.0] | FAIL |

Cell reads (new):

| person | Labor T / C / Δ | Output span Δ |
|--------|----------------:|--------------:|
| Peale | 41 / 26.5 / **+14.5** | no_delta (painter/artisan visual appendix) |
| Jefferson | 38 / 12 / **+26** | **+8** |

## Pass 5 promotions (still external)

| person_id | Evidence | Class | years_after | hard |
|-----------|----------|-------|------------:|:----:|
| `voiture_vincent` | Lett. CLXXXVII: «mes lunettes… depuis six mois… en vous escrivant» (Münster/Longueville ~1647) | france humanist | **1** | False |
| `dexter_samuel` | MHS gold temple spectacles ca.1785 + McCaffrey living reading/writing use | england humanist (Anglo densify) | **25** | False |

Caches: `voiture_lettre_187_lunettes.md`, `dexter_samuel_spectacles_1785.md`.

### Logged, not promoted (pass 5)

| person_id | Why held |
|-----------|----------|
| `hooke_robert` | Still no OA dated diary purchase line |
| Goethe | Explicitly disliked/refused spectacles («Goethe-Blick») |

## Remeasure after Voiture + Dexter (B1_SPARQL=0)

| Panel | n Δ | median Δ | boot 95% CI | SESOI +5/+15 |
|-------|----:|---------:|-------------|--------------|
| Labor primary | **52** | **+1.25** | [−3.0, 6.5] | FAIL |
| B1-Output strict span | **38** | **−1.0** | [−4.0, 6.0] | FAIL |

Cell reads (new):

| person | Labor T / C / Δ | Output span Δ |
|--------|----------------:|--------------:|
| Voiture | 6 / 12 / **−6** | no_delta |
| Dexter | 39 / 22.5 / **+16.5** | +9 but exclude_coverage_low_pin |

## Pass 6 promotions (still external)

| person_id | Evidence | Class | years_after | hard |
|-----------|----------|-------|------------:|:----:|
| `tye_thomas` | Account 1761-04-22 «a pair of Spectacles for my Self 2/6» (Ayscough; also Miss Bett Newton) | england merchant | **22** | True |

Caches: `tye_thomas_spectacles_1761.md`. Chrono: `b1_tye_thomas_activity_chrono.csv`.
Densify: Davison Q6900893, Whitbread Q3471265, Beckford Q333240 (CTRL_REGION england).

### Logged, not promoted (pass 6)

| person_id | Why held |
|-----------|----------|
| `hooke_robert` | IA diary OCR still no clean dated purchase line |
| `unwin_mary` | Surviving spectacles + Hesketh third-party wear; onset date thinner than Tye self-pin |
| `herle_mrs` | 1651 Bath accounts named purchase; bio/identity too thin |

## Remeasure after Tye (B1_SPARQL=0)

| Panel | n Δ | median Δ | boot 95% CI | SESOI +5/+15 |
|-------|----:|---------:|-------------|--------------|
| Labor primary | **53** | **+1.0** | [−3.0, 6.5] | FAIL |
| B1-Output strict span | **38** | **−1.0** | [−4.0, 6.0] | FAIL |

Cell reads (new):

| person | Labor T / C / Δ | Output span Δ |
|--------|----------------:|--------------:|
| Tye | 25 / 31 / **−6** | no_delta (merchant/admin controls ineligible for textual output) |

## Pass 7 promotions (still external)

| person_id | Evidence | Class | years_after | hard |
|-----------|----------|-------|------------:|:----:|
| `jackson_ralph` | Cash Book 1760-01-01 «myself a pr of Spectacles» (Mordecai Lazarus) | england merchant | **30** | True |
| `unwin_mary` | Museum spectacles + Hesketh «in her spectacles» (Weston soft 1786) | england letter_writer | **10** | False |

Caches: `jackson_ralph_spectacles_1760.md`, `unwin_mary_spectacles_soft.md`.
Densify Jackson: Coutts Q7788650, Angerstein Q3809383, Baring Q5565890.

### Logged, not promoted (pass 7)

| person_id | Why held |
|-----------|----------|
| `hooke_robert` | IA `diaryofroberthoo0000robe` OCR: 0 spectacle hits |

## Remeasure after Jackson + Unwin (B1_SPARQL=0)

| Panel | n Δ | median Δ | boot 95% CI | SESOI +5/+15 |
|-------|----:|---------:|-------------|--------------|
| Labor primary | **55** | **1.0** | [-3.0, 5.0] | FAIL |
| B1-Output strict span | **38** | **-1.0** | [-4.0, 6.0] | FAIL |

Cell reads (new):

| person | Labor T / C / Δ | Output span Δ |
|--------|----------------:|--------------:|
| Jackson | 9.0 / 42 / **-33.0** | no_delta |
| Unwin | 27.0 / 22.5 / **4.5** | 7.0 |

## Pass 8 promotions (still external)

| person_id | Evidence | Class | years_after | hard |
|-----------|----------|-------|------------:|:----:|
| `blundell_nicholas` | Diary 1722-08-07 «I began to uese Spectacles» for small print/letters | england humanist | **15** | True |
| `jeake_samuel` | 1676 convex spectacles 3s (RCM accounts) + diary adult wear after smallpox | england merchant | **23** | True |

Caches: `blundell_nicholas_spectacles_1722.md`, `jeake_samuel_spectacles_1676.md`.
Densify: Addison/Steele/Swift/Prior (Blundell); Pitt/Yale/Guy (Jeake).

## Remeasure after Blundell + Jeake (B1_SPARQL=0)

| Panel | n Δ | median Δ | boot 95% CI | SESOI +5/+15 |
|-------|----:|---------:|-------------|--------------|
| Labor primary | **57** | **1.0** | [-3.0, 5.0] | FAIL |
| B1-Output strict span | **39** | **-1.0** | [-4.0, 6.0] | FAIL |

Cell reads (new):

| person | Labor T / C / Δ | Output span Δ |
|--------|----------------:|--------------:|
| Blundell | 23.0 / 12.5 / **10.5** | 1.5 |
| Jeake | 2.0 / 28 / **-26.0** | no_delta |

## Next external leads (not yet ingested)

| Lead | Note |
|------|------|
| Chardin 1771 Autoportrait aux bésicles | Soft living wear via self-portrait; france artisan |
| Giles Moore journal | IA OCR had no spectacle hits in quick pass |
| Further French lunettes self-reports | Beyond Voiture |
