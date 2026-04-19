# ⭐ 堅占星 Kin Astro

<!-- Logo / Hero -->
<div align="center">

![Kin Astro](https://img.shields.io/badge/Kin_Astro-堅占星-FF6B6B?style=for-the-badge&logo=star&logoColor=white)
![Version](https://img.shields.io/badge/Version-2.0.0-00C853?style=for-the-badge)
![Systems](https://img.shields.io/badge/Systems-21-FFD700?style=for-the-badge)
[![Python](https://img.shields.io/badge/Python-3.9+-00D4FF?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.52-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Swiss Ephemeris](https://img.shields.io/badge/Swiss%20Ephemeris-pyswisseph-FF8C00)](https://github.com/astrorigin/pyswisseph)
[![License](https://img.shields.io/badge/License-MIT-8B5CF6)](LICENSE)

**二十一體系占星排盤系統 — 中國・紫微斗數・策天飛星・西洋・希臘・印度・Jaimini・宿曜道・泰國・緬甸・蒙古祖爾海・藏傳時輪金剛・卡巴拉・阿拉伯・也門・瑪雅・阿茲特克・古埃及十度區間・納迪・巴比倫・萬化仙禽**

*21-System Astrology Platform — Chinese, Zi Wei, Ce Tian Flying Stars, Western, Hellenistic, Vedic, Jaimini, Japanese Sukkayodo, Thai, Myanmar, Mongolian Zurkhai, Tibetan Kalachakra, Kabbalah, Arabic (incl. Picatrix & Shams al-Maʻārif), Yemeni Rasulid, Maya, Aztec, Egyptian Decans, Nadi, Babylonian, WanHua XianQin*

</div>

---

## 📑 目錄 | Table of Contents

- [✨ 特色亮點 | Highlights](#-特色亮點--highlights)
- [🧭 體系總覽 | Systems at a Glance](#-體系總覽--systems-at-a-glance)
- [🔍 各體系詳細介紹 | System Details](#-各體系詳細介紹--system-details)
- [🚀 快速開始 | Quick Start](#-快速開始--quick-start)
- [🔌 API 後端 | API Backend](#-api-後端--api-backend)
- [📁 專案結構 | Project Structure](#-專案結構--project-structure)
- [🛠️ 技術棧 | Tech Stack](#️-技術棧--tech-stack)
- [🧪 執行測試 | Run Tests](#-執行測試--run-tests)
- [🤝 貢獻 | Contributing](#-貢獻--contributing)
- [📜 授權 | License](#-授權--license)

---

## ✨ 特色亮點 | Highlights

| | 中文 | English |
|---|---|---|
| 🔮 **二十一體系合一** | 在同一個介面中切換二十一種占星體系，無需來回切換工具 | Switch between 21 astrology systems in one unified interface |
| 🪐 **精密天文計算** | 使用瑞士星曆表 (Swiss Ephemeris) pyswisseph 進行高精度天文計算 | High-precision astronomical calculations powered by Swiss Ephemeris (pyswisseph) |
| 🤖 **AI 智慧分析** | 整合 Cerebras AI，一鍵生成命盤深度解讀報告 | Integrated Cerebras AI for one-click in-depth chart analysis |
| 🌏 **全球化支援** | 內建全球多個主要城市，亦支援自訂經緯度即時排盤 | Built-in global city presets with custom latitude/longitude support |
| 🌐 **中英雙語** | 介面支援中文與英文切換 | Full Chinese and English bilingual interface |
| 🎨 **彩色互動介面** | Streamlit 驅動的現代化 Web UI，響應式排盤結果 | Modern interactive Web UI powered by Streamlit |
| 📱 **響應式設計** | 適配桌面與移動設備，隨時隨地查閱星盤 | Responsive design for desktop and mobile devices |
| 🔌 **REST API** | FastAPI 後端提供所有體系的 JSON 計算 API，可獨立部署 | FastAPI backend providing JSON computation APIs for all systems |
| 💾 **儲存與匯出** | 儲存／載入排盤參數，支援 TXT、CSV、PDF 匯出 | Save/load chart parameters, export to TXT, CSV, PDF |
| 🆓 **開源免費** | MIT 授權，完整原始碼可自由使用與擴展 | Open-source under MIT License, free to use and extend |

---

## 🧭 體系總覽 | Systems at a Glance

> 💡 體系按分類顯示：熱門 → 中國 → 西方 → 亞洲 → 中東 → 古代文明 → 美索不達米亞
>
> *Systems displayed by category: Popular → Chinese → Western → Asian → Middle East → Ancient → Mesopotamia*

| # | 體系 System | 黃道 Zodiac | 子功能 Sub-features |
|:-:|---|---|---|
| 1 | 🌍 西洋占星 Western | 回歸 Tropical | 本命盤・行星過運・太陽回歸・合盤比較・Ptolemy 尊貴 |
| 2 | 🌟 紫微斗數 Zi Wei | 農曆 Lunar | 十四主星・十二宮位・五行局 |
| 3 | 🀄 七政四餘 Chinese | 恆星 Sidereal | 本命盤・神煞・年限大運・流時對盤・張果星宗・擇日 |
| 4 | 🐦‍⬛ 萬化仙禽 WanHua XianQin | 農曆 Lunar | 二十八宿禽星・十二宮・吞啗合戰・相胎賦・貴賤格 |
| 5 | 🌠 策天飛星 Ce Tian | 農曆 Lunar | 十八飛星・十一正曜七副曜・飛星四化・單宮獨斷 |
| 6 | 🏺 希臘 Hellenistic | 回歸 Tropical | Greek Lots・Egyptian Bounds・Profections・Zodiacal Releasing・百論 |
| 7 | ✡ 卡巴拉 Kabbalah | 回歸 Tropical | 生命之樹・希伯來字母・塔羅 |
| 8 | 🙏 印度占星 Vedic | 恆星 Sidereal | 星座盤・大運 Dasha・Ashtakavarga・Yogas・BPHS・Varga 分盤 |
| 9 | 🔱 納迪 Nadi | 恆星 Sidereal | 三大脈輪・27 星宿・納迪宮分 |
| 10 | 🕉️ Jaimini 占星 | 恆星 Sidereal | Chara Karaka・Rashi Drishti・Argala・Arudha Pada・Chara Dasha |
| 11 | 🈳 宿曜道 Sukkayodo | 恆星 Sidereal | 二十八宿・六曜・方盤 |
| 12 | 🐘 泰國占星 Thai | 恆星 Sidereal | 泰式盤面・九宮格占卜・พรหมชาติ |
| 13 | 🇲🇲 緬甸 Mahabote | 星期制 Weekday | 八方位・七宮・行星大運 |
| 14 | 🇲🇳 祖爾海 Zurkhai | 藏曆 Tibetan | 12 生肖・五行・擇吉 |
| 15 | 🏔️ 藏傳時輪金剛 Tibetan | 藏曆 Tibetan | Mewa 九宮・Parkha 八卦・五力系統・時輪金剛曼荼羅 |
| 16 | ☪ 阿拉伯 Arabic | 回歸 Tropical | 阿拉伯點・Picatrix 星體魔法・太陽知識大全・MS164 手稿 |
| 17 | 🕌 也門 Yemeni | 恆星 Sidereal | 28 月宿護符魔法・Anwāʼ 天氣預兆・Firdaria 週期 |
| 18 | 🏺 瑪雅 Maya | 瑪雅曆 Maya Cal. | Tzolkin・Haab・Long Count |
| 19 | 🦅 阿茲特克 Aztec | 阿茲特克曆 | Tonalpohualli・Trecena・守護神祇 |
| 20 | 🏛️ 古埃及 Decans | 回歸 Tropical | 36 Decans・塔羅・Dendera 輪盤圖 |
| 21 | 🏛️ 巴比倫 Babylonian | 恆星 Sidereal | MUL.APIN 星表・K.8538 星盤・Enūma Anu Enlil 預兆 |

---

## 🔍 各體系詳細介紹 | System Details

### 🀄 七政四餘（中國傳統占星）| Chinese Traditional Astrology

中國千年傳承的占星術，以恆星黃道為基礎。

*Ancient Chinese astrology with a thousand-year heritage, based on the sidereal zodiac.*

- **七政 / Seven Governors**：太陽、太陰（月亮）、水星、金星、火星、木星、土星 — Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn
- **四餘 / Four Extras**：羅睺（北交點）、計都（南交點）、月孛（遠地點）、紫氣 — Rahu (North Node), Ketu (South Node), Yuebei (Apogee), Ziqi
- **十二宮 / Twelve Houses**：命宮、財帛宮、兄弟宮、夫妻宮、子女宮、僕役宮 etc.
- **二十八宿 / 28 Mansions**：東方青龍、北方玄武、西方白虎、南方朱雀 — Azure Dragon, Black Tortoise, White Tiger, Vermilion Bird
- **十二星次 / Twelve Jupiter Stations**：星紀、玄枵、娵訾、降婁、大梁、實沈 etc.
- **相位 / Aspects**：合、沖、刑、三合、六合 — Conjunction, Opposition, Square, Trine, Sextile

<details>
<summary>📂 六個子分頁 | 6 Sub-tabs</summary>

| 子分頁 | 功能 |
|---|---|
| **本命盤** | 二十八宿環形盤面、八字四柱、行星表、宮位表、相位摘要 |
| **神煞** | 30+ 神煞（天乙貴人、文昌星、驛馬等）、十二長生 |
| **年限大運** | 行星主運週期，以命宮地支與性別推算 |
| **流時對盤** | 自選日期時間的流時盤與本命盤對照 |
| **張果星宗** | 星入宮位解讀（1060 條星宮語句）、128 星組格局 |
| **擇日** | 天干地支評分的日期挑選工具 |
</details>

---

### 🌟 紫微斗數（Zi Wei Dou Shu）

中國傳統命理學最重要的排盤體系之一，相傳由陳希夷整理創立。

*One of the most important Chinese traditional fortune-telling systems, attributed to Chen Xiyi.*

- **十四主星 / 14 Major Stars**：紫微、天機、太陽、武曲、天同、廉貞；天府、太陰、貪狼、巨門、天相、天梁、七殺、破軍
- **十二宮位 / 12 Palaces**：命宮、兄弟宮、夫妻宮、子女宮、財帛宮、疾厄宮、遷移宮、交友宮、官祿宮、田宅宮、福德宮、父母宮
- **五行局 / Five Element Groups**：水二局、木三局、金四局、土五局、火六局
- **農曆排盤 / Lunar Calendar**：以農曆生辰（年、月、日、時辰）為基礎 — Chart based on lunar birth date and time

---

### 🌠 策天飛星紫微斗數（Ce Tian 18 Flying Stars）

紫微斗數的古法前身與重要分支，源自明代《十八飛星策天紫微斗數全集》。

*An ancient predecessor and important branch of Zi Wei Dou Shu, from the Ming Dynasty text «Collection of Ce Tian 18 Flying Stars Zi Wei Dou Shu».*

- **十八飛星 / 18 Flying Stars**：十一正曜 + 七副曜，每宮必有正副曜，不存在空宮 — 11 primary + 7 auxiliary stars, no empty palaces
- **飛星技術 / Flying Star Technique**：星曜由本宮飛入他宮，產生吉凶影響，早於後世四化飛星系統 — Stars fly from home palace to other palaces, predating the Four Transformation system
- **單宮獨斷 / Single Palace Interpretation**：以單宮解讀為主，較少使用三方四會 — Focuses on single-palace interpretation rather than trine/square groupings
- **節氣影響 / Solar Term Effects**：需計算節氣對星曜落度的影響 — Solar terms affect star placement
- **農曆排盤 / Lunar Calendar**：使用農曆新年查找表搭配朔望月計算 — Chart based on lunar new year lookup tables with synodic month calculations

---

### 🌍 西洋占星（Western Astrology）

全球最流行的占星體系，以回歸黃道為基準。

*The world's most popular astrology system, based on the tropical zodiac.*

- **十大星曜 / Celestial Bodies**：太陽、月亮、水星、金星、火星、木星、土星、天王星、海王星、冥王星、北交點 — Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto, North Node
- **十二星座 / 12 Zodiac Signs**：白羊座至雙魚座（含守護星與元素屬性）— Aries to Pisces (with ruling planets and element attributes)
- **十二宮位 / 12 Houses**：Placidus 分宮制，自動計算宮首度數 — Placidus house system with automatic cusp calculation
- **五大相位 / 5 Major Aspects**：合、沖、刑、三合、六合 — Conjunction, Opposition, Square, Trine, Sextile
- **逆行檢測 / Retrograde Detection**：自動標記逆行中的星曜 — Automatic retrograde planet labeling
- **輪盤圖 / Wheel Chart**：視覺化星盤輪圖 — Interactive visual wheel chart

<details>
<summary>📂 五個子分頁 | 5 Sub-tabs</summary>

| 子分頁 | 功能 |
|---|---|
| **本命盤 Natal** | 星盤輪圖、恆星合相（25 顆古典恆星）、小行星（Chiron、Ceres、Pallas、Juno、Vesta）、匯出 TXT/CSV/PDF |
| **行星過運 Transit** | 即時過運行星與本命盤的相位分析 |
| **太陽回歸 Solar Return** | Newton-Raphson 精密太陽回歸盤計算 |
| **合盤比較 Synastry** | 雙人交叉相位、和諧分數、元素相容性分析 |
| **Ptolemy 尊貴 Dignity** | 行星本質尊貴表（廟、旺、界、三分、面） |
</details>

---

### 🙏 印度占星 Jyotish（Vedic Astrology）

源於印度的古老占星體系，使用恆星黃道與 Lahiri 歲差。

*Ancient Indian astrology system using the sidereal zodiac with Lahiri ayanamsa.*

- **九曜 Navagraha**：太陽、月亮、火星、水星、木星、金星、土星、羅睺、計都 — Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu
- **十二星座 Rashi**：Mesha（白羊）至 Meena（雙魚）— Mesha (Aries) to Meena (Pisces)
- **二十七宿 Nakshatra**：Ashwini 至 Revati，每宿 13°20'，各分四足 (Pada) — 27 lunar mansions, each 13°20', divided into 4 padas
- **南印度方盤 / South Indian Chart**：宮位固定・行星流動的 4×4 網格 — Fixed-house, planet-moving 4×4 grid
- **北印度方盤 / North Indian Chart**：以 Lagna 為起點的旋轉宮系統 — Lagna-based rotating house system
- **歲差修正 / Ayanamsa Correction**：內建 Lahiri Ayanamsa 自動校正

<details>
<summary>📂 六個子分頁 | 6 Sub-tabs</summary>

| 子分頁 | 功能 |
|---|---|
| **星座盤 Rashi** | 南印度 / 北印度方盤、行星配置 |
| **大運 Dasha** | Vimshottari 120 年大運（含 Antardasha 子期）、Yogini 36 年大運 |
| **Ashtakavarga** | 七行星 Bhinnashtakavarga + Sarvashtakavarga 積分表 |
| **Yogas** | 12 種瑜伽檢測（Gajakesari、Kemdruma、Gandanta、5 Mahapurusha 等） |
| **BPHS** | Brihat Parashara Hora Shastra 解析引擎 |
| **Varga 分盤** | Shodasa Varga 16 分盤（D1–D60），含 Navamsa (D9)、Dashamsha (D10) 等 |
</details>

---

### 🈳 宿曜道（日本 Yōjōdō）| Japanese Sukkayodo

9 世紀由空海大師自印度傳入日本，融合佛教密宗與道家思想。

*Brought to Japan by Kūkai (Kōbō Daishi) in the 9th century, blending Esoteric Buddhism with Taoist thought.*

- **二十八宿 / 28 Mansions**：比印度多出 Abhijit（牛宿），共 28 宿 — Includes Abhijit (absent in Indian system), totaling 28 mansions
- **六曜 Rokuyō**：先勝・友引・先負・仏滅・大安・赤口 — Six daily fortune indicators
- **Moon 定曜**：六曜由 Moon 所在宿決定 — Rokuyō determined by Moon's mansion
- **宿曜道方盤 / Sukkayodo Chart**：4×7 網格，二十八宿沿圓環排列 — 4×7 grid with 28 mansions in circular arrangement
- **象徵符號 / Symbols**：每宿有獨特漢字符號（馬、彡、卍、兔、蚯…）— Unique kanji symbols for each mansion

---

### 🐘 泰國占星（Thai Astrology）

以印度 Jyotish 為基礎，融合泰國佛教文化與本土占星傳統。

*Based on Indian Jyotish, blended with Thai Buddhist culture and local astrological traditions.*

- **九曜 / Nine Planets**：與印度 Jyotish 相同（太陽至計都）— Same as Vedic Navagraha (Sun to Ketu)
- **十二星座 / 12 Signs**：泰語命名的恆星黃道星座 — Sidereal zodiac signs with Thai names
- **日主星 / Day Lord**：根據出生星期判定守護星（星期日=太陽，星期一=月亮…）— Ruling planet based on birth weekday
- **泰式方盤 / Thai Chart**：泰語標示的占星盤面 — Thai-labeled astrological chart
- **九宮格 / Nine Grid**：泰國傳統九宮格排盤與占卜 — Traditional Thai nine-grid divination
- **พรหมชาติ / Brahma Jati**：根據出生年份（12 生肖）、月份、星期推算命理，含年運輪與符咒改運法 — Fortune reading based on birth year (12 zodiac), month, weekday, with annual fortune wheel and remedies

---

### ✡ 卡巴拉占星（Kabbalah Astrology）

結合猶太神祕主義與占星術，以回歸黃道呈現。

*Combining Jewish mysticism with astrology, presented in the tropical zodiac.*

- **生命之樹 / Tree of Life**：十個質點（Sephiroth）對應不同行星能量 — Ten Sephiroth corresponding to planetary energies
- **二十二希伯來字母 / 22 Hebrew Letters**：對應黃道星座與行星 — Mapped to zodiac signs and planets
- **塔羅對應 / Tarot Correspondence**：每個星座對應一張塔羅大牌 — Each sign corresponds to a Major Arcana card
- **回歸黃道 / Tropical Zodiac**：與西洋占星相同的黃道系統 — Same zodiac system as Western astrology

---

### ☪ 阿拉伯占星（Arabic Astrology）

源自中世紀伊斯蘭黃金時代，融合希臘與波斯天文傳統。

*Originating from the medieval Islamic Golden Age, blending Greek and Persian astronomical traditions.*

- **阿拉伯點 / Arabic Parts (Lots)**：透過上升點與行星經度加減運算，推導幸運點、精神點等敏感度數 — Derived from Ascendant and planetary longitudes (Part of Fortune, Part of Spirit, etc.)
- **日夜盤 / Sect**：根據太陽位置區分日盤與夜盤，影響阿拉伯點公式 — Day/night chart distinction based on Sun's position
- **行星廟旺落陷 / Essential Dignities**：入廟、入旺、落陷、入弱 — Domicile, Exaltation, Detriment, Fall
- **回歸黃道 / Tropical Zodiac**：使用 Placidus 宮位制 — Using Placidus house system

<details>
<summary>📂 五個子分頁 | 5 Sub-tabs</summary>

| 子分頁 | 功能 |
|---|---|
| **阿拉伯盤 Chart** | 阿拉伯點計算、行星尊貴、日夜盤判定 |
| **Picatrix 星體魔法** | 28 月宿瀏覽、月宿查詢、行星時計算、護符推薦（資料來自 Greer & Warnock 2011、Attrell & Porreca 2019） |
| **太陽知識大全 Shams al-Maʻārif** | 行星屬性、星座特質、Riyada 靈性修煉、伊斯蘭祈禱、Wafq 數字方陣 |
| **參考文獻 Reference** | 阿拉伯占星古籍參考資料 |
| **MS164 手稿** | 阿拉伯占星手稿瀏覽器 |
</details>

---

### 🕌 也門占星（Yemeni / Rasulid Astrology）

南阿拉伯半島最古老的占星傳統之一，源自示巴王國，在 13 世紀 Rasulid 王朝時期達到頂峰。

*One of the oldest astrological traditions of the southern Arabian Peninsula, originating from the Kingdom of Saba' and flourishing under the 13th-century Rasulid dynasty.*

- **28 月宿 / Manazil al-Qamar**：月宿護符魔法 (Talismanic Magic)、醫療與農業擇時 — Lunar mansion talismanic magic, medical and agricultural timing
- **Anwāʼ 天氣預兆**：天氣星宿預兆系統 — Weather omen system based on star risings
- **附庸星 / Affiliated Planets**：也門本土的附庸星（Subsidiary Planets）傳統 — Local subsidiary planetary tradition
- **阿拉伯點 / Arabic Parts**：幸運點、精神點等計算 — Part of Fortune, Part of Spirit, etc.
- **Firdaria 週期**：行星主運週期系統 — Planetary period system
- **核心文獻 / Key Text**：al-Malik al-Ashraf《Kitāb al-Tabṣira fī ʿIlm al-Nujūm》（星學洞見之書）

<details>
<summary>📂 三個子分頁 | 3 Sub-tabs</summary>

| 子分頁 | 功能 |
|---|---|
| **曼荼羅 Mandala** | 也門月宿曼荼羅 SVG 視覺化 |
| **本命盤 Natal** | 行星位置、月宿分析、阿拉伯點 |
| **預兆 Omens** | Anwāʼ 天氣預兆解讀 |
</details>

---

### 🏺 瑪雅占星（Maya Astrology）

源自瓜地馬拉瑪雅文明的天文與曆法傳統。

*Rooted in the astronomical and calendar traditions of the Guatemalan Maya civilization.*

- **Long Count（長紀年）**：以 B'ak'tun、Ka'tun、Tu'n、Winal、K'in 計算天數 — Counting days in B'ak'tun, Ka'tun, Tu'n, Winal, K'in
- **Tzolkin（神聖曆）**：260 天循環，13 數字 × 20 神明名 — 260-day sacred calendar, 13 numbers × 20 day signs
- **Haab（民用曆）**：365 天，18 月 × 20 日 + 5 Wayeb 無日 — 365-day civil calendar, 18 months × 20 days + 5 Wayeb days
- **Calendar Round**：Tzolkin × Haab 同步循環，約 52 年一輪 — Synchronized Tzolkin–Haab cycle, approximately 52-year rotation
- **行星疊加 / Planetary Overlay**：結合西方占星行星位置對應 Tzolkin 能量 — Western planetary positions mapped to Tzolkin energies

---

### 🇲🇲 緬甸占星（Mahabote / Myanmar Astrology）

緬甸傳統占星術，Mahabote (မဟာဘုတ်) 意為「大創造」。

*Traditional Myanmar astrology; Mahabote (မဟာဘုတ်) means "Great Creation".*

- **七曜行星 / Seven Planets**：日、月、火、水、木、金、土，對應星期日至星期六 — Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, mapped to Sunday–Saturday
- **羅睺 / Rahu**：星期三傍晚出生者歸羅睺管轄 — Wednesday evening births governed by Rahu
- **八方位 / Eight Directions**：每顆行星對應一個羅盤方位 — Each planet corresponds to a compass direction
- **七宮位 / Seven Houses**：本命、壽命、意識、身體、權勢、死亡、道德 — Birth, Longevity, Consciousness, Body, Power, Death, Morality
- **行星大運 / Atar (Planetary Periods)**：七星循環共 96 年，主宰人生各階段 — Seven-planet cycle totaling 96 years, governing life stages
- **計算公式 / Formula**：Mahabote 值 = (緬甸年 + 星期數) mod 7 — Mahabote value = (Myanmar year + weekday number) mod 7
- **動物守護 / Animal Signs**：每個星期對應守護動物（鳥翼獅、虎、獅、有牙象、鼠、天竺鼠、龍）— Weekday animal signs (Galon, Tiger, Lion, Tusked Elephant, Rat, Guinea Pig, Dragon)

---

### 🏛️ 古埃及十度區間（Decanic Astrology / 36 Decans）

源自古埃及數千年前的天文計時系統，是西洋占星學最古老的分區技法之一。

*Originating from ancient Egypt's astronomical timekeeping system thousands of years ago, one of the oldest division techniques in Western astrology.*

- **36 個 Decans**：黃道 360° 每 10° 劃分為一個 Decan，每個星座含 3 個 Decan — 360° zodiac divided into 36 segments of 10° each, 3 per sign
- **古埃及星神 / Egyptian Star Deities**：每個 Decan 對應一位古埃及神靈（來自棺蓋對角星表、Dendera Zodiac 等文獻）— Each Decan maps to an Egyptian deity (from coffin lid diagonal star tables, Dendera Zodiac, etc.)
- **迦勒底行星統治 / Chaldean Order**：Mars → Sun → Venus → Mercury → Moon → Saturn → Jupiter 循環
- **三重統治 / Triplicity**：根據元素分配行星統治權 — Planetary rulership by elemental triplicity
- **塔羅小阿卡納 / Minor Arcana**：Golden Dawn 傳統，36 Decans 對應塔羅牌 2–10 號 — Golden Dawn tradition, 36 Decans mapped to Tarot cards 2–10
- **本質尊貴 / Essential Dignities**：Face/Decan 尊貴計分（+1 分），含完整廟旺落陷摘要 — Face/Decan dignity scoring (+1), with full dignity summary
- **Plotly 輪盤圖 / Wheel Chart**：視覺化 36 Decans 的 Dendera Zodiac 外環 — Interactive Plotly visualization of the Dendera Zodiac outer ring

> 📖 此工具為文化、歷史與占星學習用途。古埃及 Decans 起源於數千年前的天文計時系統，現代解讀僅供參考。
>
> *This tool is for cultural, historical, and astrological learning purposes. Ancient Egyptian Decans originated from an astronomical timekeeping system thousands of years ago; modern interpretations are for reference only.*

---

### 🔱 納迪占星（Nadi Jyotish）

源自南印度泰米爾那德邦的古代棕櫚葉手稿傳統，以三種「納迪脈輪」為核心。

*Originating from the ancient palm-leaf manuscript tradition of Tamil Nadu, South India, centered on three Nadi pulse types.*

- **三大納迪脈輪 / Three Nadi Types**：
  - Aadi Nadi（初脈 / 風型 Vata）：神經系統、思維活動、風元素 — Nervous system, mental activity, air element
  - Madhya Nadi（中脈 / 火型 Pitta）：消化代謝、熱情意志、火元素 — Digestion, willpower, fire element
  - Antya Nadi（末脈 / 水型 Kapha）：體液免疫、穩定耐力、水土元素 — Immunity, endurance, water/earth elements
- **27 星宿 Nakshatra**：依次歸屬三大脈輪，每 9 宿為一輪 — 27 lunar mansions cyclically assigned to three Nadis, 9 per cycle
- **納迪宮分 / Nadi Amsha**：每宮 30° 分成 150 個小分，每小分 12' — Each sign divided into 150 sub-divisions of 12' each
- **命主納迪 / Janma Nadi**：以出生月亮所在星宿決定 — Determined by the Moon's Nakshatra at birth
- **上升納迪 / Lagna Nadi**：以上升點所在星宿決定 — Determined by the Ascendant's Nakshatra
- **恆星黃道 / Sidereal Zodiac**：使用 Lahiri Ayanamsa 計算 — Calculated with Lahiri Ayanamsa

---

### 🕉️ Jaimini 占星（Jaimini Astrology）

源自古印度聖人 Jaimini 所著之《Jaimini Sutras》（約公元前 2 世紀），與 Parashara 體系並列為 Jyotish 兩大核心流派。

*Based on the «Jaimini Sutras» (~2nd century BCE), one of the two core schools of Jyotish alongside the Parashara system.*

- **Chara Karaka（可變徵象星）**：以行星在星座內的實際度數動態分配 7 種角色（Atmakaraka、Amatyakaraka 等）— Dynamic role assignment based on actual planetary degrees
- **Rashi Drishti（星座視線）**：以整個星座之間的相互視線取代 Graha Drishti — Whole-sign aspects replacing planetary aspects
- **Argala（介入）與 Virodhargala（阻擋）**：分析某宮位對另一宮位的干預效果 — Analyzing intervention effects between houses
- **Arudha Pada（虛象宮）**：反映外在世界對命主的感知 — Reflecting external world's perception of the native
- **Chara Dasha（可變大運）**：以星座為單位的大運系統 — Sign-based planetary period system
- **Sthira Karaka（固定徵象星）**：每顆行星永遠代表固定主題 — Fixed planetary significators

<details>
<summary>📂 兩個子分頁 | 2 Sub-tabs</summary>

| 子分頁 | 功能 |
|---|---|
| **Jaimini Chart** | Chara Karaka 排列、Rashi Drishti、Argala、Arudha Pada |
| **Chara Dasha** | 可變大運週期推算 |
</details>

---

### 🇲🇳 蒙古祖爾海（Mongolian Zurkhai）

蒙古傳統占星術 (Зурхай / Shar Zurkhai)，源自藏傳佛教曆算體系。

*Traditional Mongolian astrology (Зурхай / Shar Zurkhai), derived from the Tibetan Buddhist calendar system.*

- **12 生肖 / 12 Animal Signs**：鼠、牛、虎、兔、龍、蛇、馬、羊、猴、雞、狗、豬 — Rat, Ox, Tiger, Rabbit, Dragon, Snake, Horse, Sheep, Monkey, Rooster, Dog, Pig
- **五行 / Five Elements**：木、火、土、金、水，各分陰陽 — Wood, Fire, Earth, Metal, Water, each with yin and yang
- **60 年循環 / 60-Year Cycle**：12 生肖 × 5 元素 — 12 animals × 5 elements
- **擇吉 / Auspicious Timing**：結婚、出行、建屋、醫療等吉凶計算 — Marriage, travel, construction, medical treatment timing
- **障礙年 / Obstacle Years**：特定年齡對應的災厄年份 — Specific ages corresponding to calamity years
- **元素相生相剋 / Elemental Cycles**：木→火→土→金→水→木（相生）；木→土→水→火→金→木（相剋）— Generation: Wood→Fire→Earth→Metal→Water→Wood; Destruction: Wood→Earth→Water→Fire→Metal→Wood

> 📖 此計算依循蒙古傳統祖爾海古法，僅供文化學習與參考，重要決定請諮詢合格的蒙古占星師 (Zurkhaič) 或喇嘛。
>
> *Calculations follow traditional Mongolian Zurkhai methods for cultural learning and reference only. For important decisions, consult a qualified Mongolian astrologer (Zurkhaič) or Lama.*

---

### 🏔️ 藏傳時輪金剛占星（Tibetan Kalachakra Astrology）

時輪金剛續 (Kalachakra Tantra) 為藏傳占星的根本古法，融合印度天文學、中國干支體系與苯教本土元素。

*Based on the Kalachakra Tantra, the fundamental text of Tibetan astrology, blending Indian astronomy, Chinese stem-branch system, and indigenous Bön elements.*

- **藏曆 / Lunisolar Calendar (lo-tho)**：陰陽合曆，以六十年循環 (rab-byung) 為週期 — Lunisolar calendar with 60-year cycles
- **九宮 Mewa (sMe-ba dgu)**：1–9 九個數字，對應顏色、方位、吉凶 — 9 numbers mapped to colors, directions, and fortune
- **八卦 Parkha (sPar-kha brgyad)**：八方位，類似易經八卦 — Eight directions, similar to I Ching trigrams
- **五力 / Five Forces**：La（魂）、Sok（命）、Lu（身體）、Wangthang（權勢）、Lungta（風馬）— Soul, Life, Body, Power, Wind Horse
- **五行 (ḥByung-ba)**：木 (Shing)、火 (Me)、土 (Sa)、金 (Lcags)、水 (Chu) — Wood, Fire, Earth, Metal, Water
- **十二生肖 (lo-rtags)**：鼠 (Byi-ba) 至豬 (Phag)，搭配五行組成六十年循環 — 12 animals × 5 elements = 60-year cycle
- **時輪金剛曼荼羅 / Kalachakra Mandala**：SVG 視覺化的時輪金剛壇城 — Interactive SVG Kalachakra Mandala visualization

<details>
<summary>📂 五個子分頁 | 5 Sub-tabs</summary>

| 子分頁 | 功能 |
|---|---|
| **曼荼羅 Mandala** | 時輪金剛曼荼羅 SVG 視覺化 |
| **本命盤 Natal** | 行星位置、藏曆年月、生肖五行 |
| **Mewa 九宮** | 出生 Mewa 數字、顏色、方位 |
| **五力 Forces** | La・Sok・Lu・Wangthang・Lungta 分析 |
| **九曜 Planets** | 七星 + Rahu + Ketu 的藏傳解讀 |
</details>

> 📖 此計算依循藏傳占星古法，僅供文化學習與參考。重要決定請諮詢合格的藏傳占星師 (rTsis-pa) 或上師。
>
> *Calculations follow traditional Tibetan astrological methods for cultural learning and reference only. For important decisions, consult a qualified Tibetan astrologer (rTsis-pa) or Lama.*

---

### 🏺 希臘占星（Hellenistic Astrology）

古希臘羅馬時期的占星體系，是西洋占星的源頭，以整宮制（Whole-sign Houses）與希臘點為核心。

*The astrology of the Greco-Roman era — the root of modern Western astrology, centered on Whole-sign Houses and Greek Lots.*

- **希臘點 / Greek Lots (Kleros)**：Fortune、Spirit、Eros、Necessity、Courage、Victory、Nemesis — 七大希臘點計算
- **Egyptian Bounds / Terms**：古代行星界（Bounds）尊貴體系 — Ancient planetary boundaries dignity system
- **年限推進 / Annual Profections**：每年宮位前進一個星座，決定年度時間主（Time Lord）
- **黃道釋放 / Zodiacal Releasing (L1)**：以 Fortune Lot 為起點的主限週期推算 — Major period calculation from Lot of Fortune
- **行星狀態評分 / Planetary Condition**：綜合尊貴、Sect、相位的行星狀態評分 — Composite scoring of dignity, sect, and aspects
- **Sect 分析 / Sect Analysis**：日盤與夜盤的行星派別判定 — Diurnal/nocturnal sect classification
- **希臘方盤 / Greek Horoscope (θέμα)**：仿古方盤（Whole-sign houses, ASC 左、MC 上）— Square chart after L 497

<details>
<summary>📂 六個子分頁 | 6 Sub-tabs</summary>

| 子分頁 | 功能 |
|---|---|
| **Greek Chart θέμα** | SVG 方盤視覺化，仿古希臘碑文格式 |
| **Natal Analysis** | 行星狀態、Sect、尊貴摘要 |
| **Profections** | 年齡、推進星座、年度 Time Lord |
| **Zodiacal Releasing** | L1 主限週期表（各星座與統治星） |
| **Greek Lots** | 七大希臘點的星座、度數、宮位、含義 |
| **百論 Centiloquy** | 托勒密百條占星格言 (Ptolemy's Centiloquy) |
</details>

---

### 🐦‍⬛ 萬化仙禽（WanHua XianQin / Star-Animal Divination）

源自明代古籍《新刻劉伯溫萬化仙禽》（朱國祥著）的演禽術，以二十八宿禽星為核心的中國傳統命理系統。

*Star-Animal Divination system based on the Ming Dynasty classical text «新刻劉伯溫萬化仙禽» by Zhu Guoxiang, centered on the 28 Lunar Mansion Animal Stars.*

- **二十八宿禽星 / 28 Mansion Animal Stars**：角木蛟、亢金龍、氐土貉、房日兔 …… 每宿配一禽獸與五行 — Each mansion paired with an animal and Five-Element attribute
- **三元起宿 / Three Cycles Starting Mansion**：上元・中元・下元六甲旬起頭宿推算 — Deriving the starting mansion from the Three Cycles (Upper, Middle, Lower)
- **十二宮 / Twelve Palaces**：命宮、財帛、兄弟、田宅、子女、奴僕、夫妻、疾厄、遷移、官祿、福德、相貌 — Life, Wealth, Siblings, Property, Children, Servants, Spouse, Illness, Travel, Career, Fortune, Appearance
- **推命星・身星 / Life Star & Body Star**：從農曆生辰推算命宮星與身宮星 — Deriving Life Star and Body Star from lunar birth data
- **吞啗・合戰 / Swallow-Bite & Alliance-Battle**：禽星之間的生剋吞噬與合戰判斷 — Inter-star relationships of dominance, alliance, and conflict
- **情性賦 / Personality Verse**：依命星五行特質的性情描述 — Character description based on the Life Star's elemental nature
- **格局判斷 / Pattern Evaluation**：得時得地的吉凶格局評定 — Auspicious/inauspicious pattern assessment based on timing and position

<details>
<summary>📂 三個子分頁 | 3 Sub-tabs</summary>

| 子分頁 | 功能 |
|---|---|
| **起盤結果** | 十二宮禽星排布、命星身星、衍生星、吞啗合戰分析、情性賦、格局判斷 |
| **相胎賦** | 命星與胎星的 28 組配合論斷（形品、喜忌、斷曰） |
| **貴賤格** | 貴格（吉利格局）與賤格（凶煞格局）參考表 |
</details>

---

### 🦅 阿茲特克占星（Aztec Astrology）

源自中美洲阿茲特克文明的天文與曆法傳統，與瑪雅體系有密切淵源。

*Rooted in the astronomical and calendar traditions of the Aztec civilization of Mesoamerica, closely related to the Maya system.*

- **Tonalpohualli（神聖曆）**：260 天循環，13 數字 × 20 日徵（day signs），使用 Nahuatl（納瓦特爾語）命名 — 260-day sacred calendar, 13 numbers × 20 day signs in Nahuatl
- **二十日徵 / 20 Day Signs**：Cipactli（鱷魚）、Ehēcatl（風）、Calli（房屋）等，每個對應守護神祇 — Cipactli (Crocodile), Ehēcatl (Wind), Calli (House), etc., each with patron deity
- **Trecena**：13 天為一個週期，每個 Trecena 由第一天的日徵命名 — 13-day period named after its first day sign
- **方位與顏色 / Direction & Color**：每個日徵對應特定的羅盤方位與顏色 — Each day sign maps to a compass direction and color
- **行星疊加 / Planetary Overlay**：結合西方占星行星位置對應 Tonalpohualli 能量 — Western planetary positions mapped to Tonalpohualli energies

---

### 🏛️ 古巴比倫占星（Babylonian / Chaldean Astrology）

所有西洋占星體系的直接源頭，起源於美索不達米亞文明。

*The direct ancestor of all Western astrology systems, originating from Mesopotamian civilization.*

- **MUL.APIN 星表**：約公元前 1000 年的天文目錄泥板，記錄 66 顆恆星/星座的升沒時間 — Astronomical catalog tablet (~1000 BCE) recording rising/setting times of 66 stars/constellations
- **12 宮黃道 / 12 Zodiac Signs**：使用 Akkadian（阿卡德語）古名，如 LU.HUN.GA（白羊）、GU4.AN.NA（金牛）— Using Akkadian names: LU.HUN.GA (Aries), GU4.AN.NA (Taurus), etc.
- **七大行星神 / Seven Planetary Deities**：Shamash（太陽）、Sin（月）、Nabu（水星）、Ishtar（金星）、Nergal（火星）、Marduk（木星）、Ninurta（土星）
- **K.8538 星盤 / Planisphere**：SVG 視覺化的尼尼微古星盤（8 楔形區間） — SVG visualization of the Nineveh planisphere (8 wedge sectors)
- **Enūma Anu Enlil**：美索不達米亞天文預兆集，將天體現象與吉凶對應 — Mesopotamian omen compendium linking celestial phenomena to fortune

<details>
<summary>📂 三個子分頁 | 3 Sub-tabs</summary>

| 子分頁 | 功能 |
|---|---|
| **星盤 Planisphere** | K.8538 尼尼微星盤 SVG 視覺化 |
| **星座盤 Natal** | 行星位置、MUL.APIN 黃道宮位 |
| **預兆 Omens** | Enūma Anu Enlil 天文預兆解讀 |
</details>

---

## 🚀 快速開始 | Quick Start

```bash
# 1. 複製儲存庫 / Clone the repository
git clone https://github.com/kentang2017/kinastro.git
cd kinastro

# 2. 安裝相依套件 / Install dependencies
pip install -r requirements.txt

# 3. 啟動 Streamlit 前端 / Start the Streamlit frontend
streamlit run app.py

# 4.（可選）啟動 FastAPI 後端 / (Optional) Start the FastAPI backend
uvicorn api_server:app --reload
```

> **需求 / Requirements**：Python 3.9+

---

## 🔌 API 後端 | API Backend

堅占星提供獨立的 FastAPI 後端 (`api_server.py`)，將天文計算與 Streamlit UI 分離，支援程式化呼叫。

*Kin Astro provides a standalone FastAPI backend (`api_server.py`) that separates astronomical computation from the Streamlit UI, enabling programmatic access.*

```bash
# 啟動 API 伺服器 / Start the API server
uvicorn api_server:app --reload

# 瀏覽互動式文件 / Browse interactive docs
# http://127.0.0.1:8000/docs
```

**支援的 API 端點 | Available Endpoints:**

| 端點 Endpoint | 體系 System |
|---|---|
| `POST /api/chinese` | 七政四餘 Chinese |
| `POST /api/ziwei` | 紫微斗數 Zi Wei |
| `POST /api/western` | 西洋占星 Western |
| `POST /api/vedic` | 印度占星 Vedic |
| `POST /api/thai` | 泰國占星 Thai |
| `POST /api/kabbalistic` | 卡巴拉 Kabbalah |
| `POST /api/arabic` | 阿拉伯 Arabic |
| `POST /api/maya` | 瑪雅 Maya |
| `POST /api/mahabote` | 緬甸 Myanmar |
| `POST /api/decans` | 古埃及 Decans |
| `POST /api/nadi` | 納迪 Nadi |
| `POST /api/zurkhai` | 祖爾海 Zurkhai |
| `POST /api/hellenistic` | 希臘 Hellenistic |
| `POST /api/compute` | 全體系一次計算 All systems at once |
| `GET /api/health` | 健康檢查 Health check |
| `GET /api/systems` | 列出所有體系 List all systems |

> 所有端點接受出生參數（年、月、日、時、分、時區、經緯度），回傳 JSON 格式的排盤結果。
>
> *All endpoints accept birth parameters (year, month, day, hour, minute, timezone, lat/long) and return JSON chart data.*

---

## 📁 專案結構 | Project Structure

```
kinastro/
├── app.py                          # Streamlit 主應用程式 / Main Streamlit application
├── api_server.py                   # FastAPI 後端 API / FastAPI backend API
├── frontend/
│   └── custom_theme.py             # 自訂主題模組 / Custom theme module
├── styles/
│   └── custom.css                  # 全域 CSS 樣式 / Global CSS styles
├── astro/
│   ├── i18n.py                     # 中英雙語國際化 / Chinese-English i18n module
│   ├── icons.py                    # 體系圖示與文化色彩 / System icons & colors
│   ├── chart_theme.py              # 統一色彩主題 + 響應式 CSS / Unified theme + mobile CSS
│   ├── chart_renderer_v2.py        # 文化風 SVG 渲染器 / Cultural SVG chart wrapper
│   ├── ai_analysis.py              # Cerebras AI 智慧分析 / AI analysis integration
│   ├── interpretations.py          # 文字解讀引擎 / Text interpretation engine
│   ├── interpretations_base.py     # 解讀引擎基類 / Interpretation engine base
│   ├── natal_summary.py            # 命盤摘要生成 / Natal summary generator
│   ├── export.py                   # TXT/CSV/PDF 匯出 / Chart export
│   ├── cross_compare.py            # 跨體系比較 / Cross-system comparison
│   ├── world_map.py                # 互動世界地圖 / Interactive SVG world map
│   ├── swe_init.py                 # Swiss Ephemeris 初始化 / Swiss Ephemeris init
│   │
│   │  ── 七政四餘（Chinese Traditional） ──
│   ├── qizheng/
│   │   ├── calculator.py           # 核心計算引擎 / Core calculation engine
│   │   ├── chart_renderer.py       # UI 渲染（含 SVG 環形盤）/ UI renderer
│   │   ├── constants.py            # 常量與參考資料 / Constants & reference data
│   │   ├── shensha.py              # 神煞計算 / Divine Stars
│   │   ├── qizheng_dasha.py        # 年限大運 / Planetary Periods
│   │   ├── qizheng_transit.py      # 流時對盤 / Transit Comparison
│   │   ├── qizheng_electional.py   # 擇日工具 / Electional Tool
│   │   └── zhangguo.py             # 張果星宗 / Zhangguo Star Readings
│   │
│   │  ── 紫微斗數（Zi Wei） ──
│   ├── ziwei.py                    # 紫微斗數排盤 / Zi Wei Dou Shu module
│   ├── cetian_ziwei.py             # 策天十八飛星 / Ce Tian 18 Flying Stars
│   │
│   │  ── 西洋占星（Western） ──
│   ├── western/
│   │   ├── western.py              # 本命盤 / Natal chart
│   │   ├── western_transit.py      # 行星過運 / Transit analysis
│   │   ├── western_return.py       # 太陽回歸 / Solar & Lunar Return
│   │   ├── western_synastry.py     # 合盤比較 / Synastry
│   │   ├── fixed_stars.py          # 恆星合相 / Fixed star conjunctions
│   │   ├── asteroids.py            # 小行星 / Asteroids (Chiron, Ceres…)
│   │   ├── hellenistic.py          # 希臘占星 / Hellenistic astrology
│   │   └── ptolemy_dignities.py    # Ptolemy 尊貴表 / Ptolemy dignities
│   │
│   │  ── 印度占星（Vedic） ──
│   ├── vedic/
│   │   ├── indian.py               # Vedic (Jyotish) 排盤 / Vedic chart
│   │   ├── vedic_dasha.py          # Vimshottari & Yogini 大運 / Dasha cycles
│   │   ├── ashtakavarga.py         # Ashtakavarga 積分 / Ashtakavarga scoring
│   │   ├── vedic_yogas.py          # Yoga 檢測 / Yoga detections
│   │   ├── nadi.py                 # 納迪占星 / Nadi Jyotish
│   │   ├── varga.py                # Shodasa Varga 分盤 / Divisional charts (D1–D60)
│   │   ├── bphs_engine.py          # BPHS 解析引擎 / BPHS engine
│   │   └── bphs_data.py            # BPHS 資料庫 / BPHS structured data
│   ├── jaimini.py                  # Jaimini 占星 / Jaimini astrology
│   │
│   │  ── 阿拉伯占星（Arabic） ──
│   ├── arabic/
│   │   ├── arabic.py               # 阿拉伯占星 / Arabic astrology
│   │   ├── picatrix_data.py        # Picatrix 月宿資料 / Picatrix mansions data
│   │   ├── picatrix_mansions.py    # Picatrix 月宿計算 / Picatrix calculations
│   │   ├── talisman_generator.py   # 護符生成器 / Talisman generator
│   │   ├── shams_maarif.py         # Shams al-Maʻārif 渲染 / Shams rendering
│   │   ├── ms164_browser.py        # MS164 手稿瀏覽 / MS164 manuscript browser
│   │   ├── riyada.py               # Riyada 靈性修煉 / Spiritual exercises
│   │   └── wafq.py                 # Wafq 數字方陣 / Numeric squares
│   │
│   │  ── 古埃及（Egyptian） ──
│   ├── egyptian/
│   │   ├── decans.py               # 古埃及十度區間 / Egyptian Decans
│   │   └── decans_data.py          # Decans 資料庫 / Decans data
│   │
│   │  ── 萬化仙禽（WanHua XianQin） ──
│   ├── chinstar/
│   │   ├── chinstar.py             # 演禽起盤核心 / Core charting engine
│   │   ├── xiangtai_fu.json        # 相胎賦資料 / Birth Combination data
│   │   └── gui_jian_ge.json        # 貴賤格資料 / Noble/Ignoble Patterns data
│   │
│   │  ── 納迪（Nadi）──
│   ├── nadi/
│   │   └── data/                   # 納迪 JSON 資料 / Nadi JSON data
│   │
│   │  ── 其他體系（Other Systems） ──
│   ├── sukkayodo.py                # 宿曜道 / Japanese Sukkayodo
│   ├── thai.py                     # 泰國占星 / Thai astrology
│   ├── brahma_jati.py              # พรหมชาติ 泰國命理 / Thai Brahma Jati
│   ├── kabbalistic.py              # 卡巴拉占星 / Kabbalistic astrology
│   ├── maya.py                     # 瑪雅占星 / Maya astrology
│   ├── aztec.py                    # 阿茲特克占星 / Aztec astrology
│   ├── babylonian.py               # 巴比倫占星 / Babylonian astrology
│   ├── mahabote.py                 # 緬甸占星 / Myanmar (Mahabote)
│   ├── zurkhai.py                  # 蒙古祖爾海 / Mongolian Zurkhai
│   ├── tibetan.py                  # 藏傳時輪金剛 / Tibetan Kalachakra
│   ├── yemeni.py                   # 也門占星 / Yemeni Rasulid astrology
│   │
│   │  ── 古典與參考（Classics & Reference） ──
│   ├── classic/                    # 古典文獻（百論等）/ Classical texts
│   ├── reference/                  # 參考資料 / Reference materials
│   ├── template/                   # 新增體系模板 / New system template
│   └── data/                       # JSON 資料檔 / JSON data files
│
├── tests/
│   ├── test_calculator.py          # 計算模組單元測試 / Calculator unit tests
│   ├── test_new_astrology.py       # 多體系測試 / Multi-system tests
│   ├── test_advanced_features.py   # 進階功能測試 / Advanced feature tests
│   └── test_chinstar.py            # 萬化仙禽測試 / WanHua XianQin tests
├── docs/
│   └── CONTRIBUTING.md             # 貢獻指南 / Contributing guide
├── requirements.txt                # Python 相依套件 / Python dependencies
├── pyproject.toml                  # 專案中繼資料 / Project metadata
├── CHANGELOG.md                    # 變更日誌 / Changelog
├── CONTRIBUTING.md                 # 貢獻指南 / Contributing guide
└── README.md                       # 本說明文件 / This documentation
```

---

## 🛠️ 技術棧 | Tech Stack

| 元件 Component | 技術 Technology |
|---|---|
| 前端框架 Frontend | [Streamlit](https://streamlit.io/) ≥ 1.52 — 互動式 Python Web 框架 |
| 後端框架 Backend | [FastAPI](https://fastapi.tiangolo.com/) ≥ 0.115 — 高效能 Python API 框架；[Uvicorn](https://www.uvicorn.org/) — ASGI 伺服器 |
| 星曆計算 Ephemeris | [pyswisseph](https://github.com/astrorigin/pyswisseph) ≥ 2.10 — 瑞士星曆表 |
| AI 分析 AI Analysis | [Cerebras Cloud SDK](https://cerebras.ai/) — 快速推理 AI 命盤解讀 |
| 視覺化 Visualization | [Plotly](https://plotly.com/) ≥ 6.0 — 互動式圖表；[svgwrite](https://github.com/mozman/svgwrite) — SVG 盤面 |
| PDF 匯出 Export | [fpdf2](https://py-pdf.github.io/fpdf2/) ≥ 2.7 — PDF 生成 |
| 語言 Language | Python 3.9+ |
| 黃道系統 Zodiac | 恆星黃道 (Lahiri) & 回歸黃道 / Sidereal & Tropical |

---

## 🧪 執行測試 | Run Tests

```bash
pip install pytest
python -m pytest tests/
```

---

## 🤝 貢獻 | Contributing

歡迎提交 Issue 或 Pull Request！詳見 [CONTRIBUTING.md](docs/CONTRIBUTING.md)。

*Contributions via Issues and Pull Requests are welcome! See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.*

---

## 📜 授權 | License

本專案採用 [MIT License](LICENSE) 授權。

*This project is licensed under the [MIT License](LICENSE).*
