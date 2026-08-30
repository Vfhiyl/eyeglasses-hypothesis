# B1-Output purify pass（2026-08-02）

沿出成果线深挖：不是再扩佩戴者，而是**净化对照**，减少「公爵行政档 = 知识成果」的偷换。

## 做了什么

1. **对照资格表** `data/curated/b1_control_output_eligibility.csv`  
   - 仅 `textual_authorship_proxy`（书信/著作/教学出版等）可作 curated 后备  
   - 行政公爵、画家湿壁画等 → `output_eligible=False`（117 合格 / 50+ 剔除）
2. **script 27** 后备只读合格对照；劳动年 curated 不再原样泄漏。
3. **SPARQL** 对 62 个合格且缺 WD 的匹配对照 densify → 仅 **6** 人新有日期（WD 仍极稀）；另手补 Dryden P50（含 1700）。
4. **Pirckheimer** 补 Allen+BD2 的 FROM-him 书信 → 成果跨度 0→**13**；Δ −18→**−5**。
5. 端点表：`data/curated/b1_control_output_years_curated.csv`（合格者 first;last，备查）。

## 主结果（净化后）

| | 净化前 v0 | 净化后 |
|--|-----------|--------|
| n_pairs | 26 | **21** |
| 中位 Δ span | −0.75 | **+1.5** |
| CI | [−10.5, 6.25] | **[−10, 9]** |
| SESOI +5/+15 | FAIL | **仍 FAIL** |
| 任一对含 curated 对照 | 25/26 | **18/21** |
| 全 WD 对照 | ~0–3 | **3** |

读法：去掉行政对照后中位略升到 +1.5，但 **达不到 +5（且 lo≪0）**；+15 仍远。结论对「Macfarlane 量级成果延长」依旧不支持。

## 仍存偏误

- 18/21 对仍依赖 curated 著作端点（非逐书 P50）。  
- Lotto 格 `med_c=0`（画家对照无 45+ 著作年）会抬高正 Δ——附录，不主导中位。  
- WD 对 15c 人文对照几乎补不动 → 下一刀应是**书目/书信对照 chrono**，不是再刷 SPARQL。

## 下一步（若续）

1. 给高频合格对照（Marsuppini、Manetti、Nogarola、Boyle…）手编 3–5 个有出处出版年。  
2. 敏感性：drop Lotto / drop nctrl&lt;3。  
3. 劳动年路径保持冻结。
