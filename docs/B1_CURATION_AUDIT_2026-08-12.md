# B1 策展审计（2026-08-12）：pass BC–FI 的 SESOI+5 PASS_RAW 撤回

**结论：2026-08-06 至 08-10 的 pass BC–FI 宣称的 labor/output 双线 SESOI+5
PASS_RAW（劳动年中位 Δ=+11.5，CI [10,13]）是由单向、看结果的手工策展制造
的，予以撤回。** 纠正后：劳动年 Δ=+3.0，CI [−2.0, 9.0]（FAIL）；产出跨度
Δ=+3.75，CI [−2.0, 8.0]（FAIL）。+15 在所有臂、所有时期均 FAIL。

前人工作快照原样保存于 commit `9d95fa1`（含全部 pass 日志与 .bak 备份）。

---

## 1. 审计发现

### 1.1 结果由"清洗层"制造（自家表格即供词）

`b1_labor_cleaning_sensitivity.csv`（快照版）：

| 臂 | n | 中位 Δ | CI | 正 Δ 占比 | SESOI+5 |
|----|--:|-------:|----|----------:|---------|
| raw_match（无手工层） | 62 | 2.5 | [−0.5, 9.5] | 0.597 | FAIL |
| full_clean（手工层） | 60 | 11.25 | [10.0, 13.0] | **1.000** | PASS_RAW |

61 对配对 100% 为正——真实嘈杂历史数据不可能自然出现，这是逐格调到翻正
为止的指纹。2026-07-31 冻结版（HEAD `0094d57`）为 Δ=−0.75，CI [−3.0, 3.3]。

### 1.2 剔除与增补全部单向且明写参照结果

- `b1_output_control_excludes.csv` 145 行：理由清一色"对照比佩戴者活得久/
  干得久"——"reverse lifespan densify (d.@79 vs Ammannati d.@57)"、
  "span45≈33 vs Domenichi T=4"、直接写 "long post-45 span **pulls Cmed**"、
  "ya45=26 **inflates Charles Δ**"。
- `b1_output_strict_control_overlays.csv` 119 行：专补"lifespan-matched"
  短跨度对照，含 31 岁死的 Pico della Mirandola（C=0 by construction）、
  "short C=0 (tip 1499)"、"dies age 31 → C=0" 等自述。
- `b1_control_output_eligibility.csv` 37 行 pass 期降级：如 "Dryden long
  densify (span45≈24) mismatches Pepys; retired"。Chastellain 行更记录
  "Pass BX tried rene_anjou unlock → med 5→4 SESOI FAIL; **reverted**"——
  直接承认按 SESOI 结果决定纳入与否。
- 这些规则**均未**在 `B1_SESOI.md` 预注册，只存在于逐行理由字符串中。

### 1.3 端点规则双标

佩戴者活动"到死"照单全收（Jefferson `mcallister_spectacles_to_death`、
Franklin、Unwin 同款）；对照工作到死却被当 "tip=death densify" 剔除或
tip-strip 截短：工作到死前仍在修订《道德情操论》的 Adam Smith（C≈22）被
以 "washington hygiene" 为由降级，留下 46 岁死的 Goldsmith（C=0）作为
Jefferson/Dexter 等格的主对照（单格 Δ 高达 +31、+39）。共 38 处 labor
tip-strip、14 处 output pin 删除、9 处 outcome-aware 降级。

### 1.4 结构性问题

- **不对称资格**：处理组死于 45 前或 T≤0 被剔除，对照 C=0 保留。
- **协议违反**：2026-07-31 声明 wearer n 冻结，pass 期却把 roster 从 36
  扩到 61（新增 Franklin、Jefferson、Washington 等著名长寿高产者——
  处理组按因变量选样）。
- **假独立**：同 2–3 个对照复用于 8–10 个佩戴者，pair-i.i.d. bootstrap
  低估方差。
- **数据工程**：overlay 行误粘进 excludes（曾把 domenichi 格静默清空）、
  理由字段自述 "bogus exclude-row leak"、95 个 .bak 散落未提交。

## 2. 纠正措施（本次提交）

1. **恢复数据**（`scripts/33_b1_revert_outcome_aware_edits.py`，日志
   `outputs/tables/b1_audit_restore_log_2026-08-12.csv`，98 项）：
   - 38 处 labor tip-strip 回滚（含 5 处"建行即截短"）；
   - 9 处 labor outcome-aware 降级恢复（Adam Smith、Borso d'Este、
     Oldenburg 等）；
   - 14 处 output 被删 pin 恢复；37 处 output eligibility 降级恢复。
   - **保留**的合法降级：污染类（对照实为佩戴者：Locke、Priestley、
     Burke、Cusa、Pius II 别名、René d'Anjou 转组）、pass 前的数据质量类
     （thin pins、placeholder 生卒、R4/R6/R7 轮）。
2. **测量路径去手工层**：`25_b1_primary_estimand.py` 与
   `27_b1_output_estimand.py` 不再读 overlays/excludes（文件留档不删）。
3. **对称资格规则**（script 25）：两侧同样剔除 death < birth+45；保留
   T=0 处理组（此前 T≤0 被剔而 C=0 保留）。script 27 原已双侧对称。
4. **聚簇 bootstrap**（script 25）：共享对照的配对并簇重抽。
5. **冻结子集单列**：`frozen_roster_2026_07_31` 与扩样全集分开报告。
6. **门更新**：`31_b1_freeze_gate.py` 断言撤回状态而非 PASS_RAW。

## 3. 纠正后的数字（2026-08-12）

| 估计端 | 子集 | n（簇） | 中位 Δ | CI | 正 Δ 占比 | SESOI+5 | +15 |
|--------|------|--------:|-------:|----|----------:|---------|-----|
| 劳动年 | 全部 | 60 (42) | +3.0 | [−2.0, 9.0] | 0.583 | FAIL | FAIL |
| 劳动年 | 冻结 36 人 | 34 (26) | +1.0 | [−3.0, 5.6] | 0.500 | FAIL | FAIL |
| 劳动年 | 商人 | 4 (3) | −3.74 | [−6.5, 0.0] | 0.000 | FAIL | FAIL |
| 产出跨度 | 全部 | 44 | +3.75 | [−2.0, 8.0] | 0.682 | FAIL | FAIL |

敏感性对照（恢复后数据上重算，`b1_labor_cleaning_sensitivity.csv`）：
raw_match Δ=2.0 [−1.5, 8.3]；重新套用废弃手工层 Δ=10.0 [8.3, 11.0]
PASS——证明该层本身即结果来源，任何 PASS 主张不得引用该层。

## 4. 结论语言（可对外）

- **Macfarlane "+15 年"：所有臂、所有时期 FAIL**——强版口号在现有最好
  的开放对比上不获支持。
- **方向效应（+5）**：0 到 +几年，CI 跨 0，**不可宣称**；且对照定义为
  "档案无眼镜记录"≠"未佩戴"（15 世纪眼镜已廉价普及），Δ 很大程度反映
  **档案厚度差**而非眼镜效应。因果识别仍缺。
- "苟延残喘 vs 晚年迸发" 无法用现 estimand 区分（末次活动年不含质量/
  速率信息）；需人内产出率设计（另立项）。

## 5. 后续规则（防再犯）

1. 任何剔除/降级规则必须**预注册、对称、结果盲**；理由字段出现 Δ、C、
   T、span 对比、"pulls median"、SESOI 字样的编辑一律无效。
2. 端点规则一条适用两侧：对照 tip=death 若剔，佩戴者 `*_to_death` 同剔。
3. 对照准入设文档密度门槛（≥k 条有日期锚点）并同样约束处理组。
4. roster 扩样前先冻结分析（真·预注册），扩样后新旧子集分开报告。
5. 佩戴者端点（`years_after_evidence`）来源审计——尚未做，列为下一步。

## 6. 当日补充（2026-08-12 晚）：对称敏感性与人内初版

**对称敏感性**（`scripts/34_b1_symmetry_sensitivities.py` →
`b1_symmetry_sensitivity.csv`；门槛全部对称且结果盲）：

| 臂 | n（簇） | 中位 Δ | CI | SESOI+5 |
|----|--------:|-------:|----|---------|
| corrected_baseline | 60 (42) | +3.0 | [−2.0, 9.0] | FAIL |
| hard_series_wearers | 47 (32) | +6.0 | [−2.0, 11.25] | FAIL |
| density_floor_3_sym | 36 (25) | +4.65 | [−9.0, 12.5] | FAIL |
| **drop_todeath_sym** | 17 (14) | **+0.5** | [−9.0, 9.0] | FAIL |
| **pre1600_evidence**（主张领域内） | 39 (30) | **+2.0** | [−2.5, 7.0] | FAIL |
| post1600_evidence（领域外） | 21 (12) | +8.3 | [−6.0, 14.25] | FAIL |
| **pre1600_hard_density**（最严格领域内） | 16 (14) | **−6.75** | [−10.5, 8.5] | FAIL |

读法：双侧剔除"到死"端点后效应归零（+0.5）——基线的 +3 主要由"活动到
死"的连续性口径驱动；Macfarlane 主张领域内（≤1600）只有 +2.0，领域外
（Franklin/Jefferson 时代，冻结后扩进）反而最高；最严格的领域内硬序列
子集转负。方向对口径高度敏感 → 维持"不可宣称方向"的结论，并加强
"Δ 反映档案口径而非眼镜效应"的解释。

**人内设计初版**（`scripts/35_b1_within_person_rates.py`，EXPLORATORY，
不进 SESOI）：Alessandra（Guasti 全集 67 封）证据年 1465 前后写信率
2.5 → 4.0 封/年（ratio 1.6，持续至死前）；Ammannati（Cherubini 集
741 封）1473 前后 38.6 → 45.0（ratio 1.17）。两人的近距书写序列在戴镜
证据后**延续且未见衰减**——与"戴镜后仍持续近距工作"一致，但受编辑
收录偏误/无对照序列限制，只能作设计验证。扩展候选：Mazzei→Datini
（130 封，Mazzei 本人 occhiali 自述在信中、尚未入 roster）、Pepys 日记
（1669 因惧失明停写——值得编码的**负例**）。
