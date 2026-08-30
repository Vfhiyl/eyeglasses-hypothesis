# B1-Output SESOI（出成果 · 预注册意图）

**与 B1 劳动年分离。** 劳动年路径（`B1_SESOI.md` / script 25）已冻为：在现有 estimand 下 +5/+15 **FAIL**。  
本文件只裁决：**戴镜后 / 45+ 是否多出有日期的知识成果（著作跨度与件数）**。

| 主张 | SESOI | 最低 n | 结果变量 |
|------|-------|--------|----------|
| 方向：戴镜延长「有日期成果」跨度 | **+5 年** | 20 有 Δ 的匹配对 | `output_span_after_45` |
| Macfarlane 量级（成果版） | **+15 年** | 20 | 同上 |
| 件数（探索） | 不设硬阈 | — | `n_works_after_45` 的中位 Δ |

## 样本

- **处理组：** onsetish 主样本中有 Wikidata QID、且 P50∪P800 有 ≥1 条经出生/死亡窗过滤的日期作品。
- **对照：** `b1_roster_control_matches_region.csv` 匹配到的对照；同样要有 ≥1 条日期作品。
- **禁止：** 用「无 Wikidata 作品」当 0 成果（缺失 ≠ 无产出）；无作品者不进 primary Δ。

## Estimand（对称）

对处理者 T 与对照 C：

\[
\text{output\_span\_after\_45} = \max\bigl(0,\ \max(Y) - (\text{birth}+45)\bigr)
\quad\text{若}\ \exists\, y\in Y:\ y \ge \text{birth}+45;\ \text{否则 } 0
\]

其中 \(Y\) = 合理窗内的 P50∪P800 作品年（优先 P50；P800 作 notable 敏感性）。

\[
\Delta = T - \mathrm{median}(C_{\text{matched with works}})
\]

**SESOI 通过（raw）：** 中位 Δ ≥ 阈；+5 另要求 bootstrap 95% 下界 ≥ 0。

### 附录指标（不替代主 SESOI）

- `n_works_after_45`、`share_works_after_45`
- 处理组专有：`output_span_after_evidence`、`n_works_after_evidence`（onset 后；对照无 onset，不作主 Δ）

## 与劳动年 B1 的关系

| | B1 劳动 | B1-Output |
|--|---------|-----------|
| 测什么 | 近距活动/存活代理年 | 有日期的著作/作品年 |
| 当前主结论 | n=40；Δ≈−1.5；+5/+15 FAIL | **本轮新建** |
| 数据源 | 书信/档案 chrono + curated nearwork | Wikidata P50/P800（可扩书目） |

劳动年 FAIL **不**自动等于「无晚岁成果」；反之亦然。

## 实现

- Script：`scripts/27_b1_output_estimand.py`
- 表：`outputs/tables/b1_output_estimand_*.csv`
- 方法注：`outputs/tables/b1_output_estimand_method.md`
- Kickoff：`outputs/tables/b1_output_kickoff_2026-08-02.md`

## 样本边界（2026-08-02）

- **主 SESOI：** 文本脑力劳动（人文/教士/书吏/书信作者等）；**排除** painter/sculptor/artisan 视觉格。  
- **对照：** 仅文本著作型（`output_eligible=True`）；绘画/行政对照即使有薄 P800 也不用。

## 当前状态（2026-08-02 strict 扩矿后）

| 检查 | 结果 |
|------|------|
| 主样本 pairs | n=**32**（文本对照 overlay 扩矿；非水货针） |
| 中位 Δ span | **−2.5**；CI **[−5, 3]** |
| SESOI +5 / +15 | **FAIL** |
| 扩矿说明 | `b1_output_strict_expand_2026-08-02.md` |

此前冻结口径见 `b1_output_freeze_2026-08-02.md`；解冻条件仍适用。
