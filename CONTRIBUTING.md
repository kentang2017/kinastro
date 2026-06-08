# Contributing to 堅占星 Kin Astro

感謝你對 Kin Astro 的興趣！以下是參與開發的指南。

## 開發環境

```bash
# 安裝依賴
pip install -r requirements.txt
pip install pytest

# 運行 Streamlit 前端
streamlit run app.py

# 運行 FastAPI 後端
uvicorn api_server:app --reload

# 運行測試
python -m pytest tests/ -q
```

## 專案結構

```
kinastro/
├── app.py                  # Streamlit 主應用 (UI 層)
├── api_server.py           # FastAPI 後端 (計算 API)
├── astro/
│   ├── calculator.py       # 核心天文計算 (pyswisseph)
│   ├── chart_renderer.py   # 中國七政四餘盤面渲染
│   ├── chart_theme.py      # 統一主題色、CSS、SVG 樣式
│   ├── export.py           # 匯出功能 (TXT/CSV/PDF/PNG/分享連結)
│   ├── i18n.py             # 中英雙語翻譯字典
│   ├── interpretations.py  # 文字解讀 (流年/合盤/大限)
│   ├── natal_summary.py    # 命盤摘要生成
│   ├── constants.py        # 七政四餘常量定義
│   ├── western.py          # 西洋占星
│   ├── indian.py           # 印度占星 (Vedic/Jyotish)
│   ├── thai.py             # 泰國占星
│   ├── ...                 # 其他占星體系
│   ├── classic/            # 古典文獻 (百論等)
│   ├── reference/          # 參考資料 (markdown)
│   └── data/               # JSON 資料檔 (恆星、Picatrix 等)
├── tests/
│   ├── test_calculator.py
│   ├── test_advanced_features.py
│   └── test_new_astrology.py
└── requirements.txt
```

## 如何新增一個新的占星體系

以下是新增占星體系的完整步驟模板，以「XX 占星」為例：

### 步驟 1：建立計算模組

在 `astro/` 目錄下新建 `xx_astro.py`：

```python
"""
astro/xx_astro.py — XX 占星計算模組
"""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class XXPlanet:
    """單顆星曜的資料結構"""
    name: str
    name_cn: str
    longitude: float
    sign: str = ""
    sign_degree: float = 0.0
    retrograde: bool = False


@dataclass
class XXChart:
    """完整排盤結果"""
    year: int
    month: int
    day: int
    hour: int
    minute: int
    timezone: float
    latitude: float
    longitude: float
    location_name: str
    julian_day: float = 0.0
    planets: List[XXPlanet] = field(default_factory=list)
    # ... 體系特有欄位


def compute_xx_chart(
    year: int, month: int, day: int,
    hour: int, minute: int,
    timezone: float, latitude: float, longitude: float,
    location_name: str = "",
) -> XXChart:
    """核心計算函式 — 必須是純計算，不可依賴 Streamlit。"""
    import swisseph as swe

    # 1. 計算 Julian Day
    ut_hour = hour + minute / 60.0 - timezone
    jd = swe.julday(year, month, day, ut_hour)

    # 2. 計算星曜位置
    planets = []
    # ... 你的計算邏輯

    return XXChart(
        year=year, month=month, day=day,
        hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name,
        julian_day=jd,
        planets=planets,
    )


def render_xx_chart(chart: XXChart):
    """Streamlit 渲染函式 — 僅在此處 import streamlit。"""
    import streamlit as st

    st.subheader(f"XX 占星 — {chart.location_name}")
    # ... 你的 UI 渲染邏輯
    if chart.planets:
        st.dataframe(
            [{"Name": p.name, "Sign": p.sign, "Degree": f"{p.sign_degree:.2f}°"}
             for p in chart.planets],
            width="stretch",
        )
```

### 步驟 2：加入 i18n 翻譯

在 `astro/i18n.py` 的 `TRANSLATIONS` 字典中加入：

```python
# Tab 標題
"tab_xx": {"zh": "XX占星", "en": "XX Astrology"},
# 描述文字（未排盤時顯示）
"desc_xx": {
    "zh": "**XX占星**\n\n此體系的簡介...",
    "en": "**XX Astrology**\n\nBrief introduction...",
},
# Loading spinner
"spinner_xx": {"zh": "計算 XX 占星中...", "en": "Computing XX chart…"},
```

### 步驟 3：在 app.py 中加入 Tab

```python
# 1. 頂部加入 import
from astro.xx_astro import compute_xx_chart, render_xx_chart

# 2. 在 st.tabs() 列表中加入新 tab
tab_..., tab_xx = st.tabs([..., t("tab_xx")])

# 3. 加入 tab 內容
with tab_xx:
    if _is_calculated:
        try:
            _p = st.session_state["_calc_params"]
            with st.spinner(t("spinner_xx")):
                xx_chart = compute_xx_chart(**_p)
            render_xx_chart(xx_chart)
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_xx"))
```

### 步驟 4：在 api_server.py 中加入 API endpoint

```python
@app.post("/api/xx")
async def api_xx(params: BirthParams):
    try:
        chart = compute_xx_chart(**_base_kwargs(params))
        return {"status": "ok", "data": _make_serializable(chart)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
```

### 步驟 5：加入測試

在 `tests/test_new_astrology.py` 中新建測試類別：

```python
class TestXXAstrology(unittest.TestCase):
    """Tests for XX astrology module."""

    def test_compute_chart_basic(self):
        chart = compute_xx_chart(
            year=1990, month=1, day=1, hour=12, minute=0,
            timezone=8.0, latitude=22.3193, longitude=114.1694,
            location_name="Hong Kong",
        )
        self.assertIsNotNone(chart)
        self.assertGreater(len(chart.planets), 0)

    def test_planet_longitudes_in_range(self):
        chart = compute_xx_chart(...)
        for p in chart.planets:
            self.assertGreaterEqual(p.longitude, 0.0)
            self.assertLess(p.longitude, 360.0)
```

### 步驟 6：更新文件

- 在 `README.md` 的體系列表中加入新體系
- 在 `CHANGELOG.md` 中記錄新增

## 提交規範

- Commit message 使用英文，簡潔描述改動
- 每個 PR 專注一個功能或修復
- 確保所有測試通過：`python -m pytest tests/ -q`
- 不要移除或修改無關的測試

## 程式碼風格

- 計算函式（`compute_*`）必須是純函式，不依賴 Streamlit
- 渲染函式（`render_*`）內部 `import streamlit as st`
- 使用 `@dataclass` 定義資料結構
- 使用 `astro/i18n.py` 管理所有 UI 文字
- 圖表主題使用 `astro/chart_theme.py` 中的統一色彩

## 新體系模組標準

建議新體系以「資料、計算、解讀、視覺化、UI」五層拆分，避免把所有邏輯塞進單一檔案。

### 建議目錄結構

```text
astro/<system_name>/
  __init__.py
  constants.py          # dataclass、常數、靜態對應資料
  data/__init__.py      # JSON / CSV 載入器（可快取）
  <system_name>.py      # compute_* 純函式與核心規則
  interpretations.py    # 解讀文字生成與推薦理由
  visualization.py      # SVG / 結構化視覺輸出（純函式）
```

### 一致性要求

1. `compute_*` 只接受基本型別參數，回傳 dataclass，方便 API、快取與測試。
2. 視覺化函式輸出 SVG / HTML 字串，不直接依賴 Streamlit。
3. 若體系需要推薦邏輯（天使、魔神、Aethyr、護符、remedy），優先重用 `astro/recommendation_engine.py`。
4. 若體系需要教育性說明，請在 `astro/system_guides.py` 補上「原理／使用情境／差異／相關體系」內容。
5. 若體系需要大型靜態表格或對應表，請放在 `data/` 並用快取載入，不要硬編碼在 render 層。

## 新體系開發 Checklist

- [ ] 在 `astro/system_registry.py` 註冊系統資料（名稱、分類、icon、tab_key、hint_key）
- [ ] 在 `astro/data/i18n_translations.json` 補齊 `tab_*`、`desc_*`、`spinner_*`、`sys_hint_*`
- [ ] 實作 `compute_*` 純函式與主要 dataclass
- [ ] 將解讀文字放入 `interpretations.py`，避免混進 renderer
- [ ] 將 SVG / 圖像輸出放入 `visualization.py`
- [ ] 若有推薦／排序邏輯，重用 `astro/recommendation_engine.py`
- [ ] 若要提高教育性，補上 `astro/system_guides.py`
- [ ] 在 `ui/handlers/tab_<system>/render.py` 使用一致的區塊順序：標題 → 教育說明 → 核心結果 → 視覺化 → 對照 / 參考
- [ ] 補齊最少一組基礎測試（資料載入、計算結果、關鍵輸出形狀）
- [ ] 更新 `README.md` 的體系列表與說明

## 回報問題

在 GitHub Issues 中提交問題時請附上：
1. 使用的出生資料（日期、時間、地點）
2. 出錯的體系名稱
3. 錯誤訊息截圖或文字
