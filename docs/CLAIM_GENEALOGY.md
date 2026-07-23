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

## 2. 「+15 年」状态机（不得写「只来自 Miller」）

机器可读表：[`data/curated/claim_fifteen_years_sources.csv`](../data/curated/claim_fifteen_years_sources.csv)

| 状态 | 含义 |
|------|------|
| `confirmed_in_book` | 三版之一已核对纸页/扫描页出现逐字或明确等价句 |
| `attributed_secondary` | 书评/摘录站归因作者，页码未核 |
| `pending_reverification` | 先前单次电子通读未检出；分页/版本差异下需重核 |
| `debunk_as_causal_slogan` | 口号式文明起点，可 debunk |

**当前（2026-07-23）：** 多条二手/摘录将「15 年或更多」归于作者（Miller、Delanceyplace、T&C 书评概括、豆瓣中译摘录）。Chicago 电子本一次通读未检出 `fifteen years`，**不足以**定论「确定不是原书」。  
**开放猎证：** Profile 英版、Chicago 纸本全页、商印中译 Ch.8–9 页码照片。

**可安全引用的已核定性句（Chicago e-text）：** p.190 *spectacles lengthened the working life of individuals*。

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
| p.190 定性延长工作生涯 | ✅ |
| 正文 `fifteen years` 逐字 | ⚠ 该电子本未检出；**非**终局；见来源表 |
| 文明唯一起点 | ✅ 否（玻璃组合叙事） |
| 「不是蒸汽机而是眼镜」口号 | ❌ 未检出 |

### 待办（硬）

- [ ] Profile / Chicago 纸本 / 商印：+15 页码三版猎证
- [ ] 核验后更新 `claim_fifteen_years_sources.csv` 的 `verification_status`
