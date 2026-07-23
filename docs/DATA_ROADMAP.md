# 数据扩展路线图（DATA_ROADMAP）

**目标：** 裁决「经验红利解锁」vs「近距续工」，不是改措辞。  
**正题：** 眼镜是让年长学者在经验峰值窗口做出革命性突破，还是只普通延长近距工时？  
**缺口（仍开放、但不阻塞裁决）：** 更大的「佩戴 × 晚生涯产出」点名样本（现微面板 n=3）；EMLO；可选 SDBM 全库 dump。  
**已闭合的关键缺口：** 成就年龄分布（Wikidata P800）；贸易/价格/制作名单；**多城 SDBM**；Ilardi 点名佩戴种子 + 微检验脚本。

```text
制造 → 供应价格 → 【佩戴】 → 45+ 近距续工 ──┬──► 普通延长工时     ← 现证据偏向此（A ACCEPT）
                                            └──► 经验峰值革命产出 ← 宏观+成就年龄检不出（B REJECT）
```

---

## 当前已接入 vs 未接入

| 状态 | 数据源 | 检验什么 | 局限 |
|------|--------|----------|------|
| ✅ 已跑 | Studium Parisiense (~28k) | 巴黎学者 45+、活动跨度 | 单城；1300 后记录膨胀 |
| ✅ 已跑 | Stelter OSF (33k) | HRE 任职跨度、45 岁仍在任 | **无城市**；刚接入 share45 检验 |
| ✅ 已跑 | WIAG 主教 / RAG / 博洛尼亚 / MMM / BHOTMG | 神职、大学事件、手稿流转 | 非学者或识别弱 |
| ✅ 已跑 | RETE/CDMV、ISTC、手稿 OWID | 宏观 HC、印本、断点 | 末端 outcome；非佩戴 |
| ✅ 已下载未充分用 | **Pantheon 2025** | 欧洲学者 fame 样本 age at death | 精英选样；**已接入 02w** |
| ✅ 已下载未充分用 | **Wikidata 大学教师 ~7.8k** | 生卒年 45+ | 覆盖偏；**已接入 02w** |
| 🆕 种子库 | **`data/curated/spectacle_primary_mentions.csv`** | 1286–1504 采用史料时间线 | 非面板；可扩行 |
| ⏳ 增量拉取中 | **Wikidata occupations** | 每半世纪窗口前重扫代理；每页落盘；失败再扫一轮重试 | `01d` + `check_https_proxy_cert.py --host query.wikidata.org` |
| ✅ 已跑 | **SDBM 多城导出** | Venice/Milan/Nuremberg + Bologna/Cologne/Oxford + Florence/Paris | Place±Provenance；见 `sdbm_city_summary.csv` |
| ⏳ 可选 | **SDBM 全库 dump** | 更密地理网格 | 账号导出；不阻塞裁决 |
| ⏳ 待申请 | **DALME** 检索 occhiali / spectacles | 遗嘱清单中的眼镜 | 无 bulk；可搜后手工导出 |
| ✅ curated CSV | **Ilardi 订单/价格/贸易** | 1462–66 宫廷订单 + 1415 价格；RQ1976 订正 50 副；1525 产量回推 | 见 `ilardi_*.csv`；已入 synthesis |
| ✅ OA PDF | **伦敦海关 Jenks 大部 + Cobb + Gras** | 1384–1509 序列；1494 已升原文；1487 单笔 3456 | 本地 ~29 卷 PDF；ii 中段多卷无命中 |
| ✅ secondary→primary | **1494 Hill/Mowger** | Jenks iv_3：**2880** 副 | 原 MacGregor 次级引用已核 |
| ⛔ 停 | **DALME** `occhiali` / `spectacles` | 遗嘱清单拥有率 | 检索无命中；语料过小；停 |
| ✅ 已钉名 | **Davidsohn Forschungen III nr.955** | 1329 **Ser Neri Mici da Bibbiena**（Bibbiena 公证/商人）诉 Mercanzia：佛罗伦萨购得 *unum par ochialium* 于 Borgo Ghiaceti 被抢 | 本地 `data/raw/davidsohn/`；表 `davidsohn_nr955_spectacles.csv` |
| ⏳ 可扩 | **Jenks 全系列 PDF 全文搜 spectacles** | 跨世纪伦敦进口时间序列 | iii_1 / 24H6 已本地 PDF；可继续下 ii/iv |
| ✅ 已跑 | Wikidata P800 代表作年龄 | 成就年龄 pre/post 1280 + 半世纪 + 玻璃中心 | 充分样本下年龄**前移**；强化 B REJECT |
| ✅ curated | Ilardi Appendix I Florence makers | 1413–1562 occhialai 名单（OCR≈40/48） | 商业产能；非佩戴×产出 |
| ✅ 已跑 | Ilardi 年龄带订单 | 1466 按 30–70 岁分级老花镜 | 支持 A（年龄工具化） |

---

## 三轨并行（按性价比）

### 轨 1 · 直接采用证据（填 DAG 最大洞）

**产出：** `spectacle_adoption_timeline.csv` + 可引用年表  
**脚本：** `02x_process_spectacle_adoption.py`；种子见 `data/curated/spectacle_primary_mentions.csv`

| 优先级 | 行动 | 谁做 | 预期 |
|--------|------|------|------|
| P0 | 扩 curated CSV：每行带 archive ref + 页码 | 人工 + AI 辅助录入 | 20–50 条可核对记录 |
| P0 | Ilardi (2007) 订单/价格 → `ilardi_*.csv` | **已完成（OCR 自抓）** | 米兰宫廷 + 佛罗伦萨价格 + 伦敦进口 |
| P1 | DALME 搜 `occhiali` / `spectacles` / `oculos` → 导出 | **已试：无命中，停** | — |
| P1 | Jenks 后续卷全文搜 spectacles（ii/iii/iv） | AI：已加 1446、1463–4、Cobb line-sum | 跨世纪进口序列 |
| P1 | DOI 10.25592/uhhfdm.9898 测量文件落盘 | `01d_fetch_expansion_data.py` | 1504 佛罗伦萨物理痕迹 |
| P1 | Ilardi 1525/1480 Catasto 产量回推 → trade CSV | **已写入** `ilardi_trade_volumes.csv` | 产能上界，非船运实数 |
| P2 | 中文译本 p.190 / Ch.8 对照 | 你 | 传播链中文侧 |

**成功标准：** 1300 前后**至少 5 条**独立 ownership/physical 记录，带一级或二级出处。

---

### 轨 2 · 独立学者职业面板（不吊 RETE）

**产出：** `alt_scholar_age_ttests.csv` → 并入 synthesis  
**脚本：** `02w_process_scholar_age_tests.py`

| 数据源 | 新检验 | 为什么值得 |
|--------|--------|------------|
| Stelter 33k | 任职跨度、45 岁仍在任、首次任职年龄 | 比 Studium 更大；HRE 大学扩张 |
| Pantheon | 死亡年龄 45+ pre/post 1300 | 有 birthcity；可对照玻璃中心 |
| Wikidata 扩大 | 同上 + 更多 occupation | 量级 ↑ |

| 优先级 | 行动 |
|--------|------|
| P0 | 跑通 `01d` → 更新 `02j` 读 intellectuals CSV |
| P1 | Wikidata SPARQL 加 `P108 employer` 大学、`P937 work location` |
| P2 | EMLO 书信 bulk（邮件申请）→ 学者活跃年 |

**成功标准：** ≥3 个**独立数据库**对同一假设（1300 后 45+ 职业延长）给出可报告结果；若仍全 null / 与预测相反，可**加强拒绝 B 档**（非悬空）。

**已补（2026-07-23）：** Wikidata P800 代表作年龄面板（`01e`/`02aa` → `age_at_work_ttests.csv`）——充分样本下年龄**前移**，强化 B REJECT。

---

### 轨 3 · 地理 × 知识产出（玻璃中心仍用 proxy）

| 优先级 | 数据 | 用途 |
|--------|------|------|
| P1 | SDBM 导出 | 13–15 世纪手稿城市 × 世纪 |
| P1 | EDIT16 MARCXML | 意大利 16 世纪印本城市 |
| P2 | europop + 已有 ISTC/MMM | 人均产出（已有脚本，可加深） |
| P3 | PatentCity（已下 956MB） | 19 世纪光学产业城（弱验 1300，强验「玻璃中心长期优势」） |

---

## 分工约定（2026-07-22）

| 谁做 | 内容 |
|------|------|
| **脚本自动** | OWID、WIAG、Studium API、SDBM 处理、合成 |
| **脚本自动（需代理）** | `check_https_proxy_cert.py --host query.wikidata.org` 猎代理 → `01d_fetch_expansion_data.py` 分批拉 Wikidata；SDBM/Scribd 浏览器可用 `outputs/tables/working_https_proxies*.txt` + ZeroOmega |
| **请你帮下** | EMLO 申请；可选 SDBM 全库；Ilardi 遗嘱等增量 |
| **已完成 SDBM** | 11 导出（玻璃城 + 对照 + Provenance 子集）→ `sdbm_city_summary.csv` |

**SDBM 多城结论（v3.4 synthesis）：** Venice 升（Place/Prov≈2.7/3.2），但 Bologna 对照也升（≈3.1）；Paris/Oxford 降；峰值多在 **1450** → timing 可相容，**非**玻璃中心特异。

```bash
cd eyeglasses-hypothesis
.venv/bin/python scripts/01d_fetch_expansion_data.py   # 扩大 Wikidata
.venv/bin/python scripts/02j_process_wikidata.py       # 需先改读 intellectuals
.venv/bin/python scripts/02w_process_scholar_age_tests.py
.venv/bin/python scripts/02x_process_spectacle_adoption.py
.venv/bin/python scripts/07_synthesis.py
```

**你需要手动做的（高杠杆）：**

1. **EMLO** — 通信网络申请（若开）
2. **可选 SDBM 全库** — 已有多城面板；全库非阻塞
3. **DALME / 遗嘱增量** — 拥有率仍薄

---

## 什么数据会改变裁决？

| 若找到… | 改变 |
|---------|------|
| 1300–1350 遗嘱面板：眼镜条目 ↑ 且与 scribe/cleric 共现 | **A→B 桥** 有 micro 支持；B 档可能部分升级 |
| Stelter/Pantheon/Wikidata 多库一致：1300 后 career 覆盖 45 岁 ↑ | B 档 career 子命题需重判 |
| 仍全 null + curated 仅 10 条 scattered ownership | **加强 B 拒绝** + **A 保留**（有 micro、无 macro） |

---

## 文件索引

| 路径 | 说明 |
|------|------|
| `data/curated/spectacle_primary_mentions.csv` | 采用史料种子（可编辑） |
| `scripts/01d_fetch_expansion_data.py` | 自动扩展下载 |
| `scripts/02w_process_scholar_age_tests.py` | Pantheon/Wikidata/Stelter 年龄检验 |
| `scripts/02x_process_spectacle_adoption.py` | 采用时间线 |
| `data/external/DOWNLOAD_MANIFEST.txt` | 完整下载清单 |
| `docs/LITERATURE_AND_DAG.md` | 因果链与 proxy 对照 |

*结论措辞随数据变；本路线图随新数据源更新。*
