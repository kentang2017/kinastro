# Handler 遷移指南

## 目標

將 `app.py` 中的巨型 if/elif dispatch 邏輯遷移到 modular handler 架構，實現：
- `app.py` 從 6.3k LOC 降至 < 3k LOC
- 計算/渲染分離（compute layer 零 Streamlit 依賴）
- 可獨立測試的系統 handler
- 新體系快速接入（腳手架生成）

## 架構概述

```
┌─────────────────────────────────────────────────────────────┐
│ app.py (Legacy + New Hybrid)                                │
│  - UI tabs, birth form, session state                       │
│  - EXECUTION_REGISTRY.run_system() → tries new handlers     │
│  - if not handled → fallback to legacy if/elif chain        │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ ui/system_engine.py                                         │
│  - SystemHandler (compute + render + options_schema)        │
│  - EXECUTION_REGISTRY (singleton)                           │
│  - run_system() with spinner, error boundary                │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ ui/system_handlers/                                         │
│  - build_ziwei_handler.py (Phase 1 example)                 │
│  - build_andean_handler.py (Phase 2 example)                │
│  - build_western_handler.py                                 │
│  - build_vedic_handler.py                                   │
│  - build_chinese_handler.py                                 │
│  - ... (more systems)                                       │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ astro/<system>/                                             │
│  - calculator.py (PURE: no Streamlit)                       │
│  - renderer.py (Streamlit allowed)                          │
│  - constants.py, models.py                                  │
└─────────────────────────────────────────────────────────────┘
```

## 遷移步驟

### 步驟 1：確認系統已符合架構要求

檢查清單：
- [ ] `compute_*` 函式無 `import streamlit`（用 `scripts/audit_st_imports.py` 檢查）
- [ ] `compute_*` 接受 primitive args 或 `BirthChartParams`
- [ ] `compute_*` 返回 dataclass / dict（JSON-serializable）
- [ ] `render_*` 可獨立調用（不依賴 global session_state）

### 步驟 2：建立 Handler

**選項 A：使用腳手架生成**

```bash
python scripts/generate_handler.py \
  --system-id tab_maya \
  --system-name Maya \
  --compute-fn compute_maya_chart \
  --render-fn render_maya_chart
```

**選項 B：手動建立**

參考 `build_ziwei_handler.py` 或 `build_andean_handler.py`。

### 步驟 3：註冊 Handler

在 `app.py` 的 `_init_execution_registry_once()` 中加入：

```python
from ui.system_handlers.build_maya_handler import build_maya_handler
from astro.maya import compute_maya_chart, render_maya_chart

EXECUTION_REGISTRY.register(
    build_maya_handler(
        compute_maya_chart=compute_maya_chart,
        render_maya_chart=render_maya_chart,
        ai_button_sink=_render_ai_button,
    )
)
```

### 步驟 4：測試

1. 運行 `streamlit run app.py`
2. 選擇遷移的體系，確認排盤正常
3. 確認 AI 分析按鈕正常
4. 確認子分頁（如有）正常

### 步驟 5：清理 Legacy 代碼（可選）

當確認 handler 運作正常後，可註解或移除 `app.py` 中對應的 if/elif 分支。

**重要**：保留 legacy fallback 直到 100% 測試通過。

## 優先遷移清單

| 體系 | System ID | Compute Fn | Render Fn | 狀態 |
|------|-----------|------------|-----------|------|
| 紫微斗數 | tab_ziwei | compute_ziwei_chart | render_ziwei_chart | ✅ Phase 1 |
| 安地斯 | tab_andean | compute_andean_chart | render_andean_chart_ui | ✅ Phase 2 |
| 西洋占星 | tab_western | compute_western_chart | render_western_chart | 🔄 Template |
| 印度占星 | tab_indian | compute_vedic_chart | render_vedic_chart | 🔄 Template |
| 七政四餘 | tab_chinese | compute_chart | render_full_chart | 🔄 Template |
| 瑪雅 | tab_maya | compute_maya_chart | render_maya_chart | ⏳ Pending |
| 阿茲特克 | tab_aztec | compute_aztec_chart | render_aztec_chart | ⏳ Pending |
| 阿拉伯 | tab_arabic | compute_arabic_chart | render_arabic_chart | ⏳ Pending |
| 希臘 | tab_hellenistic | compute_hellenistic_chart | render_hellenistic_chart | ⏳ Pending |
| 藏傳 | tab_tibetan | compute_tibetan_chart | render_tibetan_chart | ⏳ Pending |

## 測試腳本

運行腳手架生成器測試：

```bash
python scripts/generate_handler.py --help
```

檢查 Streamlit 依賴：

```bash
python scripts/audit_st_imports.py
```

## 常見問題

### Q: 如果 compute 函式需要額外參數（如 gender, vietnam_mode）？

在 `_compute` 中注入：

```python
def _compute(params: BirthChartParams, options: dict[str, Any]):
    payload = {**params.to_dict(), "gender": params.gender}
    return _cached_compute(payload, vietnam_mode=options.get("vietnam_mode", False))
```

### Q: 如何处理子分頁（sub-tabs）？

在 handler 的 `options_schema` 中定義 `sub_tab`，在 `_compute` 中根據 sub_tab 返回不同結果。

參考 `build_western_handler.py` 處理 transit/synastry/return。

### Q: Handler 遷移後，app.py 還需要保留什麼？

- Birth form UI 元件
- Session state 管理
- `_init_execution_registry_once()` 註冊
- Legacy fallback（直到 100% 遷移完成）

## 下一步

1. 使用腳手架為剩餘 80+ 體系生成 handler
2. 分批遷移（每次 5-10 個體系）
3. 建立測試套件確保遷移無破環
4. 最終移除 `app.py` legacy dispatch
