# B1 对照池设计（草案）

## 处理组
见 `outputs/tables/b1_treatment_onsetish_roster.csv`（排除死亡清单/遗物/纯收礼）。  
全员编码（含排除项）见 `outputs/tables/b1_roster_census.csv`（2026-07-31 起主表）。

## Region constraint (2026-07-31)

Non-region birth+occ matching produced invalid pairs (e.g. Italian merchants ↔ East Asian names).  
**Prefer** `outputs/tables/b1_roster_control_matches_region.csv` (macro-region via WD P27/P19).  
Script: `scripts/24_b1_region_rematch.py`.

| | |
|--|--|
| Strict region matches | 29 (24 occ+birth+region; 5 relaxed+region) |
| Median Δ ya45 | +2.75 (SESOI +5 fail) |
| P50 work-proxy median Δ | 10.5; bootstrap CI **includes 0** |

## 已跑对照

- 池：`b1_control_candidates_v3.csv`（n≈1089）
- 出生±10：`20_b1_roster_census_panel.py` → Δ ya45 中位 **−1**
- 职业桶：`22_b1_roster_occ_match_and_p800.py` → 主桶匹配 n=14，Δ ya45 **−1.5**；放宽 n=13（商/统治者→humanist）
- P800 著作叠加：中位 Δ **+6.5**（薄；+15 未过）
- 裁决：`b1_roster_verdict.csv`
- 缺口：商人/统治者对照层；档案验阴；书信级近距劳动

## 匹配规则（预注册意图）
1. 同一 `occupation_class`（可合并：ruler*；humanist_scholar+cardinal_humanist）
2. 出生年 ±10；活动地同宏观区（意大利 / 英格兰 / 伊比利亚）
3. 档案厚度：至少有 Wikidata P50/P800 **或** 已刊书信编年
4. 阴性：在 Ilardi / 本仓库 OCR / EMLO / LetterSampo 无 spectacles/occhiali 命中

## 结果变量
- **A（首选）：** last_dated_nearwork_year − first_adult_nearwork_year
- **B：** years_alive_after_age_45（presbyopia 窗口）
- **C：** share of dated works with age≥50

## SESOI
- 方向：处理−对照 ≥ **+5** 年（变量 A）
- Macfarlane 原句：≥ **+15** 年，且 n≥20

## 已知偏误
「无眼镜记录」≠未佩戴；富档案偏误；证据年偏晚。
