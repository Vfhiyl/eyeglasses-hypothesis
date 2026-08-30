# B1-Output hand-pin densify（2026-08-02）

接 purify：给高频文本著作对照补**多针出版/书信年**，并跑关键敏感性。

## 做了什么

1. 重写 `data/curated/b1_control_output_years_curated.csv`（30 人多针；其余合格者仍用 first;last 端点）  
   - 含 Marsuppini、Manetti、Nogarola、Dati、Vernia、Dei、Panormita、Barbaro、Boyle、Dryden、Tillotson、Ray、Gerson、Christine…  
2. script 27：对照年 = P50∪P800∪手针；出生死亡可从 eligibility/手针补。  
3. 敏感性表刷新：`b1_output_estimand_sensitivity.csv`

## 主结果

| 模式 | n | 中位 Δ | CI | +5 |
|------|---|--------|-----|-----|
| primary（手针后） | 21 | **+3.0** | [−12, 8] | FAIL |
| drop Lotto | 20 | **−0.5** | [−12, 8] | FAIL |
| nctrl≥3 | 17 | +6.0 | [−10, 10] | FAIL（lo&lt;0） |
| drop Lotto + nctrl≥3 | 16 | +4.5 | [−10, 10] | FAIL |
| drop 薄商人针 | 17 | +7.0 | [−5, 10] | FAIL（lo&lt;0） |

相对 purify（中位 +1.5）：手针后中位升到 **+3**，仍远低于 +15；**没有任何敏感性通过 sesoi5（需 lo≥0）**。  
Lotto 格 `med_c=0` 仍是异常正 Δ；去掉后中位回到约 0。

## 读法

在「文本著作型对照 + 手针」下，成果跨度优势**不稳定且达不到 SESOI +5 的置信要求**；Macfarlane 量级 +15 仍无支持。  
13/21 对已用到至少一手针对照；继续刷 WD 收益低。

## 下一步（若续）

- 修 Lotto 格对照（画家→文本对照或剔除出主 SESOI）  
- 或冻 B1-Output 主结论，转书目库级对照（EDIT16 / ISTC 作者年）——更大工程
