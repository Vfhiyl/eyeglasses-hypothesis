# 数据字典与样本筛选

## 时期约定

| 字段 | 含义 |
|------|------|
| `period_start` / `century` | `year // 100 * 100`，半开世纪：`1400` = 1400–1499 |
| `post_1300` | `century >= 1300` |
| 局部窗口（Studium 主分析） | 活动锚点 1200–1285 vs 1300–1385 |

## 核心表

### `studium_paris_scholars.csv`

| 字段 | 说明 |
|------|------|
| `life_date_quality` | `interval_meta` / `text_range` / `multi_year_uncertain` / `single_year_not_birth` / … |
| `birth_year` | 仅在可信 life 解析下填写；单一年份**不**作出生年 |
| `observed_activity_span_years` | 最早–最晚活动年差；**不是**职业持续时间 |
| `age_at_activity_end` | `activity_end - birth_year`（需可信出生年） |
| `is_master` / `is_student` | 来自 status 文本启发式 |

**筛选：** 主年龄分析要求 `life_date_quality ∈ {interval_meta, text_range}`。

### `panel_city_century.csv`

| 字段 | 说明 |
|------|------|
| `hc_observed` / `books_observed` / `pop_observed` | 覆盖标识 |
| `*_fill0` | 敏感性用显式填零；主回归应过滤 `*_observed==1` |
| `glass_center` | 来自 `config/cities.yaml` |

### 其他常用输出

- `breakpoint_tests.csv`：趋势 Chow，`window_half=80`
- `evidence_by_claim.csv`：子命题汇总
- `studium_sample_audit.csv`：随机核验样本

## 许可证与来源（摘要）

详见 `outputs/tables/data_provenance.csv`（由 `scripts/12_data_provenance.py` 生成）。使用前请遵守各数据集原许可证；本仓库脚本为研究审计用途。
