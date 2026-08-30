# Strict_overlap 扩矿（2026-08-02）

**不做水货针**；挖的是「已有成果年、缺文本著作对照」的近失格。

## 做法

1. 对照升级：René of Anjou、Joan of Valois → `output_eligible` 文本著作型  
2. 新设法文文学对照：Chartier、Chastellain、La Sale、Jouffroy、Fillastre（手针+eligibility）  
3. 意/英文本同行 overlay（同区、出生±22）：Landino、Alberti、Colet 等  
4. 表：`data/curated/b1_output_strict_control_overlays.csv`（+36 links）  
5. script 27 读取 overlay 并入匹配列表  

**未**把 artisan/painter、confidence=low 单针订单灌进 strict。

## 结果

| | 扩前 | 扩后 |
|--|------|------|
| **strict n** | 24 | **32** |
| 中位 Δ | ~−4 | **−2.5** |
| CI | | **[−5, 3]** |
| SESOI +5/+15 | FAIL | **仍 FAIL** |

### 新进 strict（8 人）

| person_id | Δ | n_ctrl |
|-----------|---|--------|
| hesselin_denis | +11.0 | 3 |
| gonzaga_ludovico | +1.5 | 6 |
| wyatt_henry | 0.0 | 3 |
| sforza_francesco | −0.5 | 6 |
| barbara_brandenburg | −2.0 | 5 |
| charles_orleans | −4.0 | 5 |
| philippe_le_hardi | −4.0 | 5 |
| bianca_maria | −28.0 | 5 |

Bianca 书信针仍薄、对照人文强 → 大负 Δ，属测量不对称，不是灌水。

## 仍进不了 strict（诚实留下）

Lotto（画家）、Arduino 等 artisan、低置信单针修士/Neri、Moser 制镜匠、Paele 软证据。
