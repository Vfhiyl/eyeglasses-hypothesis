# B1 证据狩猎清单

**命题（劳动年）：** 实际佩戴眼镜的年长读写者，是否比未佩戴者多完成若干年近距知识劳动？  
**状态（2026-08-12 审计纠正）：** 劳动年 primary **n=60**，Δ **+3.0**，CI **[−2.0, 9.0]** → +5/+15 **FAIL**；冻结 36 人子集 Δ **+1.0**，CI **[−3.0, 5.6]**。pass BC–FI 曾报 Δ=+11.5 PASS_RAW，经审计确认为 outcome-aware 策展制造，**已撤回**（见 `docs/B1_CURATION_AUDIT_2026-08-12.md`）。  
**命题（出成果 / B1-Output）：** 45+ 有日期成果跨度是否多 +5/+15？→ n=44，中位 Δ **+3.75**，CI **[−2.0, 8.0]** → +5/+15 **FAIL**（同批撤回后的纠正值）。  
**Macfarlane 原句：** 已核（Glass p.145）= 专业脑力劳动者可用近距工作年限 +15 或更多 — **书中有句 ≠ 史实已证**；+15 在所有臂、所有时期 FAIL。  
**对称敏感性（2026-08-12）：** `b1_symmetry_sensitivity.csv` — 双侧去"到死"端点 Δ=+0.5；主张领域内（≤1600）Δ=+2.0；最严格领域内子集 Δ=−6.75；方向对口径高度敏感。人内初版见 `b1_within_person_rates.csv`（exploratory）。

### R1 组合抬分（2026-08-22；Wave 3 2026-08-28）

不只追 ≥5 严格锐利（破镜/退货）。全 roster 用 `outputs/tables/b1_wearer_lift_scoreboard.csv` 打 0–100 分档；脚本 `38_b1_wearer_lift_scoreboard.py`。中档 soft episode（订单/自报 + 已有编年）写入 `b1_episode_registry.csv` 的 `SOFT_*` 行，**不**计入严格锐利解冻条；薄档 YA0/soft-stock 写 CLOSED/PIN 地板（`b1_lift_thin_tier_2026-08-22.md`）。**Wave 3：** 再抬 8 人 55–69→70–84（Ammannati / René / Bianca Maria / Azevedo / Ardingelli / Charles d'Orléans / Nicolas de Baye / Tranchedini）；见 `b1_lift_wave3_2026-08-28.md`。**Wave 4：** 再抬 16 人（`b1_wave4_soft_episodes.csv` / `b1_lift_wave4_2026-08-28.md`）。**Wave 5：** +9 soft +9 薄档地板 = 18（`b1_lift_wave5_2026-08-28.md`）。**Wave 6：** +3 soft +17 薄档；0–19 已清空（`b1_lift_wave6_2026-08-28.md`）。**Wave 7：** +15 新具名入册、0 升档（`b1_lift_wave7_2026-08-28.md`）；roster 107→122。**Wave 8：** 再 +15 新具名、0 升档（`b1_lift_wave8_2026-08-29.md`）；roster 122→137。**Wave 9：** +14 CLOSED 地板升档 + Dudley 1 新（`b1_lift_wave9_2026-08-29.md`）；roster 137→138。**Wave 10：** +1 CLOSED（Dudley）+ 14 新具名（`b1_lift_wave10_2026-08-29.md`）；roster 138→152。**Wave 11：** +12 CLOSED（Wave 10 薄档）+ 5 新具名（`b1_lift_wave11_2026-08-29.md`）；roster 152→157。**Wave 12：** +5 CLOSED（Wave 11 薄档）+ 10 新具名（`b1_lift_wave12_2026-08-29.md`）；roster 157→167。**Wave 13：** 出生<1700 筛选集上 +15 新具名、0 升档（`b1_lift_wave13_2026-08-29.md`）；筛选 127→142；全库 167→182。**Wave 14：** 出生<1700 筛选集上 +13 CLOSED 升档 + 2 新具名（`b1_lift_wave14_2026-08-29.md`）；筛选 142→144；全库 182→184。**Wave 15：** 出生<1700 筛选集上 +2 CLOSED 升档 + 13 新具名（`b1_lift_wave15_2026-08-29.md`）；筛选 144→157；全库 184→197。**Wave 16：** 出生<1700 筛选集上 +10 CLOSED 升档 + 5 新具名（`b1_lift_wave16_2026-08-29.md`）；筛选 157→162；全库 197→202。**Wave 17：** 出生<1700 筛选集 40–100 档 +14 升档 + 1 新具名落地≥40（`b1_lift_wave17_2026-08-30.md`）；筛选 40–100：43→58。**Wave 18：** 出生<1700 筛选集 40–100 档 +13 升档 + 2 新具名落地≥40（`b1_lift_wave18_2026-08-30.md`）；筛选 40–100：58→73。**Wave 19：** 出生<1700 筛选集 40–100 档 +14 升档 + 1 新具名落地≥40（`b1_lift_wave19_2026-08-30.md`）；筛选 40–100：73→88。

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

## Pirckheimer（2026-07-24 续；2026-08-22 HARD_TO_FIND）

- **整套 *Willibald Pirckheimers Briefwechsel*（Beck/Reicke–Scheible）很难找：** 订购锚点所需 **Bd.4–6** 无开放全文；远程检索已关（IA 0；Heidelberg 早期卷；Beck 店页无公开 Inhalt PDF；GB Bd.5 预览仅卷首/目录碎片且无 Brille；Persée 全是脚注引用）。**勿再做网页挖矿** — 仅图书馆纸书或 Ilardi 引文可解锁。Hunt 表：`outputs/tables/pirckheimer_bd67_digital_hunt.csv`
- Bd.2（用户提供）：~1507–1515，**证据前**
- **Bd.6/7：** 网上无开放全文（Beck 2004/2009 版权）
- **开放替代（已抓）：** Allen *Opus epistolarum* vols 4–8 OCR → 与 Pirckheimer 往来至 **1529**（+9y）；表：`b1_pirckheimer_allen_erasmus_chrono.csv`
- Bd.1（1940）MGH PDF 已下：`data/raw/pirckheimer/pirckheimer_bd1.*`（早期信）
- Bd.5 GB 预览已留：`data/raw/pirckheimer/bd5_google_preview/`（仅卷范围 1522–1525，无眼镜）
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

## Cederni（2026-07-24 升 hard；2026-08-22 R1 episode）

- Ilardi 引 Caccini→Cederni **1454-06/07** 信：6 副近/远用镜，**确认自用**（非转售）
- **锐利弧：** 1454-06-20 寄出 → **07-05 退回 3 副不合格** → 07-12 换新合格（Ilardi n.78–79）
- R1：`cederni_1454_return` ANALYZABLE_NOW（`b1_cederni_1454_episode_method.md`）
- OA 戴后活动：Sepoltuario — 墓 ~1456；Neri **1461-08-17**；**Prior 1473**；**Buonuomo 1478**；卒 ~**1482-12**
- 编年：`b1_cederni_activity_chrono.csv` → **hard +24y**；本人去信多佚 — 公务岗位作近距代理
- Corti–Kent 1991 仍版权；Ilardi 引文够钉 episode

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

## Barbara Brandenburg（2026-07-24 薄；2026-08-22 soft R1）

- 1466-09-18 → Federico 订 *ochiali assai*（Ilardi n.56）
- R1：`barbara_1466_order` **SOFT_ORDER**（`b1_barbara_1466_episode_method.md`；OA letter chrono → 1479）
- Nicoud 1468：**3** 封 Barbara → Bianca（末封 1468-10-03）；Fantoni regesti 仍可选 blocked
- 存活至 1481 = +15；soft episode 已入组合抬分，非严格锐利

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

### Free roam Heymann → Denis Hesselin (2026-07-31)

- Heymann IA `b2486092x`: Paris city comptes **1473–74** *lunettes clouants* for Prévôt **Denis Hasselin/Hesselin** (already owned non-riveted pair). Soft +32y to Receveur des Aides terminus 1506 (Pattou; death after 1506).
- France clerk densify: Bourré / le Daim / Robertet / Fumée / Briçonnet. Hesselin Δ **+17**.
- `egidio_piacenza` region override → italy (Δ −26 → +1).
- John Baret 1463 silver-gilt spectacles bequest logged only (gift to monk Ixnyng).
- Primary n=**37**; median Δ **0.0**; CI **[−2.5, 2.1]**; SESOI still FAIL. Note: `b1_free_roam_2026-07-31_hesselin.md`.

### England + Magnia HRE densify (2026-07-31)

- Heymann named-onset exhausted → densify thin England cells + fix `jacopo_magnia` unknown→**hre**.
- Henry/Wyatt/Wolsey → occ+birth+region; Wyatt Δ **+17** (Dudley+Empson); Wolsey n_ctrl **3** (Fisher/Colet/Tunstall); Magnia Δ **+8.5→−3**.
- Primary n=**37**; median Δ **−0.5**; CI **[−3.0, 4.5]**; SESOI still FAIL. Note: `b1_free_roam_2026-07-31_england_hre_densify.md`.

### Baye France clerk densify (2026-08-01)

- OA named-onset dry → densify `nicolas_de_baye`: Fusoris→clerk; +Montreuil +Jouvenel → **occ+birth+region**; Baye Δ **−17**.
- van der Paele (van Eyck 1436) logged portrait-only; not promoted.
- Curated file briefly wiped by bad rewrite; restored (124 rows) + snapshot `b1_control_nearwork_chrono_curated.snapshot_2026-08-01.csv`.
- Primary unchanged: n=**37**; median Δ **−0.5**; CI **[−3.0, 4.5]**. Note: `b1_free_roam_2026-08-01_baye_densify.md`.

### Domenichi + Henry densify (2026-08-01)

- OA roam dry → densify extreme/thin cells.
- Domenichi: +5 primary curated peers (Grataroli/Visdomini/Rasario/Figliucci/Borro); Δ **−17.5→−12**, n_ctrl **7**.
- Henry VIII: +Manners/Hastings/Neville (Courtenay excluded &lt;45); n_ctrl **1→4**, Δ **−5→+2**.
- Primary median **−0.5→0.0**; CI still **[−3.0, 4.5]**; SESOI FAIL. Note: `b1_free_roam_2026-08-01_domenichi_henry_densify.md`.

### Egidio / Azevedo / Wyatt densify (2026-08-01)

- IA roam SSL-fail → densify three thin/extreme cells.
- Egidio n_ctrl **1→9**, Δ **+1→−7**; Azevedo **−13.5→−10.5**; Wyatt **+17→+2** (Warham/Docwra).
- Primary median **0→−0.5**; CI **[−3.0, 2.1]** (upper &lt;5). Note: `b1_free_roam_2026-08-01_egidio_azevedo_wyatt.md`.

### Lotto densify after IA roam (2026-08-01)

- Direct IA tight personal-use queries: no birth-dated named onset.
- `lotto` n_ctrl **2→6**, Δ **+16.5→+12.5**; panel median/CI unchanged (−0.5; [−3, 2.1]). Note: `b1_free_roam_2026-08-01_lotto_densify.md`.

### Pirckheimer + Spinelli densify (2026-08-01)

- No new IA named onset; densify unmatched peers.
- Pirckheimer n_ctrl **2→6** (Δ still −4); Spinelli **−9.5→−2** (n_ctrl 5); merchant median **−0.98**.
- Panel unchanged: n=37; median −0.5; CI [−3.0, 2.1]. Note: `b1_free_roam_2026-08-01_pirck_spinelli_densify.md`.

### Batch densify (2026-08-01 cont.)

- Multi-cell curated fill; Pius II excluded as control; ya45=0 forced off primary.
- Primary: n=37; median Δ **−1.0**; CI **[−4.0, 2.0]**. Note: `b1_free_roam_2026-08-01_batch_densify.md`.

### R1–R8 多轮自治（2026-08-01）

- 命名 onset 猎捕 A–D（IA/Gallica/Heymann/Bourgeois/Manni）：**无新硬生卒个人佩戴者**。
- 薄格加密 + 极端格清洗 + 商人 OA-thin 降权；primary n=**37**，中位 Δ **0.0**，CI **[−3.0, 2.0]**。
- 冻结：`b1_round8_freeze.md` + curated snapshot `...snapshot_2026-08-01_r8.csv`。

### Phase2 二期多轮自治（2026-08-01）

- 新语料/账本面猎捕 + Guidotti：**无新硬生卒个人佩戴**；商人薄格高质量加固（Rucellai/Sassetti/Portinari）。
- 极端 Δ 标 structural；高频对照 spectacle-negative 抽检无污染；Latone/Nuno/Walmysford **永久附录关闭**。
- Primary n=**37**；中位 Δ **−2.97**；CI **[−4.0, 2.0]**；敏感性表仍 FAIL。
- 冻结：`b1_phase2_freeze.md` + `...snapshot_2026-08-01_phase2.csv`；轮次笔记 `b1_phase2_rN_*.md`。

### Digitarq óculos free roam (2026-08-01)

- Gateway + refreshed JWT; catalogued óculos-family hits → `data/raw/digitarq_free_roam/oculos_catalog.csv`.
- Best soft: Jacques Moser / Jaques maker (1552–62, b.≈1522) + nickname *O dos Óculos* (1603). **No hard wearer ingest.** Note: `b1_free_roam_2026-08-01_digitarq_oculos.md`.

### Digitarq layer-2 (2026-08-01)

- AdvancedSearch date filters not working via guessed POST body; Ilardi-orbit names dry for óculos.
- New soft: 1539 Contos office bulk buy of óculos (`PT/TT/CC/2/227/00107`) — unnamed officials, no ingest.
- Moser OCR sample failed; 1412 *lunetas* = Castelo da Luneta false friend.
- Note: `b1_free_roam_2026-08-01_digitarq_layer2.md`.
### Moser vision bio (2026-08-01 evening)

- Digitarq proc.5620 **m0012** vision: Jacques Moser, ~40 in 1562, Isabel Bernardez, *fazer oculos*, literate. Maker only — no promote.
- Notes: `data/raw/digitarq_free_roam/moser_1562_sample/VISION_READ_*.md`.

### FamilySearch Full-Text (2026-08-01 night)

- Gateway + `config/familysearch_session.local`; script `scripts/familysearch_fulltext_search.py`.
- UK∩1600 `spectacles` ≈102 (mostly wills); UK∩1500 **0**; 1300/1400 hits look like OCR false positives.
- Best soft bequests: Chester **1619** “my spectacles” (son John Cooke); Lancs **1631** Gilber spectacles+case; Cheshire **1616** spectacles+herball.
- **No hard-birth ingest** (will-path). Note: `b1_free_roam_2026-08-01_familysearch.md`; shortlist `familysearch_b1_shortlist.jsonl`.

### FamilySearch film browse + vision (2026-08-02)

- Film API + stitch: `scripts/familysearch_film_browse.py`; dgs `008470424` cached.
- Vision (not OCR) on Allerton neighborhood i=54–56: **Thomas Allerton**, Chester vintner, will **1615-04-25**; bequeaths **spectacles with brass case** to **Randall Holme**; wife Alice. i=56 = Appleton wrapper (unrelated).
- Still will-path only. Note: `data/raw/familysearch_fulltext/priority_images/VISION_READ_allerton_1615.md`.

### FamilySearch vision densify cont. (2026-08-02 evening)

- Stitch+vision: **Margaret Nugent** (Manchester widow, will 1620) silver spectacles; **George French** (inv. 1633 St Keverne) one pair; **Philip Oldfield** (inv. 1616) spectacles + herbal + Bibles; Herts 1642 inv. two pairs (testator TBD).
- Also **Elizabeth Martindale** (Bishopton Durham inv. 1670): spectacles + Latin books. PARES `anteojos` mostly modern military optics.
- Herts inv. `i=642` soft-named via neighbor will `i=639`: **James Cassell/Castell** (~1681/1691); film `008306986` cached.
- Named densify: **Thomas Smith** (Chester inv. 1682); **John Harrison** (Golborne/Winwick inv. 1681); **Bryan Travis** (Warrington inv. 1694, books + two pair). UK@1550 Full-Text still empty.
- No hard ingest. Note: `b1_free_roam_2026-08-02_familysearch_vision.md`.

### Letter-path pivot (2026-08-02 late)

- Left will densify; mined EMLO spectacles dump.
- Soft living wearers: **Anthony Wood** (fitted spectacles 1676 via Sheldon); **William Lynnet** bought pair London 1672; **Arthur Charlett** wear-duration ask 1707.
- PARES date filter still useless for 15–16c. Note: `b1_free_roam_2026-08-02_letter_mines.md`.

### Anthony Wood dig + promote (2026-08-02)

- Confirmed diary **9 Mar 1675**: “double pair of spectacles” from Ralph Sheldon (Clark *Life* II p.310); EMLO **27 Dec 1676** new-set + Wood self-draft on fit/lifelong use.
- Chrono: `b1_wood_anthony_activity_chrono.csv` → `years_after=17` (Athenae vol. II **1692-07-18**); panel hard-ingest; England 1630s humanist densify (12 peers).
- **PROMOTED:** onsetish + `occ+birth+region`; T=15; Δ=**−6.0**; primary **n=37→38**. Notes: `b1_free_roam_2026-08-02_anthony_wood.md`, `b1_free_roam_2026-08-02_wood_promote.md`.

### William Lynnet promote (2026-08-02)

- EMLO **7 Aug 1672**: self-report London spectacle purchase (Trinity fellow).
- Post-wear: Trinity Senior Dean 1677–84 / 1686–91; letter 1687; Vice-Master **1691–1700** → `years_after=28`; England cleric densify (n_ctrl=6).
- **PROMOTED:** T=32; Δ=**+1.5**; primary **n=38→39**; median **−2.97**; CI **[−4.0, 2.0]**; SESOI still FAIL. Note: `b1_free_roam_2026-08-02_lynnet_promote.md`.

### EMLO vocab free roam → letter-path close (2026-08-02)

- Expanded Solr: `lunettes` / phrase `"pair of spectacles"` / `spectacle maker` / etc. (cache `data/raw/emlo_free_roam_2026-08-02/`).
- **No new living named wearer.** Phrase hits collapse to Lynnet; `lunettes` = telescopes; Cole/Aubrey/Charlett-1716 closed as maker / historiography / third-party anecdote.
- **EMLO English letter seam closed** for practical B1 onset hunting. Note: `b1_free_roam_2026-08-02_emlo_vocab_close.md`.

### England densify neg audit (2026-08-02)

- Soft-neg on Wood/Lynnet densify (18 peers): **Locke demoted** (EE ~1701 green spectacles receipt); other 17 clear in this audit.
- Wood Δ **−6→−5** (n_ctrl 12→11); primary n/median/CI unchanged (39; −2.97; [−4, 2]). Note: `b1_free_roam_2026-08-02_england_densify_neg.md`.

### Dutch mine open — Huygens soft (2026-08-02)

- Non-EMLO roam: Italian local OCR / Gallica dry for new living onset; LetterSampo still closed.
- **Constantijn Huygens** (*Mijn jeugd* «De bril, 1612»): began concave youth spectacles at 16; continuous use. Soft-hold — **myopia/distance**, not B1 near-work class; not promoted. Note: `b1_free_roam_2026-08-02_dutch_huygens.md`.

### Dutch midlife *bril* dig → practical close (2026-08-02)

- Targeted near-work hunt: EMLO `bril*` dry/false-friend; IA diary search 0; DBNL search **403**; no new named midlife reading-wearer.
- Dutch near-work letter/diary onset lane **practically closed** pending better DBNL access. Note: `b1_free_roam_2026-08-02_dutch_bril_dig.md`.

### German *Brille* mine → practical close (2026-08-02)

- EMLO German spectacle vocab dry/false-friend; IA early-modern German personal-wear phrases **0**; DDB API unauthorized.
- Lichtenberg 1776 Ramsden lorgnette letter verified OA — owns one for **looking at girls**, plus proxy order for a student lord → **wrong B1 class** (not near-work).
- German letter/diary near-work onset lane **practically closed**. Note: `b1_free_roam_2026-08-02_german_brille.md`.

### Spanish *anteojos* free roam (2026-08-02)

- EMLO Spanish spectacle terms **0** / false-friend; IA early Spanish **0**.
- PARES 1710 Gandía letters: *anteojos para la vista del tío Coloma* — third-party vision order; wearer identity still thin (no CSV ingest).
- Note: `b1_free_roam_2026-08-02_spanish_anteojos.md`.

### Wolsey + Ardingelli densify (2026-08-02)

- Letter mines dry → deep densify thin/extreme cells.
- Wolsey: +Blythe / Stokesley / Bainbridge / Lee → n_ctrl **7**, Δ **−5**.
- Ardingelli: +Piero de' Medici (short ya45=8) → n_ctrl **4**, Δ **−4.5**.
- Primary median still **−2.97** [−4.0, 2.0]; merchant median **−3.74**. Note: `b1_free_roam_2026-08-02_wolsey_ardingelli_densify.md`.

### Coloma soft-hold + Baye densify (2026-08-02)

- PARES OSUNA CT.235 D.154–175: *anteojos para la vista del tío Coloma* (1710) — no images; wearer identity not letter-pinned → **no ingest**.
- Baye: Premierfait → clerk + Gontier Col (birth est. 1355) → n_ctrl **5**, Δ **−17→−10**. Note: `b1_free_roam_2026-08-02_coloma_baye.md`.

### EMLO leftovers free roam — Richardson / Rawlins soft (2026-08-02)

- Spectacles dump otherwise exhausted (promotes/closes already logged).
- **Richardson jr** (1708–1781): 1774 self-commission for **magnifying** spectacles; post-wear chrono thin → soft-hold medium, not promoted.
- **Rawlins** (1689–1752): 1748 third-party “take to spectacles”; ~+4y ceiling → soft-hold low.
- Note: `b1_free_roam_2026-08-02_richardson_rawlins.md`.

### Richardson jr promote (2026-08-02)

- Deep-dig unlocked Bartlet collecting trail **1774-02 → 1777-05** (coins/books/medals) after magnifying-spectacle onset.
- **PROMOTED:** ya=**3.3**; T=**24.3**; n_ctrl=**8**; Δ=**+8.3**; primary **n=39→40**; median Δ **−2.97→−1.49**; CI still **[−4.0, 2.0]**; SESOI FAIL.
- Note: `b1_free_roam_2026-08-02_richardson_promote.md`.
