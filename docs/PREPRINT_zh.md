# 眼镜假说可复现审计：开放历史数据能否支持「老花镜延长中世纪学者生涯」？

**类型：** 工作论文 / 预印本（审计报告）  
**版本：** v4.0（2026-07-23）  
**原则：** 裁决强度不得超过证据；**正确修法是猎新证据**，不是把结论冲淡成「既不能证真又不能证伪」。  
**说明：** 本文自洽。配套代码：https://github.com/Vfhiyl/eyeglasses-hypothesis（作者自测可复现，非独立审计签字）。

---

## 摘要

Macfarlane 与 Martin（2002）及相关传播常将十三世纪凸透镜眼镜与欧洲知识增长相联系。本文区分：

1. **近距续工：** 眼镜降低老花后近距读写成本，延长可工作工时（不必等于晚生涯革命）。  
2. **经验红利解锁（强宏观版）：** 年长学者经验峰值被系统性释放，表现为 45+ 份额上升、制造中心优势、1290 断点强于印刷等。

**四层裁决（硬结论 + 开放猎证）：**

| 层 | 裁决 |
|----|------|
| **A1 现代机制** | **支持。** PROSPER：采茶重量相对生产率约 +21.7%；PROSPER II：成衣生产率约 +5.7%（95% CI 约 1–10%）。THRIVE 终点是自报收入（约 +33%），**不是**生产率——分写，禁止合并成「6%–33% 效率」。 |
| **A2 中世纪应用** | **历史上可信**（发明定年与贸易扩散）；**平均延长多少年未估计**——待 B1 面板。 |
| **B 宏观强版** | **未获支持**（B2/B4 代理）。**≠** 已拒绝「佩戴者多干几年」（**B1 未识别 → 优先猎证**）。Wikidata P800/P577 仅 exploratory，不作摘要主拒绝句。 |
| **C 传播话术** | **文明唯一起点：debunk。** 「+15 年」句：**已在 Chicago 正文 p.145 核验**（作者原句）；开放数据是否支持该量化是另一回事，不得把「书里有这句话」当成「历史已证实」。 |

**一句话：** 现代近距机制与中世纪近距工具史站得住；宏观「经验红利解锁」在现有代理上站不住；佩戴者到底多干几年必须靠新的联立证据来裁决，不能用弱化措辞结案。

**关键词：** 眼镜史；老花；知识革命；可复现审计；负结果；证据狩猎

---

## 1. 引言

### 1.1 问题

Alan Macfarlane 与 Gerry Martin（2002）将玻璃技术组合与欧洲知识增长相联系。凸透镜老花镜是其中一环。Ilardi（2007）夯实发明与贸易史，但不自动推出宏观生涯革命。二手层常压缩为「文明起点」「+15 年」。

### 1.2 做什么、不做什么

| 范围 | 本文 |
|------|------|
| A1/A2、B2/B4、C 文明口号 | **给出可检验裁决** |
| B1 佩戴×生涯年数 | **未识别 → 猎证主线**（非永久不可知） |
| 玻璃全书宽链 | **未系统检验** |

反模糊：数据充分且预测落空 → 对该命题裁决不支持；不充分 → **去找数据**。

命题拆分见文内 B1–B4；完整地图可另附仓库 `docs/CLAIM_MAP.md`。

---

## 2. 主张谱系与「+15 年」

三层必须分开：

1. **原书宽论证：** 玻璃组合与知识革命相关。  
2. **原书 Ch.8 眼镜叙事（已核 Chicago 扫描本）：** 老花在四十多岁妨碍读写；眼镜约 1285 北意发明等（印刷页 **p.144–145**）。  
3. **「+15 年」量化（已核）：** 同页 **p.145** 原文：

> The invention of spectacles increased the intellectual life of professional workers by fifteen years or more.

同页并提 Petrarch、工匠 active life almost doubled、与印刷互促。Miller / Delanceyplace 等为转述。Profile 英版与商印中译页码仍待对照。

**C 档：** debunk「文明唯一起点」；**不得**再写「+15 年不在原书 / 只来自 Miller」。书中有量化句 ≠ 开放数据已证实该年数。

---

## 3. 理论链与识别缺口

```text
镜片制造 → 贸易价格 → 获得并佩戴 → 近距工时 → 活动跨度/著作 → 宏观知识
```

**主缺口 = B1：** 佩戴者 vs 未佩戴者的联立面板几乎不存在。玻璃中心、手稿库、代表作年龄都是弱代理。  
大众贸易削弱「始终精英奢侈品」和「制造地必领先」（B4），**不**自动否定各地佩戴者的边际收益（B1）。

---

## 4. 数据与方法

### 4.1 数据源（节选）

Studium Parisiense；RETE/CDMV；ISTC；手稿序列；SDBM 多城导出；Wikidata；Ilardi/Jenks 贸易；Rosen/Davidsohn；PROSPER / PROSPER II / THRIVE。

**语义约束：**

- Studium `observed_activity_span` ≠ 真实 career duration。  
- SDBM 计量的是**被记录的手稿相关事件**，不是干净的「产出」。  
- RETE 人力资本依赖后世出版可见性。  
- ISTC 是 15 世纪印本横截面，非 1300 DiD。  
- Wikidata P800 为策展「代表作」，P577 为发表/发行年，≠ 创作全集年表。

### 4.2 设计

- 机制：RCT **分结局**报告。  
- B2：Studium 等 45+ 份额；报告 95% CI 与 SESOI（5pp）。  
- B3：P800/P577 年龄 → **附录 exploratory**。  
- B4：玻璃中心回归；CI vs SESOI。  
- 时点：分段趋势 Chow；正式估计 `Δslope_1450 − Δslope_1290` 的 bootstrap CI。  
- 合成按**证据家族**汇总，**禁止**用检验条数投票。

### 4.3 B1–B4

| ID | 命题 | 状态 |
|----|------|------|
| B1 | 佩戴者是否多干几年 | **未识别；猎证**（点名佩戴×著作；目标 n≥20） |
| B2 | 社会 45+ 学术活动份额 | 现有面板**不支持上升**（CI 仍宽） |
| B3 | 重大作品年龄后移 | 非 B1 必要预测；P800 exploratory |
| B4 | 制造中心知识优势 | **未获支持**；跨城贸易削弱该预测 |

---

## 5. 结果

### 5.1 按证据家族（非计票）

| 家族 | 裁决 |
|------|------|
| F1 现代机制 | A1 **支持**（分结局） |
| F2 佩戴者微观 | B1 **未识别**；方向样本仍不足，继续扩名 |
| F3 Studium 年龄结构 | B2 **未获支持**；share45 差分 CI 跨过 SESOI → 不精确，但无上升证据 |
| F4 Wikidata P800 | B3 exploratory；策展著名作品发表年龄后期样本更低——**不作主拒绝句** |
| F5 城市地理 | B4 **未获支持**；Model1 CI 宽 |
| F6 宏观时点 | 人力资本序列上 `Δslope(1450−1290)` bootstrap 95% CI **不含 0**（1450 更强）——眼镜断点强于印刷的主张站不住 |
| F7 贸易采用 | A2 **支持**大众近距工具史 |

### 5.2 RCT（禁止合并）

- **PROSPER（采茶重量）：** 相对生产率约 **+21.7%**。  
- **PROSPER II（成衣生产率）：** 约 **+5.7%**（约 1.04–10.4%）。  
- **THRIVE：** 自报月收入差异约 **+33%**——收入 ≠ 产量。

### 5.3 B2 / B4 / 时点

- Studium share45：点估计约 +4.5pp，95% CI 约 [−4.3, +13.4]pp，相对 SESOI=5pp 为 **imprecise**；**没有**「上升已证实」。  
- 玻璃中心活跃份额：系数约 +0.02，CI 宽；B4 未获支持。  
- 人力资本 Chow：`Δslope_1450 − Δslope_1290 ≈ 0.003`，CI 下限 > 0 → **可裁决**「至少在该序列上，1450 斜率变化强于 1290」。

### 5.4 B1 猎证进度

Ilardi 点名佩戴表已扩至十余名；与本地 P800 缓存对接后仍仅少数有日期作品。活 SPARQL 微面板（Petrarch/Filelfo/Lotto）方向偏「证据前著作更多」，**n 不足**。  
**下一步硬任务：** EMLO/书信；更多遗嘱库存；宫廷订单收件人×著作年表；目标 core n≥20。

### 5.5 发明史日期（纠错）

Giordano 布道：**1306-02-23**（现代纪年）；佛罗伦萨 Annunciation 纪年写作 **1305-02-23**。**不是** 1305-02-29，也**不要**称「公历」（格里高利历 1582 后）。发明传统推算约 **1285–1286**。

伪「1305 佛罗伦萨商人遗嘱」已 debunk（缝合条目）。

### 5.6 SDBM

多城「后/前」事件比：Venice/Bologna 升、Paris/Oxford 降、峰值多在 1450——与「眼镜制造中心 1300 独有产出跃迁」不符。计量对象是**记录事件**。

---

## 6. 讨论

宏观代理失败**不能**偷换成「眼镜对个人无用」。纸张、印刷、计算机都是大众工具，仍可对部分知识劳动者产生大边际。  
B2/B4 未获支持 + A1/A2 成立，逼出真正缺口：**B1 个体识别**——这是下一阶段研究议程，不是修辞终点。

---

## 7. 结论

1. **A1 支持**（分结局写 RCT）。  
2. **A2 可信，效应年数未知**。  
3. **B2/B4 宏观强版未获支持**；时点上印刷侧更强（该 HC 序列上正式 Δ 检验）。  
4. **B1 未识别 → 必须继续猎证**（不得写成已拒绝，也不得写成不可知）。  
5. **C：** 文明唯一起点 debunk；+15 年句在 Chicago **p.145**（作者原句已核）；该量化是否成立仍靠 B1 等证据，不能用页码代替检验。

**定稿表述：**

> 开放数据支持「老花矫正改善近距劳动」的现代机制，并支持中世纪眼镜作为可扩散近距工具的历史叙事；不支持「制造中心知识优势 / 45+ 份额系统性上升 / 眼镜宏观断点强于印刷」等强宏观解锁版。佩戴者是否因此多工作若干年，现有面板尚未识别——这是证据问题，要用更大的佩戴×产出样本来裁决，而不是用模糊措辞收场。

---

## 8. 复现（可选）

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/07_run_all.py
```

核心表已写入正文逻辑；仓库另有 `outputs/tables/`。声明：**作者自测可复现**。

---

## 参考文献

- American Statistical Association (2016). Statement on Statistical Significance and P-Values. *The American Statistician*. https://doi.org/10.1080/00031305.2016.1154108  
- Buringh, E., & van Zanden, J. L. (2009). Charting the “Rise of the West”. *Journal of Economic History*.  
- Davidsohn, R. (1901). *Forschungen zur Geschichte von Florenz*, III.  
- de la Croix, D., et al. RETE / CDMV scholar and city data. https://perso.uclouvain.be/david.delacroix/rete.html  
- Ilardi, V. (2007). *Renaissance Vision from Spectacles to Telescopes*. American Philosophical Society.  
- Macfarlane, A., & Martin, G. (2002). *Glass: A World History* / *The Glass Bathyscaphe*. Chicago / Profile.  
- Reddy, P. A., et al. (2018). PROSPER. *Lancet Global Health*. https://doi.org/10.1016/S2214-109X(18)30329-2  
- Rosen, E. (1956). The Invention of Eyeglasses. *J Hist Med Allied Sci* 11(1):13–46; 11(2):183–218.  
- Seewooraduth et al. / THRIVE (2024). *PLOS ONE*. https://doi.org/10.1371/journal.pone.0296115  
- PROSPER II (2025). *British Journal of Ophthalmology*. https://doi.org/10.1136/bjo-2025-328563  
- Studium Parisiense database documentation.  
- Jenks, S. London customs accounts (spectacles imports; see curated trade tables).  

*数值以仓库流水线重跑为准；仅读本文时以正文表为准。*
