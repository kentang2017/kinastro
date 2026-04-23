# 薩珊傳統占星星盤整合指南
# Sassanian Traditional Star Chart Integration Guide

## 檔案結構

```
astro/sassanian/
├── __init__.py                          # 模組入口
├── sassanian_chart_renderer.py          # 星盤渲染器（方形/橫幅格式）
├── sassanian_astronomy.py               # 薩珊天文計算（Ayanamsa、恆星位置）
├── sassanian_symbols.py                 # 薩珊符號系統（Pahlavi 文字、圖案）
└── data/
    ├── royal_stars.json                 # 四顆皇家恆星資料
    └── pahlavi_names.json               # Pahlavi 行星/星座名稱
```

## app.py 修改

### 1. 在 `_SYSTEM_CATEGORIES` 中添加薩珊星盤 tab

位置：約第 881 行

```python
("cat_middle_east", ["tab_sassanian_chart", "tab_persian", "tab_arabic", "tab_yemeni"]),
```

### 2. 在 `_SYSTEM_LABELS` 中添加標籤

位置：約第 925 行後

```python
"tab_sassanian_chart": t("sassanian_tab_name"),
```

### 3. 在 `_SYSTEM_HINTS` 中添加提示

位置：約第 967 行後

```python
"tab_sassanian_chart": t("sassanian_tab_help"),
```

### 4. 添加薩珊星盤的 elif 處理邏輯

位置：在所有 `elif _selected_system == "tab_...":` 之後，約第 2170 行後

```python
elif _selected_system == "tab_sassanian_chart":
    # ── 薩珊傳統占星星盤 ──────────────────────────────────────
    st.header(t("sassanian_chart_title"))
    st.info(t("sassanian_chart_disclaimer"), icon="🏛️")

    # 選項設定
    col1, col2, col3 = st.columns(3)
    with col1:
        show_pahlavi = st.checkbox(t("sassanian_show_pahlavi"), value=True)
    with col2:
        show_royal_stars = st.checkbox(t("sassanian_show_royal_stars"), value=True)
    with col3:
        show_firdar = st.checkbox(t("sassanian_show_firdar"), value=True)

    with st.spinner(t("spinner_sassanian")):
        chart_data = {
            "year": birth_year,
            "month": birth_month,
            "day": birth_day,
            "hour": birth_hour,
            "minute": birth_minute,
            "longitude": longitude,
            "latitude": latitude,
            "timezone": timezone,
        }

        from astro.sassanian.sassanian_chart_renderer import generate_sassanian_chart

        sassanian_fig = generate_sassanian_chart(
            chart_data=chart_data,
            width=1200,
            height=900,
            show_pahlavi=show_pahlavi,
            show_royal_stars=show_royal_stars,
            show_firdar=show_firdar,
        )

        st.plotly_chart(sassanian_fig, use_container_width=True)

        # 可選：添加 AI 分析按鈕
        _render_ai_button("tab_sassanian_chart", sassanian_fig, btn_key="sassanian")
```

## chart_renderer_v2.py 修改（可選）

如果需要將薩珊星盤作為現有星盤的選項，可以在 `chart_renderer_v2.py` 中添加：

```python
def render_chart_with_sassanian_option(..., sassanian_mode: bool = False):
    if sassanian_mode:
        from astro.sassanian.sassanian_chart_renderer import generate_sassanian_chart
        return generate_sassanian_chart(chart_data)
    # ... 現有邏輯
```

## ai_analysis.py 修改

添加薩珊術語提示：

```python
elif system == "tab_sassanian_chart":
    prompt = f"""
    請使用波斯薩珊王朝占星術語（基於 Bundahishn 和 Dorotheus Pahlavi 譯本）分析此星盤：
    
    - 使用 Pahlavi 行星名稱（Khwarshid, Mah, Tir, Anahid, Warhran, Ohrmazd, Keyvan）
    - 強調整宮制和薩珊 Ayanamsa 的特點
    - 分析四顆皇家恆星（Tascheter, Vanand, Satevis, Hastorang）的影響
    - 提及 Firdar 生命週期的可能性
    
    {chart_context}
    """
```

## 測試

運行測試套件：

```bash
cd /mnt/c/Users/hooki/OneDrive/pastword/文件/Github/kinastro
PYTHONPATH=. python3 -m pytest tests/test_sassanian_chart.py -v
```

或測試單個模組：

```bash
PYTHONPATH=. python3 astro/sassanian/sassanian_astronomy.py
PYTHONPATH=. python3 astro/sassanian/sassanian_chart_renderer.py
```

## 歷史星盤測試資料

測試用歷史星盤（已在 `sassanian_astronomy.py` 中定義）：

- **281 CE**: 薩珊示例星盤（Dorotheus Pahlavi 譯本）
  - 日期：281 年 3 月 15 日 12:00
  - 地點：泰西封 Ctesiphon (44.5°E, 33.3°N)

- **381 CE**: 薩珊示例星盤
  - 日期：381 年 7 月 22 日 6:00
  - 地點：泰西封 Ctesiphon (44.5°E, 33.3°N)

## 視覺風格規範

### 色彩調色盤
- 深紅 (Crimson): `#8B1538`
- 金箔 (Gold Leaf): `#D4AF37`
- 綠松石 (Turquoise): `#40E0D0`
- 深靛藍 (Dark Indigo): `#1A237E`
- 白色 (White): `#F5F5F5`
- 羊皮紙 (Parchment): `#F5E6D3`

### 圖案元素
- Faravahar 翅膀元素（角落裝飾）
- 八瓣玫瑰星（恆星標記）
- 火壇符號（上升點標記）
- 石榴/葡萄藤邊框

### 星盤格式
- 方形（3x4 網格）或橫幅格式
- 整宮制（Whole Sign Houses）
- 薩珊 Ayanamsa（約 22°）
- Pahlavi 文字標籤（可選）

## 參考文獻

- Greater Bundahishn (Iranian Bundahishn, tr. Anklesaria, 1956)
- Dorotheus of Sidon, Pahlavi translation (Pingree, 1976)
- Al-Biruni, "The Chronology of Ancient Nations" (tr. Sachau, 1879)
- Pingree, D. (1963). "Classical and Byzantine Astrology in Sassanian Persia"
- Sassanian silver plates (Metropolitan Museum, Louvre)
- Taq-e Bostan rock reliefs (6th-7th century CE)
