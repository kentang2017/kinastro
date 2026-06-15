# 太陽回歸流年多體系時間軸 | Solar Return Annual Multi-System Timeline

## 概述 | Overview

KinAstro 獨家功能：以**太陽回歸（Solar Return）精確天文時刻**作為每年度的起點，同步起算大六壬祿命、紫微、八字、七政四餘與西洋 SR 盤，形成中西合參的年度預測時間軸。

*KinAstro's signature feature: use the exact astronomical Solar Return moment as each year's starting point to cast Da Liu Ren destiny charts, Ziwei, Bazi, Qizheng, and Western SR — a cross-cultural annual forecast timeline.*

---

## 核心方法 | Core Method

### 太陽回歸瞬間
- 使用 Newton-Raphson 迭代求太陽回到本命黃經的精確 Julian Day
- 回歸地預設為**出生地**（可擴展為現居地）

### 中式起盤時刻
- 將 SR 瞬間換算為回歸地**當地民用時間**
- 以此時刻起大六壬四課三傳（非農曆正月初一或固定立春）

### 本命與流年錨點
| 項目 | 規則 |
|------|------|
| 本命地支 `benming_zhi` | 生年地支（固定） |
| 流年太歲 `liunian_zhi` | SR 公曆年歲君（立春為界） |
| 虛歲 | `SR年 - 生年 + 1` |

---

## 各體系應用 | Per-System Application

### 大六壬祿命（核心）
- SR 當地時刻起課 → `LunMingAnalyzer` 論命
- 規則引擎評分：三傳、用神、格局、太歲、十二宮

### 紫微斗數
- **流年宮**：太歲地支臨宮
- **小限宮**：陽男陰女順行、陰男陽女逆行，命宮起虛歲
- **流年四化**：依流年天干飛化

### 子平八字
- 本命不變，`reference_date = SR 當地日期` 取大運流年

### 七政四餘
- 本命盤 + `compute_dasha(current_year=SR年)`
- SR 時刻流時盤與本命守照共振（`evaluate_qizheng_resonance`）

### 西洋太陽回歸
- 輔助對照：ASC、太陽月亮落宮、角宮行星、本命相位

---

## API 與程式入口 | API & Code Entry

```python
from astro import compute_solar_return_flowyear_timeline
from astro.models import BirthData

timeline = compute_solar_return_flowyear_timeline(birth, 2024, 2028)
```

```
POST /api/v1/annual/solar-return-timeline
```

---

## 參考 | References

1. **太陽回歸** — Western predictive astrology, solar return charts
2. **《六壬論命秘要》** — 大六壬祿命理法
3. **紫微斗數全書** — 流年、小限、四化
4. **果老星宗** — 七政四餘年限大運