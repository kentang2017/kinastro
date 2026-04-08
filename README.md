# ⭐ 堅占星 Kin Astro

<!-- Logo / Hero -->
<div align="center">

![Kin Astro](https://img.shields.io/badge/Kin_Astro-堅占星-FF6B6B?style=for-the-badge&logo=star&logoColor=white)
[![Python](https://img.shields.io/badge/Python-3.10+-00D4FF?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Swiss Ephemeris](https://img.shields.io/badge/Swiss%20Ephemeris-pyswisseph-FF8C00)](https://github.com/astrorigin/pyswisseph)
[![License](https://img.shields.io/badge/License-MIT-8B5CF6?style=flat-badge)](LICENSE)

**十一體系占星排盤系統 — 中國・紫微斗數・西洋・印度・宿曜道・泰國・卡巴拉・阿拉伯・瑪雅・緬甸・古埃及十度區間**

*Multi-System Astrology Platform — Chinese, Zi Wei, Western, Vedic, Japanese, Thai, Kabbalah, Arabic, Maya, Myanmar & Egyptian Decans*

</div>

---

## ✨ 特色亮點

| | |
|---|---|
| 🔮 **十一體系合一** | 在同一個介面中切換十一種占星體系，無需來回切換工具 |
| 🪐 **九曜精密計算** | 使用瑞士星曆表 (Swiss Ephemeris) pyswisseph 進行高精度天文計算 |
| 🌏 **全球化支援** | 內建全球 10+ 個主要城市，亦支援自訂經緯度即時排盤 |
| 🎨 **彩色互動介面** | Streamlit 驅動的現代化 Web UI，響應式排盤結果 |
| 📱 **響應式設計** | 適配桌面與移動設備，隨時隨地查閱星盤 |
| 🆓 **開源免費** | MIT 授權，完整原始碼可自由使用與擴展 |

---

## 🧭 支援的占星體系

### 🀄 七政四餘（中國傳統占星）

中國千年傳承的占星術，以恆星黃道為基礎。

- **七政**：太陽、太陰（月亮）、水星、金星、火星、木星、土星
- **四餘**：羅睺（北交點）、計都（南交點）、月孛（遠地點）、紫氣
- **十二宮**：命宮、財帛宮、兄弟宮、夫妻宮、子女宮、僕役宮
- **二十八宿**：東方青龍、北方玄武、西方白虎、南方朱雀
- **十二星次**：星紀、玄枵、娵訾、降婁、大梁、實沈
- **相位**：合、沖、刑、三合、六合

---

### 🌍 西洋占星（Western Astrology）

全球最流行的占星體系，以回歸黃道為基準。

- **十大星曜**：太陽、月亮、水星、金星、火星、木星、土星、天王星、海王星、冥王星、 北交點
- **十二星座**：白羊座至雙魚座（含守護星與元素屬性）
- **十二宮位**：Placidus 等分宮制，自動計算宮首度數
- **五大相位**：合、沖、刑、三合、六合
- **逆行檢測**：自動標記逆行中的星曜
- **輪盤圖**：視覺化星盤輪圖

---

### 🙏 印度占星 Jyotish（Vedic Astrology）

源於印度的古老占星體系，使用恆星黃道與 Lahiri 歲差。

- **九曜 Navagraha**：太陽、月亮、火星、水星、木星、金星、土星、羅睺、計都
- **十二星座 Rashi**：Mesha（白羊）至 Meena（雙魚）
- **二十七宿 Nakshatra**：Ashwini 至 Revati，每宿 13°20'，各分四足 (Pada)
- **七曜管宿**：每顆曜主管 3 個 Nakshatra（太陽管 Krittika 等）
- **南印度方盤**：宮位固定・行星流動的 4×4 網格
- **北印度方盤**：以 Lagna 為起點的旋轉宮系統
- **歲差修正**：內建 Lahiri Ayanamsa 自動校正

---

### 🈳 宿曜道（日本 Yojōdō）

9 世紀由空海大師自印度傳入日本，融合佛教密宗與道家思想。

- **二十八宿**：比印度多出 Abhijit（牛宿），共 28 宿
- **六曜 Rokuyō**：先勝・友引・先負・仏滅・大安・赤口
- **Moon 定曜**：六曜由 Moon 所在宿決定
- **宿曜道方盤**：4×7 網格，二十八宿沿圓環排列
- **象徵符號**：每宿有獨特漢字符號（馬、彡、卍、兔、蚯…）

---

### 🐘 泰國占星（Thai Astrology）

以印度 Jyotish 為基礎，融合泰國佛教文化與本土占星傳統。

- **九曜**：與印度 Jyotish 相同（太陽至計都）
- **十二星座**：泰語命名的恆星黃道星座
- **日主星**：根據出生星期判定守護星（星期日=太陽，星期一=月亮…）
- **泰式方盤**：泰語標示的占星盤面

---

### ✡ 卡巴拉占星（Kabbalah Astrology）

結合猶太神祕主義與占星術，以回歸黃道呈現。

- **生命之樹**：十個質點（Sephiroth）對應不同行星能量
- **二十二希伯來字母**：對應黃道星座與行星
- **塔羅對應**：每個星座對應一張塔羅大牌
- **回歸黃道**：與西洋占星相同的黃道系統

---

### ☪ 阿拉伯占星（Arabic Astrology）

源自中世紀伊斯蘭黃金時代，融合希臘與波斯天文傳統。

- **阿拉伯點 (Arabic Parts / Lots)**：透過上升點與行星經度加減運算，推導幸運點、精神點等敏感度數
- **日夜盤 (Sect)**：根據太陽位置區分日盤與夜盤，影響阿拉伯點公式
- **行星廟旺落陷 (Essential Dignities)**：入廟、入旺、落陷、入弱
- **回歸黃道 (Tropical Zodiac)**：使用 Placidus 宮位制

---

### 🌟 紫微斗數（Zi Wei Dou Shu）

中國傳統命理學最重要的排盤體系之一，相傳由陳希夷整理創立。

- **十四主星**：紫微、天機、太陽、武曲、天同、廉貞；天府、太陰、貪狼、巨門、天相、天梁、七殺、破軍
- **十二宮位**：命宮、兄弟宮、夫妻宮、子女宮、財帛宮、疾厄宮、遷移宮、交友宮、官祿宮、田宅宮、福德宮、父母宮
- **五行局**：水二局、木三局、金四局、土五局、火六局
- **農曆排盤**：以農曆生辰（年、月、日、時辰）為基礎

---

### 🏺 瑪雅占星（Maya Astrology）

源自瓜地馬拉瑪雅文明的天文與曆法傳統。

- **Long Count（長紀年）**：以 B'ak'tun、Ka'tun、Tu'n、Winal、K'in 計算天數
- **Tzolkin（神聖曆）**：260 天循環，13 數字 × 20 神明名
- **Haab（民用曆）**：365 天，18 月 × 20 日 + 5 Wayeb 無日
- **Calendar Round**：Tzolkin × Haab 同步循環，約 52 年一輪
- **行星疊加**：結合西方占星行星位置對應 Tzolkin 能量

---

### 🇲🇲 緬甸占星（Mahabote / Myanmar Astrology）

緬甸傳統占星術，Mahabote (မဟာဘုတ်) 意為「大創造」。

- **七曜行星**：日、月、火、水、木、金、土，對應星期日至星期六
- **羅睺 (Rahu)**：星期三傍晚出生者歸羅睺管轄
- **八方位**：每顆行星對應一個羅盤方位
- **七宮位**：本命、壽命、意識、身體、權勢、死亡、道德
- **行星大運 (Atar)**：七星循環共 96 年，主宰人生各階段
- **計算公式**：Mahabote 值 = (緬甸年 + 星期數) mod 7

---

### 🏛️ 古埃及十度區間（Decanic Astrology / 36 Decans）

源自古埃及數千年前的天文計時系統，是西洋占星學最古老的分區技法之一。

- **36 個 Decans**：黃道 360° 每 10° 劃分為一個 Decan（十度區間），每個星座含 3 個 Decan
- **古埃及星神**：每個 Decan 對應一位古埃及神靈（來自棺蓋對角星表、Dendera Zodiac 等文獻）
- **迦勒底行星統治 (Chaldean Order)**：Mars → Sun → Venus → Mercury → Moon → Saturn → Jupiter 循環
- **三重統治 (Triplicity)**：根據元素分配行星統治權
- **塔羅小阿卡納 (Minor Arcana)**：Golden Dawn 傳統，36 Decans 對應塔羅牌 2–10 號
- **本質尊貴 (Essential Dignities)**：Face/Decan 尊貴計分（+1 分），含完整廟旺落陷摘要
- **今日 Decan**：根據當前太陽位置自動顯示今日十度區間
- **Plotly 輪盤圖**：視覺化 36 Decans 的 Dendera Zodiac 外環
- **文化尊重提示**：說明古埃及 Decans 的歷史起源與現代詮釋差異

> 📖 此工具為文化、歷史與占星學習用途。古埃及 Decans 起源於數千年前的天文計時系統，現代解讀僅供參考。

---

## 🚀 快速開始

```bash
# 1. 複製儲存庫
git clone https://github.com/kentang2017/kinastro.git
cd kinastro

# 2. 安裝相依套件
pip install -r requirements.txt

# 3. 啟動應用
streamlit run app.py
```

> **需求**：Python 3.10+

---

## 📁 專案結構

```
kinastro/
├── app.py                      # Streamlit 主應用程式
├── astro/
│   ├── calculator.py           # 七政四餘核心計算引擎
│   ├── chart_renderer.py       # 中國占星 UI 渲染函數
│   ├── constants.py            # 常量與參考資料
│   ├── indian.py               # 印度占星 (Jyotish) 排盤模組
│   ├── sukkayodo.py            # 日本宿曜道 (Yojōdō) 排盤模組
│   ├── thai.py                 # 泰國占星排盤模組
│   ├── western.py              # 西洋占星排盤模組
│   ├── kabbalistic.py          # 卡巴拉占星排盤模組
│   ├── arabic.py               # 阿拉伯占星排盤模組
│   ├── ziwei.py                # 紫微斗數排盤模組
│   ├── maya.py                 # 瑪雅占星排盤模組
│   ├── mahabote.py             # 緬甸占星 (Mahabote) 排盤模組
│   ├── decans_data.py          # 古埃及十度區間 36 Decans 資料庫
│   └── decans.py               # 古埃及十度區間排盤模組
├── tests/
│   ├── test_calculator.py      # 計算模組單元測試
│   └── test_new_astrology.py  # 新增功能測試
├── requirements.txt            # Python 相依套件
├── README.md                   # 本說明文件
└── LICENSE                     # MIT 授權
```

---

## 🛠️ 技術棧

| 元件 | 技術 |
|------|------|
| 前端框架 | [Streamlit](https://streamlit.io/) — 互動式 Python Web 框架 |
| 星曆計算 | [pyswisseph](https://github.com/astrorigin/pyswisseph) — 瑞士星曆表 |
| 視覺化 | [Plotly](https://plotly.com/) — 互動式圖表（Decan 輪盤圖）|
| 語言 | Python 3.10+ |
| 黃道系統 | 恆星黃道（Lahiri 歲差）& 回歸黃道 |

---

## 🧪 執行測試

```bash
pip install pytest
pytest tests/
```

---

## 🤝 貢獻

歡迎提交 Issue 或 Pull Request！所有貢獻都會被感謝。

---

## 📜 授權

本專案採用 [MIT License](LICENSE) 授權。
