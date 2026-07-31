# B1 SESOI（预注册意图）

| 主张 | SESOI | 最低 n | 结果变量 |
|------|-------|--------|----------|
| 方向：戴镜延长近距劳动 | **+5 年** | 20 | A: last_nearwork − first_adult_nearwork（有日期序列） |
| Macfarlane 原句 | **+15 年** | 20 | 同上；对照匹配后处理−对照 |

## 样本定义（2026-07-31 修正）

- **主样本：** 明文具名佩戴者 roster 普查（onsetish；含短序列/0），见 `scripts/20_b1_roster_census_panel.py` → `b1_roster_census.csv`
- **Hard dated series：** 仅附录（长轨迹可复核）；**禁止**用 hard 子集均值当 SESOI 主估计
- **n≥20：** 指 onsetish 中有结局编码的处理组（或匹配对数），不是 hard 个数

## 当前状态（2026-07-31 深夜：region 重建 + René densify）

**主表：** `b1_primary_estimand_*.csv` + `b1_free_roam_2026-07-31_rene_orleans_densify.md`

| 检查 | 结果 |
|------|------|
| 全体 primary | n=**36**；中位 Δ **−0.75**；CI **[−3.0, 3.3]** → 仍排除 +5/+15 |
| 本轮 | SPARQL 重建 region 表；René 法国统治者对照加密（Δ −25.5→−2）；Orléans 恢复 Philip the Good 对照（Δ +13） |
| Latone / Nuno | 仍无硬生卒可 ingest |
| 近距因果 B1 | **未识别**；+15 强读 **不支持** |
