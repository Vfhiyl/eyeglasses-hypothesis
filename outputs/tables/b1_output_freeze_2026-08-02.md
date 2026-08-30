# B1-Output 冻结裁决（2026-08-02）

## 为何停

连续 purify → 手针 → Lotto/visual fix 后，再补针对 **SESOI 判决无实质改变**：所有合理敏感性均 **FAIL +5（需 boot lo≥0）** 与 **FAIL +15**。继续扩针属于收益递减。

## 冻结主结果

| 设定 | n | 中位 Δ | CI | +5 | +15 |
|------|---|--------|-----|----|-----|
| **Primary**（文本脑力；去视觉） | 19 | **−4** | [−12, 8] | FAIL | FAIL |
| drop 薄商人 | 15 | +6 | [−10, 9] | FAIL | FAIL |
| scholar buckets | 14 | +4.5 | [−10, 9] | FAIL | FAIL |
| scholar ∩ pins≥3 | 10 | +5 | [−7, 13] | FAIL | FAIL |

表：`b1_output_estimand_summary.csv`、`b1_output_estimand_sensitivity.csv`  
规则：`docs/B1_OUTPUT_SESOI.md`；script `27_b1_output_estimand.py`

## 可写进摘要的句子

1. **在当前「45+ 有日期文本成果跨度 vs 匹配文本著作对照」测量下，不支持佩戴者中位多出 +5 或 +15 年成果跨度。**  
2. 学术子集中位可到约 +5～+6，但 bootstrap 下界为负 → **不能**写成已证实的小正效应。  
3. 戴镜证据后许多人仍有续作（描述性：Alessandra +5y 书信、Wood/Maurolico 长跨度等）≠ 相对对照的 +15 年优势。  
4. 劳动年 B1（script 25）与成果 B1-Output **双线**均不支持 Macfarlane 量级年数。

## 明确不做什么（冻结期内）

- 不再为抬 n 扩具名佩戴者  
- 不再刷 Wikidata SPARQL 指望翻盘  
- 不把名人正 Δ 格（Filelfo/Petrarch）写成总效应  

## 解冻条件（任一）

- 新书目库级对照面板（EDIT16/ISTC 作者年）且预注册；或  
- 独立 post-evidence 速率 estimand 预注册并达到 n≥20 对照设计  

## 方向调整

B1-Output **测量方向没做错**，但作为「猎证主战场」已裁决到可写进 claim map 的强度；下一主任务应离开微观佩戴×年数，转向仍开放的宏观/话术核对（见 CLAIM_MAP）。
