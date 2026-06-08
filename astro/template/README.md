# 新增占星體系模板 (New Astrology System Template)

本目錄提供「新增占星體系」的完整樣板，幫助開發者快速擴展 kinastro。

## 步驟

1. **複製模板** — 將 `my_system.py` 複製到 `astro/` 或 `astro/<子目錄>/`
2. **實作計算** — 實作 `compute_xxx_chart()` 函式（必須為純函式，以支援 `@st.cache_data`）
3. **實作渲染** — 實作 `render_xxx_chart()` 函式（使用 Streamlit widgets）
4. **註冊到 registry** — 在 `astro/system_registry.py` 中加入新的 `System(...)`
5. **加入翻譯** — 在 `astro/data/i18n_translations.json` 加入對應翻譯 key
6. **撰寫測試** — 在 `tests/test_new_astrology.py` 加入至少 5 個測試
7. **更新文件** — 在 `CHANGELOG.md` 記錄新增體系

## 命名慣例

- Tab key: `tab_xxx`（如 `tab_maya`、`tab_mahabote`）
- 計算函式: `compute_xxx_chart()`
- 渲染函式: `render_xxx_chart()`
- 資料類: `XxxChart`（dataclass）
- 翻譯 key: 以 `xxx_` 為前綴

## 注意事項

- 計算函式參數必須是基本型別（int, float, str）以支援 Streamlit 快取
- 所有 `st.dataframe()` 應使用 `width="stretch"` 參數
- SVG 圖表應使用 `astro/chart_theme.py` 中的 `svg_header()` / `svg_footer()`
- 若需載入 JSON 資料，請使用 `@st.cache_data` 快取載入函式

## 建議的模組切分

```text
astro/<system_name>/
  __init__.py
  constants.py
  data/__init__.py
  <system_name>.py
  interpretations.py
  visualization.py
```

- `constants.py`：資料類別、常數、映射表
- `<system_name>.py`：主 `compute_*` 邏輯
- `interpretations.py`：解讀與推薦文字生成
- `visualization.py`：SVG / HTML 字串輸出（純函式）
- `data/`：大型對應表、JSON、CSV

## 新系統一致性 Checklist

- [ ] 回傳 dataclass，而不是鬆散 dict
- [ ] `compute_*` 純函式，不引用 Streamlit
- [ ] `render_*` 僅做 UI 組裝
- [ ] 若有推薦排序，重用 `astro/recommendation_engine.py`
- [ ] 若有教學內容，補上 `astro/system_guides.py`
- [ ] 若有大型靜態表格，放入 `data/` 並快取
- [ ] 設計至少一個 SVG / 結構化視覺輸出供 UI 與 API 重用
