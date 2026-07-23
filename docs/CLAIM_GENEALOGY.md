# 主张谱系（Claim Genealogy）

本文件区分三类主张，避免用本项目的窄检验裁决整本 *Glass* 书。

## 1. 原书较宽论证（Macfarlane & Martin）

| 项 | 内容 |
|----|------|
| 英/美书名 | *The Glass Bathyscaphe*（Profile, 2002）/ *Glass: A World History*（Chicago, 2002） |
| ISBN（美） | 9780226500287 |
| 中文译本 | 商务印书馆，北京，2003（ISBN 7-100-03918-5）；繁体 Cite 台湾 2006 |
| 作者页自述 | https://www.alanmacfarlane.com/glass/book.html |

**出版社/书评层常见表述（非本项目统计对象）：**

- 玻璃在视觉、光学、实验器皿、窗、镜、显微镜/望远镜中的综合作用，为欧洲科学与文明分流提供条件。
- 亚马逊书评引述（**非原书正文逐字句**）：*“The invention of spectacles [in the 13th century] increased the intellectual life of professional workers by fifteen years or more”*（John J. Miller；详见 §5 人工核对：原书最接近 **p.190** 定性表述）。

**本项目态度：** 原书是「玻璃技术组合」叙事，不是「仅有眼镜 → 现代文明」的单因论。本仓库**未系统检验**器皿玻璃、窗玻璃、望远镜等链条。

## 2. 窄化可检验命题（本项目审计对象）

1. 老花眼镜是否系统性延长读写密集型学者的可观察职业生涯（尤其 45+）；
2. 玻璃/眼镜制造中心城市是否获得稳定的知识产出优势；
3. 宏观知识序列在约 1290 的结构变化是否强于印刷术时点（约 1450）。

## 3. 二手传播版强断言（高度夸张）

常见短视频/自媒体压缩句式示例（措辞随平台变化）：

> 「不是蒸汽机，而是眼镜」「现代文明的起点就是眼镜」「学者寿命延长二十年所以科学革命」

| 检查项 | 状态 |
|--------|------|
| 「不是蒸汽机，而是眼镜」是否为原书原句 | **未在公开出版社简介与作者页中找到原句**；更像二手口号 |
| 「学者寿命/智力生涯 +15 年」 | 出现在 **John J. Miller 亚马逊书评**转述中；**人工通读正文 p.1–203 + 附录 p.204–213 未检出逐字原句**。*Sources for Quoted Passages*（p.218–219）Ch.8 仅列 Bird、Rasmussen、Browning、Trevor-Roper 等，**无此句之出处**。最接近原文：**p.190** *spectacles lengthened the working life of individuals*；**p.201** *glasses in old age*；Ch.8 presbyopia/传播。定稿：**书评量化句 ≠ 原书可引用页码** |
| 裁决 | 对**二手强断言**：可判定为高度夸张。对**原书宽论证**：本项目未检验，不作判决。 |

## 4. 三档裁决（定稿，v3.1）

与 [`VERDICT_zh.md`](VERDICT_zh.md) 一致；避免用「既不能证实也不能证伪」作读者终点。

| 档位 | 命题 | 裁决 |
|------|------|------|
| **A · 弱机制** | presbyopia 矫正降低读写边际成本 | **成立（合理）** |
| **B · 强窄命题** | 宏观 45+ 延长、玻璃中心 HC 优势、1290 断点 > 1450 | **不成立（现有证据下应拒绝）** |
| **C · 二手强断言** | 「现代文明起点就是眼镜」「+15 年智力生涯」 | **夸张 / debunk** |
| **原书宽论证** | 「玻璃是欧洲科学/分流的重要条件之一」 | **本项目未系统检验**；B/C 的拒绝**不能**证伪整本书 |

## 5. 人工核对记录（定稿，2026-07-22）

**书目：** Macfarlane & Martin, *Glass: A World History*（Chicago, 2002）  
**来源：** Scribd 电子版；通读正文 p.1–203、附录 p.204–213、*Further Reading* / *Sources for Quoted Passages* p.214–219、索引 p.235–255。  
**机器可读清单：** `outputs/tables/claim_genealogy_checklist.csv`

全书**无脚注**（p.214）；直接引文出处见 p.218–219；完整书目见 Bibliography。

### 5.1 核对项与页码

| 核对项 | 状态 | 原书位置与备注 |
|--------|------|----------------|
| 眼镜发明与意大利传播 | ✅ 部分 | **p.144–145**（Ch.8 章首）：北意传播、印刷革命语境；**p.184–185**：13 世纪西欧镜片/眼镜。**~1280** 在作者公开讲座稿（chinaglass.pdf）出现，正文未 isolate 于单页 |
| 「+15 年 / professional workers / intellectual life」 | ❌ 无逐字原句 | **正文 p.1–203、附录、索引均无** `fifteen years` 条目；*Sources* Ch.8（p.219）无此句出处。**最接近：p.190** *spectacles lengthened the working life of individuals*（定性）；**p.201** *glasses in old age* 与 thinking machines 并列 |
| 眼镜是否为文明唯一起点 | ✅ 否 | 嵌于**玻璃组合**宽叙事：镜/窗/器皿/透镜/显微镜等（Ch.4 **p.60–61**；Ch.9 **p.180–203**；Appendix 2 二十实验 16/20 需玻璃） |
| 「不是蒸汽机而是眼镜」 | ❌ 未检出 | 正文、附录、索引均无；Steam engine 见 **p.192**（与 glass 对比，非口号式原句） |
| presbyopia vs myopia 机制 | ✅ | **p.148–151**（Ch.8）；索引 **presbyopia** → 144, 149–151, 181；**myopia** → 149–173 |
| 中文译本对应 | ⏸ 未做 | 商务印书馆 2003（ISBN 7-100-03918-5）待对照 p.190 / Ch.8 译法 |

### 5.2 主张谱系三层（人工核对后）

| 层级 | 代表表述 | 原书依据 | 本项目用法 |
|------|----------|----------|------------|
| **原书宽论证** | 玻璃（含眼镜）改变视觉与实验条件，促成西方知识革命 | p.60–61, 144–174, 184–203, p.190 | 未系统检验；窄结果不能证伪 |
| **原书定性（眼镜）** | 眼镜延长个人可工作年限；老花 vs 近视分流东西方 | **p.190**, p.201, Ch.8 | 机制叙述；非可回归微观数据 |
| **二手/书评量化** | 「professional workers … fifteen years or more」 | **仅 Miller 亚马逊书评**；非正文引文 | 标为**高度夸张/压缩**；禁止当已核页码引用 |

### 5.3 索引抽查（p.235–255）

与眼镜相关的索引簇（便于他人复核，**非**「+15 年」检索）：

- **spectacles：** 1, 3, 13–16, 38, 61, 79, 82, 97, 104, 106, 112, 118, 122, 130, 142, **144–152**, 171, 181, 184, **190**
- **presbyopia (long-sightedness)：** 144, 149–151, 181
- **myopia：** 149–173（含 education, close work, nutrition, personality）
- **Italy: spectacles invented：** 144–145
- **无索引项：** `fifteen years`, `professional workers`, `intellectual life`, `working life`

### 5.4 可安全引用的原书原文（英文）

1. **p.190**（Ch.9）：*spectacles (glasses) lengthened the working life of individuals*
2. **p.201**（Ch.9）：*glasses in old age*（与 prisms, telescopes, microscopes 等并列）
3. **p.61**（Ch.4）：*spectacles in older age*（与 mirrors, window frames 并列，改变看世界的方式）
4. **p.151** 附近（Ch.8）：presbyopia 约 **age forty**；凸透镜供老花，凹透镜更晚且更难

### 5.5 待办（可选）

- [ ] 中文译本段落对照（p.190 / Ch.8）
- [ ] 若学术写作需引「+15 年」，改用：**Miller 书评转述** + 脚注指向 **p.190 定性句**，并说明原书无该量化原句

核对清单维护：`outputs/tables/claim_genealogy_checklist.csv`（与上表同步）。
