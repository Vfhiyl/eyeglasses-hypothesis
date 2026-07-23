# 眼镜假说：实证检验流水线

用可复现的 Python 脚本检验 Macfarlane「13 世纪眼镜延长学者生涯、推动知识革命」假说。输出仅为 CSV 与回归表（`outputs/tables/`），无仪表盘。

**数据下载指南**：见 [`data/external/DOWNLOAD_MANIFEST.txt`](data/external/DOWNLOAD_MANIFEST.txt)（用户手动文件放 `../download_data/`，由 `00_sync_downloads.py` 同步）。

---

## 审计对象（本项目检验什么）

| 范围 | 内容 | 本项目 |
|------|------|--------|
| **大命题** | *Glass: A World History*（Macfarlane & Martin）：玻璃在文艺复兴、科学革命、实验器皿、透镜/望远镜/显微镜、容器玻璃等综合文明作用 | **未系统检验** |
| **窄化可检验命题** | 13 世纪末凸透镜眼镜（老花矫正）是否**系统性延长**读写密集型学者职业生涯，并赋予**玻璃制造中心城市**持久知识优势 | **本项目审计对象** |

不要把「大玻璃论」打成「小眼镜论」再宣布胜利或失败——README 与 `verdict.txt` 均按窄命题表述。

---

## 快速运行

```bash
cd eyeglasses-hypothesis
python -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/07_run_all.py
```

**优先阅读**（v3.1）：

0. [`docs/VERDICT_zh.md`](docs/VERDICT_zh.md) — **读者结论（三档裁决，可直接引用）**
1. [`docs/PREPRINT_zh.md`](docs/PREPRINT_zh.md) — **中文预印本（完整报告）**
2. [`outputs/tables/verdict.txt`](outputs/tables/verdict.txt) — 英文三档摘要
2. [`outputs/tables/evidence_by_claim.csv`](outputs/tables/evidence_by_claim.csv) — 按子命题汇总
3. [`outputs/tables/evidence_core.csv`](outputs/tables/evidence_core.csv) — 核心关联检验
4. [`outputs/tables/evidence_summary.csv`](outputs/tables/evidence_summary.csv) — 全量附录

单元测试：`.venv/bin/python tests/test_chow_and_periods.py`

---

## 项目做了什么

1. **同步与抓取**：从 `../download_data/` 同步；自动拉取 OWID、WIAG、Wikidata、Studium Parisiense API 等。
2. **清洗与对接**：统一 century/year 面板、玻璃中心 vs 对照（`config/cities.yaml`）。
3. **五层检验**：RCT 机制 → 断点/宏观 → 回归 → 反事实 → 稳健性。
4. **合成（审计版）**：`07_synthesis.py` 输出三列证据标签 + core/background 分表。

---

## 怎么读结果（v3：方向 × 识别强度）

| 列 | 含义 |
|----|------|
| `direction` | `consistent` / `inconsistent` / `null`（相对窄命题预测） |
| `identification_strength` | `descriptive` / `associational` / `experimental` / `sensitivity` |
| `supports_mechanism` | 主要来自现代 RCT（任务≠中世纪学术） |
| `supports_historical_timing` | 宏观时点相容（非因果） |
| `supports_strong_causal_claim` | **恒为 False**（本流水线无预注册准实验设计） |
| `inconsistent_with_prediction` | 方向与预测不符的关联结果（≠高质量反证） |
| `data_adequacy` | `adequate` / `insufficient` / `na` |

**优先读** [`evidence_by_claim.csv`](outputs/tables/evidence_by_claim.csv) 按子命题汇总；**不要**再用 `0/N` 强因果计数作标题。

---

## 当前结论（2026-07，v3.1 三档裁决）

定位：**可复现审计 + 强断言 debunk 包**——给出带方向的结论，而非「既不能证实也不能证伪」。

### 三档裁决

| 档位 | 命题 | 裁决 |
|------|------|------|
| **A · 弱机制** | 老花镜降低读写边际成本 | **成立（合理）** |
| **B · 强窄命题** | 宏观职业延长 + 玻璃中心优势 + 1290 > 1450 | **不成立（应拒绝）** |
| **C · 二手强断言** | 「文明起点」「+15 年」 | **夸张（应 debunk）** |

详见 [`docs/VERDICT_zh.md`](docs/VERDICT_zh.md)。

### 定稿表述

> 老花镜对读写工作有帮助（档 A）。但宏观可检验版窄命题在开放数据下站不住（档 B）。「文明起点」「+15 年」应 debunk（档 C）。
---

## 替代解释矩阵

| 结果 | 眼镜解释 | 更强替代解释 |
|------|----------|--------------|
| 1200–1300 手稿增长 | 老花读写延长 | 大学扩张、城市文书需求、保存偏差 |
| 巴黎学者 post/pre 增长 | 学者寿命/产出增加 | 资料覆盖、巴黎大学制度与编纂扩张 |
| Bologna Acta 引用增长 | 德国学者读写增强 | 机构记录变密、法学教育扩张 |
| MMM 玻璃中心事件增长 | 玻璃中心知识优势 | 地点归因、provenance 事件、商业流通 |
| 1450 断点更强 | 不利于眼镜优先叙事 | 印刷术、书价下降、识字率（Buringh–van Zanden） |
| BHOTMG 玻璃中心 HC「暴涨」 | 玻璃中心学术崛起 | pre-1300 基数近零（算术幻觉） |

---

## 地理设计：与预测方向不一致（弱识别）

「玻璃中心 = 眼镜可及性」是脆弱映射。关联结果若显著为负或不显著，可**削弱确信**，但因处理变量与对照构造较弱，**不能单独当作强反证**。

方法备忘（二次审计已改）：

- 断点：`log(y) ~ t + post + t×post`，±80 年等长窗口（非均值伪 Chow）
- Model1：去掉与 `C(century)` 共线的 `post_1300`
- ISTC：15 世纪横截面关联，**不是** DiD
- 面板：`hc_observed` / `books_observed`；主回归用观测单元
- 世纪：`period_start = year // 100 * 100`（1452 → 1400）
---

## 文档（预印本附录）

| 文档 | 内容 |
|------|------|
| [`docs/DATA_ROADMAP.md`](docs/DATA_ROADMAP.md) | **数据扩展路线图（下一步找什么）** |
| [`docs/PREPRINT_zh.md`](docs/PREPRINT_zh.md) | **中文预印本（主报告）** |
| [`docs/CLAIM_GENEALOGY.md`](docs/CLAIM_GENEALOGY.md) | 原书 / 译本 / 二手口号 vs 窄命题 |
| [`docs/LITERATURE_AND_DAG.md`](docs/LITERATURE_AND_DAG.md) | Ilardi 等文献 + 因果链与识别缺口 |
| [`docs/DATA_DICTIONARY.md`](docs/DATA_DICTIONARY.md) | 字段与筛选规则 |
| [`docs/DATA_PROVENANCE.md`](docs/DATA_PROVENANCE.md) | SHA-256 快照（由脚本生成） |

附加输出：`power_mde_summary.csv`、`sensitivity_age_thresholds.csv`、`studium_sample_audit.csv`、`robust_leave_one_out_glass.csv`、`robust_glass_permutation.csv`、`data_provenance.csv`。

单元测试：`.venv/bin/python tests/test_chow_and_periods.py && .venv/bin/python tests/test_studium_and_synthesis.py`

---

## 已接入数据源

| 数据 | 用途 | 状态 |
|------|------|------|
| ISTC 2025 | 15 世纪印本 | ✓ |
| RETE / CDMV | 宏观 HC | ✓ |
| Stelter OSF | HRE 任职年龄 | ✓ |
| Buringh 手稿 | 世纪产出 | ✓ |
| Murray HA | 精英科学 | ✓ |
| WIAG 主教 + Domherren | 神职高龄 | ✓ |
| RAG | 帝国学者事件 | ✓ |
| Bologna Knod | Acta 引用 | ✓ |
| MMM（含 SDBM TTL） | 手稿流转 | ✓ |
| BHOTMG | 城市大学 HC | ✓（背景层，已降权） |
| Studium Parisiense | 巴黎学者 ~28k | ✓ |
| SDBM 站内 CSV | 最新全库 | ✗ 审批；MMM 含快照 |

---

## 证伪条件（设计约定 vs 实际）

| 子命题 | 设计标准 | 实际 |
|--------|----------|------|
| A2：眼镜延长学者生涯 | 1300 后 45+ 占比显著上升 | **数据不足 + 未支持** |
| A3：眼镜先于知识爆发 | 1290 断点强于 1450 | **1450 更强（削弱）** |
| C1：玻璃中心效应 | `glass_center` 显著为正 | **未支持；多项显著为负** |

---

## 流水线结构

| 阶段 | 脚本 |
|------|------|
| 同步/抓取 | `00_sync_downloads.py`, `01a_*`, `02u_fetch_studium.py` |
| 处理 | `01_fetch_istc.py`, `02e`–`02v_process_*.py` |
| 分析 | `03`–`06`, `08_run_robustness.py` |
| 合成 | `07_synthesis.py` → `evidence_core.csv`, `evidence_background.csv`, `verdict.txt` |

---

## 主要局限

- 无历史随机实验；回归/断点为关联性。
- pre-1300 个体年龄样本极少。
- ISTC 仅 1452–1500。
- MMM 事件混合 provenance/国籍与生产。
- RCT 任务（采茶/缝纫/计件）与中世纪学者任务（阅读/抄写/讲授）**不匹配**。

---

## 参考文献

- Macfarlane, A. & Martin, G. (2002). *Glass: A World History* / *The Glass Bathyscaphe*
- Ilardi, V. (2007). *Renaissance Vision from Spectacles to Telescopes*. APS
- Rosen, E. (1956). The invention of eyeglasses. *J. Hist. Med. Allied Sci.*
- de la Croix et al. RETE / CDMV
- Stelter et al. (2021). *Demography*
- Buringh & van Zanden（手稿/印本）
- Curtis et al. BHOTMG
- Mapping Manuscript Migrations / SDBM
- Studium Parisiense (LaMOP)
- PROSPER / PROSPER II / THRIVE

详见 `docs/LITERATURE_AND_DAG.md`、`docs/CLAIM_GENEALOGY.md`。

---

**不能声称因果**：本仓库提供可复现的关联性检验、审计分层证据与方法附录。