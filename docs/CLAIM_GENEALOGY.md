# 主张谱系（Claim Genealogy）v4

本文件区分主张层级，并落实反模糊原则：**不足则猎证**，不用悬空措辞收工。

## 1. 原书较宽论证（Macfarlane & Martin）

| 项 | 内容 |
|----|------|
| 英/美书名 | *The Glass Bathyscaphe*（Profile, 2002）/ *Glass: A World History*（Chicago, 2002） |
| ISBN（美） | 9780226500287 |
| 中文译本 | 商务印书馆，北京，2003（ISBN 7-100-03918-5） |
| 作者页 | https://www.alanmacfarlane.com/glass/book.html |

**本项目态度：** 原书是「玻璃技术组合」叙事，不是「仅有眼镜 → 现代文明」单因论。宽链未系统检验。

## 2. 「+15 年」状态机（已核 Chicago 正文）

机器可读表：[`data/curated/claim_fifteen_years_sources.csv`](../data/curated/claim_fifteen_years_sources.csv)

| 状态 | 含义 |
|------|------|
| `confirmed_in_book` | 已核对纸页/扫描页出现逐字句 |
| `attributed_secondary` | 书评/摘录站归因作者 |
| `pending_reverification` | 版本分页待核 |
| `debunk_as_causal_slogan` | 口号式文明起点，可 debunk |

**当前（2026-07-23）：** Chicago 扫描本 **印刷页 p.145**（Ch.8 *Spectacles and Predicaments*）原文：

> The invention of spectacles increased the intellectual life of professional workers by fifteen years or more.

同页并述 Petrarch、工匠 active life almost doubled、与印刷互促。本地核验见 `data/raw/macfarlane_glass/README.md` 与 `ocr_hi/hi-079.txt`。

**因此：** 先前「正文无 fifteen years、只来自 Miller」**撤回**。Miller / Delanceyplace 是转述，不是源头。  
**仍待核：** Profile 英版页码、商印中译对应页。  
**C 档仍可 debunk：** 「文明唯一起点」类单因口号（书中亦是玻璃组合叙事，不是「只有眼镜」）。

**另：** p.190 一带「延长工作生涯」的定性句与 **p.145 的 +15 年量化句**不是同一句；窗玻璃 “lengthened the working day” 又是另一条。

## 3. 窄命题与 B1–B4

见 [`CLAIM_MAP.md`](CLAIM_MAP.md)。本项目可立即裁决的是 A1/A2 方向、B2/B4 宏观未获支持、C 文明单一起点 debunk；**B1（佩戴者是否多干几年）是猎证主线，不作「已拒绝」。**

## 4. 二手文明口号

> 「不是蒸汽机，而是眼镜」「现代文明的起点就是眼镜」

**裁决：debunk（因果过度压缩）。** 与「+15 年是否在原书」分开处理。

## 5. 人工核对记录（Chicago 电子本，保留为部分证据）

**书目：** *Glass: A World History*（Chicago, 2002）Scribd 电子版通读 p.1–203 + 附录/索引。  
**清单：** `outputs/tables/claim_genealogy_checklist.csv`

| 核对项 | 状态 |
|--------|------|
| p.145 +15 years 原文 | ✅ confirmed | Ch.8; local Chicago scan 2026-07-23 |
| p.190 定性延长工作生涯 | ✅ 另句 | 勿与 p.145 混淆 |
| 正文 `fifteen years` 逐字 | ✅ | **p.145**（先前「未检出」撤回） |
| 文明唯一起点 | ✅ 否 | 嵌于玻璃组合宽叙事 |
| 「不是蒸汽机而是眼镜」口号 | ❌ 未检出 | 正文口号式原句未见 |

### 待办

- [x] Chicago：+15 页码（p.145）
- [ ] Profile / 商印页码对照
- [ ] 更新 checklist CSV 与 PREPRINT C 档措辞（本轮已同步 md）
