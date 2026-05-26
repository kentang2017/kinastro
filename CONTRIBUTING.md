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

## 專案結構（2026 最新）

```
kinastro/
├── app.py                  # Streamlit 主應用（目前仍含 legacy dispatch，逐步瘦身中）
├── api_server.py           # FastAPI 後端（純計算 API）
├── astro/                  # 所有占星計算與資料
│   ├── system_registry.py  # ★ 84 體系中央元資料（推薦先看）
│   ├── systems/            # 共享基底（BaseChart 等，擴充中）
│   ├── <slug>/             # 新體系推薦結構
│   │   ├── calculator.py   # 純計算（**絕不可 import streamlit**）
│   │   ├── renderer.py     # Streamlit 渲染（可 lazy import st）
│   │   ├── constants.py
│   │   └── __init__.py     # 建議 lazy re-export（參考 andean/、maya/）
│   ├── qizheng/            # 七政四餘（演進中的大型 package）
│   ├── western/            # 西洋（多子模組）
│   ├── vedic/              # 印度
│   ├── ...                 # 80+ 其他體系（flat 舊檔與 package 混存，遷移中）
│   ├── i18n.py             # 雙語
│   ├── chart_theme.py      # 顏色 + SVG 公用
│   ├── template/           # 新體系模板（已現代化）
│   └── data/               # JSON 資料
├── ui/                     # 新 UI 抽象層（逐步接管）
│   ├── system_engine.py    # EXECUTION_REGISTRY + SystemHandler
│   ├── system_handlers/    # 各體系 handler（Phase 1+ 進行中）
│   └── components/         # birth_form, system_selector 等可重用元件
├── frontend/               # 複雜視覺化 renderer（某些體系專用）
├── tests/                  # ~40 個測試檔（體系專屬 + 整合）
├── docs/                   # 包含 ARCHITECTURE.md
├── scripts/                # 工具（含 audit_st_imports.py）
└── pyproject.toml          # 單一版本來源 + ruff/mypy 設定（Phase 0 起）
```

**重要原則**：
- 計算層零 Streamlit（用 `scripts/audit_st_imports.py` 檢查）。
- 優先 package + calculator/renderer 分離。
- 透過 `astro/system_registry.py` + `ui/system_engine.py` 註冊，而非狂改 app.py。

## 如何新增一個新的占星體系（2026 推薦流程）

**強烈建議**：採用 package + handler 模式，而非舊式單檔 + 直接改 app.py 巨型 if 鏈。

### 步驟 1：建立 package（推薦）

```bash
mkdir -p astro/mytrad
touch astro/mytrad/{__init__.py,calculator.py,renderer.py,constants.py}
```

`calculator.py`（**純淨**）：
```python
from dataclasses import dataclass
# 絕對不 import streamlit

@dataclass
class MyTradChart:
    # 建議共用欄位放前面（或繼承 systems.base.BaseChart）
    year: int
    # ... 其他出生資訊 + 體系特有結果

def compute_mytrad_chart(params: dict) -> MyTradChart:
    """純計算函式。"""
    ...
    return MyTradChart(...)
```

`renderer.py`（UI）：
```python
def render_mytrad_chart(chart: MyTradChart) -> None:
    import streamlit as st  # lazy
    from astro.i18n import t
    from astro.chart_theme import ...
    ...
```

`__init__.py`（lazy）參考 `andean/` 或 `maya/`。

### 步驟 2：宣告到 Registry

編輯 `astro/system_registry.py`，加入：
```python
_reg(System(
    id="tab_mytrad",
    name_zh="我的傳統",
    ...
    sub_tabs=[SubTab("mytrad_sub_natal", "natal")],
    ai_persona_key=...,
))
```

### 步驟 3：建立 Handler（強烈建議）

在 `ui/system_handlers/build_mytrad_handler.py`：
```python
from ui.system_engine import SystemHandler
from ui.components.birth_form import BirthChartParams

def build_mytrad_handler(*, compute_fn, render_fn, **deps) -> SystemHandler:
    @st.cache_data(...)
    def _cached(...): ...
    def _compute(p: BirthChartParams, opts): ...
    def _render(result, p, opts): ...
    return SystemHandler("tab_mytrad", _compute, _render)
```

### 步驟 4：註冊 + 相容

- 在 app.py 的 `_init_execution_registry_once` 附近註冊 handler。
- 因為有 `if EXECUTION_REGISTRY.run_system(...)` 守衛，舊 legacy 路徑自動跳過。
- 加入 i18n key、測試、必要時更新 wiki。

### 完整參考
- 模板：`astro/template/my_system.py`（已更新）。
- 良好範例：`astro/andean/`、`astro/maya/`。
- 架構說明：`docs/ARCHITECTURE.md`。
- Audit 工具：`python scripts/audit_st_imports.py`。

**舊流程（不推薦繼續擴大）**：直接在 app.py 加 if 分支 + flat 檔案。現有 legacy 會繼續支援，但新體系請走 handler 路線。

---

### 舊文件（已過時，僅供歷史參考）
以下內容為 2024-2025 早期版本，已不再是推薦做法。
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

## 回報問題

在 GitHub Issues 中提交問題時請附上：
1. 使用的出生資料（日期、時間、地點）
2. 出錯的體系名稱
3. 錯誤訊息截圖或文字
