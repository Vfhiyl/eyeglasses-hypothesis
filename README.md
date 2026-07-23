# 眼镜假说：实证检验流水线（v4.0）

用可复现 Python 脚本审计 Macfarlane 相关「眼镜延长学者生涯 / 知识革命」叙事。输出为 CSV 与 `verdict.txt`。

**原则：** 裁决强度不得超过证据；不够则**猎新证据**，禁止「既不能证真又不能证伪」收工。

**数据下载：** [`data/external/DOWNLOAD_MANIFEST.txt`](data/external/DOWNLOAD_MANIFEST.txt) → `../download_data/` → `00_sync_downloads.py`。

---

## 优先阅读（v4）

1. [`docs/PREPRINT_zh.md`](docs/PREPRINT_zh.md) — **可单独发表的中文预印本**
2. [`docs/VERDICT_zh.md`](docs/VERDICT_zh.md) — 四层裁决
3. [`docs/CLAIM_MAP.md`](docs/CLAIM_MAP.md) — B1–B4 命题图与猎证
4. [`outputs/tables/verdict.txt`](outputs/tables/verdict.txt)
5. [`outputs/tables/evidence_by_family.csv`](outputs/tables/evidence_by_family.csv) — **按家族汇总（不计票）**

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/07_run_all.py
```

复现声明：**作者自测可复现**（非独立审计签字）。仓库：https://github.com/Vfhiyl/eyeglasses-hypothesis

---

## 四层裁决（摘要）

| 层 | 裁决 |
|----|------|
| **A1** 现代机制 | **支持**（生产率分试验写；勿合并 6–33%） |
| **A2** 中世纪近距工具 | **可信**；延长年数未估 |
| **B 宏观强版** | **未获支持**（B2/B4）；HC 上 1450 斜率变化显著大于 1290 |
| **B1** 佩戴者多干几年 | **未识别 → 猎证**（主战场） |
| **C** 文明唯一起点 | **debunk**；+15 年待三版页码 |

---

## 开放猎证（最重要）

1. Macfarlane 三版 +15 页码  
2. 点名佩戴 × 产出面板 → core n≥20（`scripts/15_b1_wearer_offline_expand.py`；EMLO）  
3. 手核 `outputs/tables/wikidata_p800_hand_audit_sample.csv`（exploratory）

---

## 怎么读表

优先 `evidence_by_family.csv`。`n_tests` **不是**选票。Null 看 `equivalence_ci_summary.csv`（CI vs SESOI）。

---

## 许可与引用

见 `LICENSE`、`CITATION.cff`。Tag：`v4.0.0`。
