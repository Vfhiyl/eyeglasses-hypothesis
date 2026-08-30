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
| **B1** 佩戴者多干几年 | **+5/+15 FAIL**（纠正后 Δ=+3.0，CI[−2,9]；因果未识别）；pass 期 PASS_RAW **已撤回**，见 `docs/B1_CURATION_AUDIT_2026-08-12.md` |
| **C** 文明唯一起点 | **debunk**；+15 年句已确认为原书原句（Glass p.145），史实不获支持 |

---

## 开放猎证（最重要）

1. 端点敏感性已做（`b1_symmetry_sensitivity.csv`：双侧去"到死"端点 Δ→+0.5；领域内最严子集 −6.75）；逐人核对佩戴者 `years_after_evidence` 来源仍开放  
2. 对称、预注册、结果盲的对照准入/剔除规则（见 `docs/B1_SESOI.md` 治理节）  
3. 人内产出率设计已有初版（`b1_within_person_rates.csv`：Alessandra ratio 1.6、Ammannati 1.17，exploratory）；待扩 Mazzei / Lotto 账本 / Pepys 负例 + 对照序列  
4. 手核 `outputs/tables/wikidata_p800_hand_audit_sample.csv`（exploratory）

---

## 怎么读表

优先 `evidence_by_family.csv`。`n_tests` **不是**选票。Null 看 `equivalence_ci_summary.csv`（CI vs SESOI）。

---

## 许可与引用

见 `LICENSE`、`CITATION.cff`。Tag：`v4.0.0`。
