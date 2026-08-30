# B1-Output Lotto / visual fix（2026-08-02）

## 诊断

Lotto（画家，artisan）Δ=+27 来自对照 P800 多在 **45 岁前** → `output_span_after_45=0`，中位对照跨度被压成 0。  
这些对照在 `b1_control_output_eligibility.csv` 中本为 `output_eligible=False`，却因薄 P800 年漏进测量。

## 规则（写入 script 27）

1. **对照：** `output_eligible=False`（行政/绘画等）一律不进 B1-Output，即使有 P800。  
2. **处理组主 SESOI：** `occupation_bucket=artisan` 或 class 含 painter/sculptor/fresco → **附录**，不进 `in_primary_delta`。

## 结果

| | 手针后（含 Lotto） | 本 fix |
|--|-------------------|--------|
| primary n | 21 | **19** |
| 中位 Δ | +3.0 | **−4.0** |
| CI | [−12, 8] | **[−12, 8]** |
| SESOI +5/+15 | FAIL | **FAIL** |

Lotto 现无合格文本著作对照 → 无 Δ（非「排除但仍带 +27」）。  
主结论更干净：**文本脑力劳动成果跨度相对对照略负/近零，不支持 +5/+15。**

## 仍薄的格

商人薄针（Datini/Ardingelli/Strozzi/Cederni）大负 Δ 仍拉低中位；属成果代理稀疏，不是眼镜负效应的硬证。
