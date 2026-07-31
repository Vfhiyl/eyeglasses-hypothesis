# B1 证据狩猎清单

**命题：** 实际佩戴眼镜的年长读写者，是否比未佩戴者多完成若干年近距知识劳动？  
**状态（2026-07-31 深夜）：** region 表 SPARQL 重建完成；René 法国统治者对照加密；primary **n=36**，中位 Δ **−0.75**，CI **[−3.0, 3.3]**（仍排除 +5/+15）。见 `b1_free_roam_2026-07-31_rene_orleans_densify.md`。  
**Macfarlane 原句：** 已核（Glass p.145）= 专业脑力劳动者可用近距工作年限 +15 或更多 — **书中有句 ≠ 史实已证**。

### Roster 普查主表（用这些，不用 hard 均值）

| 表 | 路径 |
|----|------|
| 全员编码 | `outputs/tables/b1_roster_census.csv` |
| 分布摘要 | `outputs/tables/b1_roster_census_summary.csv` |
| 对照匹配 | `outputs/tables/b1_roster_control_matches.csv` |
| 对照 SESOI | `outputs/tables/b1_roster_control_summary.csv` |
| 方法说明 | `outputs/tables/b1_roster_census_2026-07-31.md` |

## 面板一览（2026-07-24）

| 资产 | 结果 |
|------|------|
| 具名佩戴者 | 38（高/中 33；QID 26） |
| **P50∪P800 合并** | **core n=6** → `adequate_direction_sample` |
| mean share_after（core） | ≈ **0.13** |
| mean age_delta（core） | ≈ **−15.6** |
| LetterSampo / EMLO | 无 ≤1600 spectacles 命中 |
| **Alessandra 书信编年** | Guasti OCR：67 封有日期；戴镜自述 1465 后仍写信至 1470（+5y）；rate↑ 但有版本密度偏误 |
| **Datini** | Prato 数字库已通：`datini.archiviodistato.prato.it`；F.721/713 订镜信 **ASPO 定位+原图已下**（Piaciti/Gaddi 1400）；元数据搜 ochiali=0（正文未标引）；Origo 1402 赠镜；Mazzei 至 1410（+10y） |
| **存活年数（onset-ish）** | n=16；median **+10y**、mean **+12y**；≥15y 占 6/16 — **只是死后上限，不是多干的近距劳动年** |

**读法：**

1. Wikidata 著作日**不**支持「戴镜证据年后代表作涌入」的晚解锁强版。  
2. 书信个案（Alessandra）支持「戴镜证据后仍持续近距读写数年」。  
3. 存活 +10–12 中位年与口号 +15 **同量级但不可等同**；证据年往往偏晚（已戴多年才入档），会**低估**真实佩戴跨度、**高估**「证据后新解锁」年数。  
4. **仍缺**：同 SES 未佩戴对照池；SESOI（建议预注册 ≥5 年近距劳动）；n≥20 有日期活动序列的佩戴者。

### 主表路径

| 表 | 路径 |
|----|------|
| P50∪P800 | `outputs/tables/b1_wearer_p50_p800_panel.csv` |
| 活动代理（4 人） | `outputs/tables/b1_activity_proxy_panel.csv` |
| Alessandra | `outputs/tables/b1_alessandra_letter_chrono.csv` |
| Mazzei→Datini | `outputs/tables/b1_mazzei_letter_chrono.csv` |
| Datini 事件 | `outputs/tables/b1_datini_event_timeline.csv` |
| 证据后存活 | `outputs/tables/b1_years_alive_after_evidence.csv` |

脚本：`scripts/17_b1_sparql_panel.py`（需你已开的 `https_proxy`）

## 对照池（设计，未建库）

**目标：** 估计「有佩戴证据」相对「无佩戴证据」的额外近距活动年数（不是寿命）。

| 要素 | 草案 |
|------|------|
| 处理组 | roster 中 high/medium，evidence_type ∈ self_report / order_request / account_wear（排除纯死亡清单） |
| 对照 | 同世纪、同职业大类（humanist / merchant / ruler / cleric）、同出生±10y，**档案中无** occhiali/spectacles 命中 |
| 结果 | 首选：有日期书信/著作的末次活动年 − 首次成年活动年；次选：死亡年 − 45（presbyopia 窗口起点） |
| SESOI | 预注册：**+5 年**近距活动（方向）；**+15** 仅作 Macfarlane 原句检验，需 n≥20 且效应稳健 |
| 偏误 | 佩戴者更可能被史家记下眼镜 → 对照「无记录」≠「未佩戴」；用职业×档案厚度分层 |

## 下一步 ROI（不需你动手的我会继续做）

1. 继续挖开放语料扩 hard series（目标 n≥20）  
2. **存在但本机打不开**才记入 `outputs/tables/b1_exists_but_blocked_for_agent.csv` 再找你  
3. **不会**启停 gateway

**Gateway：** 只使用你已启动的代理；本仓库规则禁止助手启停 gateway。

### 存在但 agent 打不开（暂不喊你）

| 项 | 状态 |
|----|------|
| Cherubini Ammannati PDF 三卷 | 站上有；本机 TLS/502；已有 ELENCO 够用 |
| Sverzellati Aevum Tranchedini | 付费；**Ferrari GSL 已替代**入 hard（+17y） |
| Pirckheimer Bd.6–7 | 纸书存在；**无**免费数字化全文 |


## Datini 数字库（2026-07-24）

- 正站：http://datini.archiviodistato.prato.it/la-ricerca/（**不要**用 firenze 子域）
- 卷宗：`outputs/tables/datini_busta721_catalog.csv`、`datini_busta713_catalog.csv`
- 订镜对齐：`outputs/tables/datini_ochiali_letter_dossier.csv`；原图在 `data/raw/datini_prato/images/`
- 元数据 `ochiali`=0 / `occhiali`=1（无关）；**正文未 OCR 入检索**

## 对照池 v2（2026-07-24）

- 候选：`outputs/tables/b1_control_candidates_v2.csv`（作家/诗人/史家等出生队列，不在 Ilardi roster；n≈208）
- 活动比较（清洗后）：`b1_treatment_control_activity_panel_clean.csv` / `b1_treatment_control_summary_clean.csv`
- **清洗结果：** treatment **n=3–4** vs control **n=15**；`years_work_after_45` 中位差约 **+8**（过方向 SESOI +5 的原始中位差，**远未过 +15**，且 n≪20）
- **读法：** 弱提示方向、**不能**确认；名人佩戴者 WD 偏误 + 对照未档案验阴；Macfarlane +15 仍未立

## Filelfo

Rosmini《Vita》显示 **1456 订镜后至 1481** 仍有持续著述/书信活动记载（+25y 存活且有年份事件），补强「未停笔」方向，但不能量化多了几年。

## Lotto Libro di spese（2026-07-24）

- OA 文本已下：`data/raw/lotto_libro/`（De Carolis 2017 OpenstarTs）
- 账本跨度约 **1540–1556**（证据年≈开账）；文中有多处 **ochiali** 购置
- 计入硬活动序列：`years_after_evidence=16`

## 硬活动序列计数

当前 hard dated series：**13** — 仍远低于 n≥20。面板：`outputs/tables/b1_activity_proxy_panel.csv`。

| person | years_after_evidence | proxy |
|--------|---------------------:|-------|
| alessandra_strozzi | 5 | Guasti letters |
| datini | 10 | Mazzei→Datini |
| petrarch | 10 | WD P50∪P800 |
| filelfo | 25 | Rosmini Vita years |
| ammannati | 6 | Cherubini elenco |
| gonzaga_ludovico | 13 | Luzio–Renier + Ilardi letter quotes |
| leo_x | 8 | Pastor vols 7–8 dated briefs/letters |
| lotto | 16 | Libro di spese |
| pirckheimer | 9 | Allen–Erasmus corr. |
| tranchedini | 17 | Ferrari GSL memoriale |
| bianca_maria | 6 | Nicoud MEFRM 2000 Persée letters |
| lorenzo_medici | 11 | Ross 1910 Medici correspondence OA (strict n=8) |
| cederni | 24 | Ilardi 1454 orders + Sepoltuario civic posts |

## Pirckheimer（2026-07-24 续）

- Bd.2（用户提供）：~1507–1515，**证据前**
- **Bd.6/7：** 网上无开放全文（Beck 2004/2009 版权）；Heidelberg 仅 Bd.2；IA/GB 无 Full View — hunt：`outputs/tables/pirckheimer_bd67_digital_hunt.csv`
- **开放替代（已抓）：** Allen *Opus epistolarum* vols 4–8 OCR → 与 Pirckheimer 往来至 **1529**（+9y）；表：`b1_pirckheimer_allen_erasmus_chrono.csv`
- Bd.1（1940）MGH PDF 已下：`data/raw/pirckheimer/pirckheimer_bd1.*`（早期信）
- Goldast 1665 Opera OCR 已下（后期年份命中稀疏）

## Ammannati（CLOSED 2026-07-24）

- **Tomo III PDF（用户完整本）**：`data/raw/ammannati/ammannati_cherubini_tomo3.pdf`
- 戴镜信钉死：**n.653，1473-04-25，Roma → Lorenzo**；*occhiali… da lungha et da presso*（Donato Acciaiuoli）
- 活动至 **1479-08-08（n.987）** ≈ **+6y 3m**；表：`b1_ammannati_tomo3_letter_chrono.csv`、`b1_ammannati_occhiali_letter_653.csv`
- Tomo I/II 缺件：**不再追**（III 已覆盖证据后时段）
- 1506 印本已有 OCR，劣于 Cherubini，不重复加工

## Tranchedini（2026-07-24）

- **开放替代（已抓）：** *Giornale storico della Lunigiana* IA OCR  
  - 1912–13：Sforza/Ferrari *Una biblioteca pontremolese*（memoriale 书目 1466–1475）  
  - 1914–15：Ferrari *Inventari… a Nicodemo Trincadini*（1468–1479 编年笔记；**1470-07-26** *scatola piena de ochiali fini*；**1472-06-16** *parechie paia de ochiali*）  
  - 原文：`data/raw/tranchedini/*_djvu.txt`；编年：`outputs/tables/b1_tranchedini_ferrari_memorial_chrono.csv`
- 戴镜证据年仍用 Ilardi **1462**；活动至 **1479-08-08** ≈ **+17y** → 计入 hard series
- Sverzellati *Aevum* 外交书信仍付费（blocked 表）；Ferrari 已够做活动代理，不阻塞

## Gonzaga Ludovico（2026-07-24）

- **开放摘录：** Luzio–Renier *I Filelfo… Gonzaga*（GSLI 16, 1890）全文 OCR：`data/raw/gonzaga/GiornaleStoricoLettItal1890_djvu.txt`
  - **1466-03-14** Abate Bessarion（S. Benedetto）送两副 *ochialli*；文中称 Lodovico 约 1466 起视力衰退但仍爱读书、用好眼镜
- Ilardi 钉死：**1460-02-13**→Lochner 自述每日读信戴镜；**1473-03-07**→Saggi 仍戴（+13y）
- 编年：`b1_gonzaga_ludovico_spectacle_reading_chrono.csv` → **hard +13y**（薄：出版引文，非完整 carteggio）
- Leverotti *Oratori mantovani* 16 卷仍无 OA；Portioli *Petriolo* IA 未命中

## Leo X（2026-07-24）

- Pastor *History of the Popes* vol.7–8 OCR：`data/raw/leo_x/`
- 编年摘录：`b1_leo_x_pastor_dated_docs.csv`（约 40 条 1513–1521 教宗文书引用）→ **hard +8y**
- Magliana 猎场 *occhiale*：更像狩猎用单筒，不当作近用阅读证据

## 死亡库存佩戴者（CLOSED — 无法做戴后活动序列）

证据年=死亡年 → `years_after_evidence=0`，不入 hard：

| person | 证据 | OA 已核 |
|--------|------|---------|
| stapeldon | 1326 遗嘱库存 *pair of spectacles* | Register OCR：`data/raw/stapeldon/` |
| magnavia | 1365 库存 *occhiale de cristallo*×2 | Fumi 1894 IA：`data/raw/magnavia/`；表 `b1_magnavia_fumi_occhiale_inventory.csv` |
| orsi | 1322 库存镀金银框 | Davidsohn *Geschichte* v4.2 OCR：`data/raw/orsi/` |

## Cederni（2026-07-24 升 hard）

- Ilardi 引 Caccini→Cederni **1454-06/07** 信：6 副近/远用镜，**确认自用**（非转售）
- OA 戴后活动（非本人书信全集）：Sepoltuario IATH — 墓 ~1456；Neri 祭坛画 **1461-08-17**；**Prior 1473**；**Buonuomo 1478**；卒 ~**1482-12**
- 编年：`b1_cederni_activity_chrono.csv` → **hard +24y**（末公务 1478）
- Corti–Kent 1991 仍版权；本人去信多佚 — 公务岗位作近距代理

## Lorenzo de' Medici（2026-07-24 新入 hard）

- Ilardi 2007 n.94：*Lettere* IV (Rubinstein 1981) p.165 — **1479** 信自证用镜；Cerretani *vista corta*
- 现代 *Lettere* 全编 **版权**（Giunti）；OA 代理：Janet Ross *Lives of the Early Medici* (1910) IA OCR  
  - `data/raw/lorenzo_medici/ross_lives_early_medici_djvu.txt`  
  - 编年：`b1_lorenzo_medici_ross_letter_chrono.csv`（strict **8** 封；1479-09-11 → 1490-07-28）  
  - → **hard +11y**；已写入 roster `lorenzo_medici`
- Fabroni *Vita* 1784 / Roscoe 1825：续挖可加密编年

## Bianca Maria Visconti（2026-07-24 续 → hard）

- 佩戴证据：Tranchedini 1462-11-20 第三方报告（与 Francesco Sforza 同信；medium）
- **OA 密序列：** Nicoud, *Mélanges de l’École française de Rome* 112 (2000) Persée 全文  
  - 1468-05-23 → 1468-09-30：**38** 封 *from* Bianca Maria（政务/家书近距读写）  
  - 表：`b1_bianca_maria_letter_chrono.csv`；原文缓存：`data/raw/bianca_maria/nicoud_2000_persee.txt`
- Covini *Reti Medievali* 2009 OA PDF 已下并 OCR：`data/raw/bianca_maria/covini_2009*`（引 1465/1467 书信；附录未全抽）
- → **hard +6y**（证据年 1462 → 末封 1468）

## Barbara Brandenburg（薄，未升 hard）

- 1466-09-18 → Federico 订 *ochiali assai*（Ilardi n.56）
- Nicoud 1468：**3** 封 Barbara → Bianca（末封 1468-10-03）→ OA 活动仅 **+2y**
- Fantoni *Libri e documenti* 7 (1981) 129 regesti（1452–1468）存在但本机未拿到全文 — 记 blocked 可选
- 存活至 1481 = +15，但缺 1469–1481 OA 密编年 → **hard=False**

## 本轮试过仍无 hard 增量

- Cederni：Corti–Kent 1991 **版权**；本人书信几乎佚失 → blocked 表
- Policastro / Arduino：无 OA 密书信；Arduino 死后仅 +3y
- Wolsey：LP OCR 已下；礼物 1527→死 1530 最多 **+3y**，暂不入 hard
- Filippo Strozzi：*Vita* 1851 有 1480–91 活动，但佩戴 onset 仅 medium/约估 → 不升 hard
- Gonzaga Copialettere 全本：ASMn 库内，**无**完整 OA 数字化信集
- OpenEdition Chittò / books.openedition.org：本机 TLS 失败（可记 blocked）

## 下一步（续猎）

hard 现 **n=13** ≪ 20；中位约 +10；≥15 现 **4/13**。继续扫冷门 OA；存在但打不开才记 blocked。

## Session continue (2026-07-24e) — free hunt

- **Simonetta diari (Natale 1961) OA** downloaded: `data/raw/policastro/simonetta_diari_natale_djvu.txt`  
  - Confirms Policastro death **1478-08-26** still *castellano de Viglevano*; **no** intermediate dated castellan acts in diary → still hard=False (survival-only).
- **Wyatt LP densify:** vol.4 pt.3 (`11332111bsb`) + vols 10/12 + addenda OCR.  
  - Treasurer activity clear to **14 Feb 1530** (with Tuke succession); enfeoff licence **6 Apr 1531**; death by **1 Feb 1537** (son’s livery).  
  - Dense near-work window post-gift ≈ **+3y** (to 1530) — **not** hard (same class as Wolsey).
- **Antenhofer 2013** *Barbara Gonzaga Die Briefe* = **daughter** (Württ. 1474–), not marchesa Brandeburgo; may embed mother letters but **copyright** → blocked (clarified).
- **Tordi 2 / Bese Ardinghelli:** scholarly OA fulltext of quaderno still missing → blocked.
- **OpenEdition Chittò:** Anubis + TLS; ends 1468 anyway.
- **Hohenzollern-Jahrbuch** Google OCR dump useless for Barbara.
- hard **n still 13**; continue OA hunt.

### Filippo Strozzi / Wyatt densify (same session)

- Sepoltuario **#1148** Filippo di Matteo Strozzi: birth 1428-07-10; Calimala consul **1484**; Prior **1485**; Calimala **1488**; death **1491-05-14**. Chrono: `b1_strozzi_filippo_sepoltuario_chrono.csv`. **→ HARD +25y** after Guasti 1464 onset pin (see below).
- Wyatt LP chrono: `b1_wyatt_henry_lp_chrono.csv` → dense treasurer window **+3y** only → soft/not hard.
- Bese Ardinghelli: not found as Sepoltuario individual under Bese/Ardinghelli searches; Tordi 2 still blocked.

### Filippo Strozzi → HARD (same session continue)

- **Onset pinned:** Guasti Lett. XXVIII, Florentine 22 Mar 1463 = **modern 1464-03-22**: Alessandra buys *occhiali e de' più fini, come tu di'* for Filippo in Naples; Lett. XXIX notes payment. Ilardi 2007: personal use; later calls him *spectacle wearer himself*.
- Roster: `evidence_year=1464`, confidence **high**, type `order_request_via_mother`.
- Post-wear OA chrono (Vita 1851 + Sepoltuario #1148): Napoli act 1469; purchases/patronage 1473–78; Calimala **1484/1488**; Prior **1485**; Palazzo fabbrica **1489**; death 1491.
- → **hard +25y** (1464→1489). hard **n=14**; ≥15 now **5/14**.

### Barbara densify (soft only)

- Ferrari *Scriver dei figli* OAPEN quotes **Barbara→Federico 1478-11-24** (ASMn AG b.2103bis doc.558).
- Soft years_after **12** (1466→1478); still hard=False (thin mid-1470s gap). Chrono: `b1_barbara_oa_letter_chrono.csv`.

### Barbara Lindbæk densify (soft)

- Lindbæk 1902 (tidsskrift.dk OA) cites Hofmann 1881: Barbara→Albrecht Achilles **1471**, **1474-03-24**; weaker ~1472 Dorothea envoy.
- Chrono: `b1_barbara_oa_letter_chrono.csv`; notes: `b1_barbara_hunt_notes.md`.
- Still **hard=False** (thin); years_after **12**.

### Policastro mid-career hunt (soft)

- Pre-wear Registro 9 acts found; mid 1461–1477 still lacks dense OA near-work.
- Notes: `b1_policastro_hunt_notes.md`; chrono: `b1_policastro_activity_chrono.csv`. **hard=False**.

### Barbara Brandeburgo → HARD

- **Hofmann 1881 FOUND OA** on MDZ/BSB `bsb11473927` (earlier “vol.41 missing” assumption wrong).
- FROM-Barbara Beilagen: **1471-07-05, 1473-11-06, 1474-03-23, 1475-09-12, 1479-11-11** (+ Nicoud 1468 + Ferrari 1478).
- → **hard +13y** (1466→1479). Chrono: `b1_barbara_oa_letter_chrono.csv` / `b1_barbara_hofmann_letter_chrono.csv`.
- hard **n=15**; ≥15 still **5/15** (Barbara +13 < 15).

## Session continue (2026-07-24g) — next hard path triage

- Goal: add another HARD dated series (n=15 → toward ≥20).
- **LBC Reg.9 post-wear (9.223–257) + after-n.9 lane:** scraped; **0** Policastro/Viglevani hits. LBC = Francesco I regs 1–16 only → **no** Galeazzo 1467 OA primary. Policastro mid-career LBC path **closed**.
- **Santoro 1948 p.617:** still no OA quote; remains blocked (library/microfilm scan).
- Other Ilardi mediums (Magnia friars, Bartholomeus, Neri Mici, Barbaro low): **no** OA post-wear hard series this pass.
- Early medium deep-dive (`neri_mici` / `bartholomeus_padua`): still **no** birth–death or multi-point post-wear OA; Barbaro Dispacci **pre**-1476 letter — **no** hard. Notes: `outputs/tables/b1_early_wearers_hunt_notes.md`.
- Arduino / Sforza short windows: skip (unchanged).
- → **hard n still 15**; no panel/roster ingest. Notes: `outputs/tables/b1_next_hard_hunt_notes.md`.

## Session continue (2026-07-24h) — early medium wearers

- Deep hunt: `neri_mici` (Davidsohn Forschungen III nr.955) + `bartholomeus_padua` (Zecchin via Ilardi).
- **Neither** has birth/death OA pins or multi-point post-wear near-work → **no hard ingest**.
- Barbaro: Manni 1476 letter **after** Corazzol Dispacci 1471–73 (wrong order); wear **low** → do not hard-ingest.
- → **hard n still 15**. Notes: `outputs/tables/b1_early_wearers_hunt_notes.md`.

### Session stuck note 2026-07-24f

- hard **n=15** (median 11.0; ≥15: 5/15). Macfarlane +15 still unproven.
- New hard this session: **strozzi_filippo +25** (Guasti 1464 onset); **barbara_brandenburg +13** (Hofmann 1881 MDZ).
- OA mid-career for **Policastro** exhausted on LBC; remaining unlocks mostly library: Santoro 1948 p.617, ASM Pavia cart.757, Tordi 2, Vangelista fol.162r.

### Free roam Baye / France (2026-07-31)

- **Nicolas de Baye** (Q3340895): Tuetey Journal petition Nov 1416 — cannot *enregistrer* without *lunettes*. Soft +2y (conseiller 1417 → proscription 1418). Chrono: `b1_nicolas_de_baye_chrono.csv`.
- Opened **france** primary cell; curated Gerson / Clamanges / Christine / Fusoris / Premierfait. Christine region override (Venice birth ≠ Italy career).
- Restored **Henry VIII** onsetish (Ilardi had been blocking as probate).
- Primary n=**33**; median Δ **−1.0**; CI **[−4, 0.6]**; SESOI +5/+15 still FAIL. Note: `b1_free_roam_2026-07-31_baye_france.md`.

### Thin-cell densify (2026-07-31)

- Injected Italy rulers (Montefeltro, Malatesta, Montferrat, Ercole I, Visconti, Gianfrancesco) + clerics (Sadoleto, Contarini, Paul III, Bembo, Bibbiena, Clement VII); Giles/Cajetan bucket→cleric.
- Gonzaga n_ctrl 1→4; Barbara 1→5; Leo X 1→9. Primary n=33; median Δ −1.0; CI [−4, 0.6]; SESOI still FAIL.
- Note: `b1_free_roam_2026-07-31_thin_cell_densify.md`. Leonello d'Este removed (d. age 43; stole Sforza strict match).

### Free roam Philippe le Hardi (2026-07-31)

- Prost t.II §8240 OA: **1389-08-14** «estuy à bericles pour luy» (Jehan de Baugis, Paris). Soft +15y to death 1404. Chrono: `b1_philippe_le_hardi_chrono.csv`.
- France ruler densify: Jean de Berry + Amadeus VI. Charles V inventory estrin logged only (not onsetish).
- Primary n=**34**; median Δ **−1.0**; CI **[−4, 0.6]**; SESOI still FAIL. Note: `b1_free_roam_2026-07-31_philippe_hardi.md`.

### Laborde dig + Charles d’Orléans (2026-07-31)

- Philippe densify: Laborde glossaire **1403** Dijon plate for lunettes in ducal book (still living; d.1404).
- **Charles I d’Orléans** (Q310146): 1454 `estuy de lunectes` (Laborde J / Ducs de Bourgogne 6789). Soft +11y. Chrono: `b1_charles_orleans_chrono.csv`.
- Primary n=**35**; median Δ **−1.0**; CI **[−4, 2.0]**; SESOI still FAIL. Note: `b1_free_roam_2026-07-31_laborde_orleans.md`.

### Region rebuild + René densify (2026-07-31)

- Rebuilt wiped `b1_person_macro_region.csv` via SPARQL; primary recovered **n=1 → 36**.
- **René II**: injected Gilbert Montpensier / Louis II Trémoille / Charles Berry (Berry `use_in_primary=False`); match → occ+birth+region; primary Δ **−25.5 → −2.0**.
- Removed Philip the Good + Jeanne d’Évreux from candidates (logged only) so Philip returns as Orléans control; Orléans Δ **+13**.
- Primary n=**36**; median Δ **−0.75**; CI **[−3.0, 3.3]**; SESOI still FAIL. Note: `b1_free_roam_2026-07-31_rene_orleans_densify.md`.
