<div align="center">

# ⭐ kinastro — 堅占星排盤

**七政四餘、西洋占、印占排盤系統 ｜ Chinese, Vedic & Thai Traditional Astrology Chart Calculator**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.52-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Swiss Ephemeris](https://img.shields.io/badge/Swiss%20Ephemeris-pyswisseph-orange)](https://github.com/astrorigin/pyswisseph)

</div>

---

## 🌏 中文說明

### 簡介

**kinastro（堅七政四餘）** 是一個基於 [Streamlit](https://streamlit.io/) 的互動式中國傳統占星術排盤系統。使用 [pyswisseph](https://github.com/astrorigin/pyswisseph)（瑞士星曆表）進行精確的天文計算，提供日月五星（七政）及羅睺、計都、月孛、紫氣（四餘）的天文位置。

### 什麼是七政四餘？

**七政四餘**是中國傳統占星術的核心體系：

- **七政（日月五星）**：太陽、太陰（月亮）、水星、金星、火星、木星、土星
- **四餘（虛星）**：羅睺（北交點）、計都（南交點）、月孛（平均遠地點）、紫氣

### 功能特色

- 🪐 計算 **11 顆星曜**（七政 + 四餘）的精確天文位置
- 🗺️ 支援全球多個城市預設（北京、上海、香港、台北、東京等）及自訂經緯度
- 🏛️ 傳統 **十二宮位** 分布（命宮、財帛宮、兄弟宮等）
- 🌟 **二十八宿** 對應系統（東方青龍、北方玄武、西方白虎、南方朱雀）
- 🔄 **星曜相位** 分析（合、沖、刑、三合、六合）
- 📐 黃道十二宮及中國十二星次對照
- 🔙 逆行星曜自動檢測
- 🎨 彩色顯示的傳統排盤方格圖

### 快速開始

```bash
# 複製儲存庫
git clone https://github.com/kentang2017/kinastro.git
cd kinastro

# 安裝相依套件
pip install -r requirements.txt

# 啟動應用
streamlit run app.py
```

---

## 🌐 English Description

### Introduction

**kinastro** is an interactive **Chinese Traditional Astrology (七政四餘) Chart Calculator** built with [Streamlit](https://streamlit.io/). It uses [pyswisseph](https://github.com/astrorigin/pyswisseph) (Swiss Ephemeris) for precise astronomical calculations, computing the positions of the Seven Governors (七政) and Four Remainders (四餘).

### What is Seven Governors and Four Remainders (七政四餘)?

This is the core system of traditional Chinese astrology:

- **Seven Governors (七政)**: Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn
- **Four Remainders (四餘)**: Rahu (North Node), Ketu (South Node), Yuebei (Mean Apogee/Lilith), Ziqi (Purple Gas)

### Features

- 🪐 Precise positions for **11 celestial bodies** (7 governors + 4 remainders)
- 🗺️ Preset cities worldwide (Beijing, Shanghai, Hong Kong, Taipei, Tokyo, etc.) and custom coordinates
- 🏛️ Traditional **Twelve Houses/Palaces** (命宮, 財帛宮, 兄弟宮, etc.)
- 🌟 **28 Lunar Mansions** mapping (Azure Dragon, Black Tortoise, White Tiger, Vermilion Bird)
- 🔄 **Aspect analysis** (conjunction, opposition, square, trine, sextile)
- 📐 Western zodiac and Chinese Star Stations cross-reference
- 🔙 Automatic retrograde detection
- 🎨 Color-coded traditional square chart grid

### Quick Start

```bash
# Clone the repository
git clone https://github.com/kentang2017/kinastro.git
cd kinastro

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

---

## 📁 Project Structure / 項目結構

```
kinastro/
├── app.py                  # Streamlit main app / 主應用程式
├── astro/
│   ├── calculator.py       # Core computation engine / 核心計算引擎
│   ├── chart_renderer.py   # UI rendering functions / 介面渲染函數
│   └── constants.py        # Constants & reference data / 常量與參考資料
├── tests/
│   └── test_calculator.py  # Unit tests / 單元測試
├── requirements.txt        # Python dependencies / 相依套件
└── README.md
```

## 🛠️ Tech Stack / 技術棧

| Component | Technology |
|-----------|-----------|
| Frontend / 前端 | [Streamlit](https://streamlit.io/) |
| Ephemeris / 星曆計算 | [pyswisseph](https://github.com/astrorigin/pyswisseph) (Swiss Ephemeris) |
| Language / 語言 | Python 3.10+ |

## 🧪 Running Tests / 運行測試

```bash
pip install pytest
pytest tests/
```

## 🤝 Contributing / 貢獻

Contributions are welcome! Feel free to open issues or submit pull requests.

歡迎貢獻！請隨時提交 Issue 或 Pull Request。
