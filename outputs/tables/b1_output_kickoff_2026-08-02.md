# B1-Output kickoff（2026-08-02）

劳动年 B1 冻为 +5/+15 FAIL 后，主战场转向**有日期的知识成果**。

## 已做

1. 预注册：`docs/B1_OUTPUT_SESOI.md`
2. 测量：`scripts/27_b1_output_estimand.py`
3. 佩戴者成果年 = Wikidata P50∪P800 ∪ `data/curated/b1_wearer_output_years_curated.csv`（书信/著作 chrono 收成）
4. 对照 = 匹配对照的 P50∪P800；缺口时用 `use_in_primary` curated nearwork 的 last−(birth+45) 作后备跨度

## v0 主结果（`b1_output_estimand_summary.csv`）

| 指标 | 值 |
|------|-----|
| 有成果年的处理者 | **26** |
| 有 Δ 的匹配对 | **26**（≥20） |
| 中位 Δ（output_span_after_45） | **−0.75** |
| bootstrap 95% CI | **[−10.5, 6.25]** |
| SESOI +5 / +15 | **FAIL_OR_UNAVAILABLE** / **FAIL** |
| share Δ>0 | 0.50 |
| 探索：中位 Δ n_works_after_45 | +2.0；CI [1.0, 5.5] |

读法：在「45 岁后有日期成果跨度」上，佩戴者相对匹配对照**没有** +5/+15 年的中位优势；CI 上界刚过 +5，但中位为负、下界很负。件数 Δ 略正（探索，非年 SESOI）。

## 正 Δ 较大的格（附录，非裁决）

Filelfo +22；Lotto +17.5；Maurolico +16；Petrarch +15.5 — 名人著作密，可能是名录偏误而非眼镜因果。

## 敏感性（`b1_output_estimand_sensitivity.csv`）

| mode | n | 中位 Δ | CI | +5/+15 |
|------|---|--------|-----|--------|
| full（主） | 26 | −0.75 | [−10, 6.25] | FAIL |
| chrono_only | 19 | −5 | [−13, 4] | FAIL（上界&lt;5） |
| drop_thin（pins&gt;2） | 14 | +6.75 | [−7.5, 13.5] | FAIL（下界&lt;0） |
| wd_only | 4 | +11 | [−30, 27] | FAIL（n 太小） |
| wd_ctrl_only（对照只用 WD） | 13 | +11.5 | [−3, 25.5] | FAIL（下界&lt;0） |

注意：full 里 **25/26** 对至少用了一个 curated-nearwork 对照后备 → 与劳动年路径部分重叠；下一步应优先给这些对照补真 P50/书目，而不是再扩佩戴者名单。

## 下一步（按优先级）

1. **对照真成果年 densify**（降低 curated 后备占比）
2. Pirckheimer 等晚岁书信补针（现跨度可能低估）
3. 劳动年 B1：**不再**以扩 n 为主线

表：`b1_output_estimand_pairs.csv`、`b1_wearer_output_years.csv`、`b1_output_estimand_method.md`
