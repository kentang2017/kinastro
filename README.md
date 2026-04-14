# ⭐ 堅占星 Kin Astro

<!-- Logo / Hero -->
<div align="center">

![Kin Astro](https://img.shields.io/badge/Kin_Astro-堅占星-FF6B6B?style=for-the-badge&logo=star&logoColor=white)
[![Python](https://img.shields.io/badge/Python-3.10+-00D4FF?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.52-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Swiss Ephemeris](https://img.shields.io/badge/Swiss%20Ephemeris-pyswisseph-FF8C00)](https://github.com/astrorigin/pyswisseph)
[![License](https://img.shields.io/badge/License-MIT-8B5CF6)](LICENSE)

**十五體系占星排盤系統 — 中國・紫微斗數・西洋・印度・宿曜道・泰國・卡巴拉・阿拉伯・瑪雅・緬甸・古埃及十度區間・納迪・蒙古祖爾海・希臘・萬化仙禽 + 跨體系比較**

*Multi-System Astrology Platform — Chinese, Zi Wei, Western, Vedic, Japanese, Thai, Kabbalah, Arabic (incl. Picatrix & Shams al-Maʻārif), Maya, Myanmar, Egyptian Decans, Nadi, Mongolian Zurkhai, Hellenistic, WanHua XianQin + Cross-System Comparison*

</div>

---

## 📑 目錄 | Table of Contents

- [✨ 特色亮點 | Highlights](#-特色亮點--highlights)
- [🧭 體系總覽 | Systems at a Glance](#-體系總覽--systems-at-a-glance)
- [🔍 各體系詳細介紹 | System Details](#-各體系詳細介紹--system-details)
- [🚀 快速開始 | Quick Start](#-快速開始--quick-start)
- [📁 專案結構 | Project Structure](#-專案結構--project-structure)
- [🛠️ 技術棧 | Tech Stack](#️-技術棧--tech-stack)
- [🧪 執行測試 | Run Tests](#-執行測試--run-tests)
- [🤝 貢獻 | Contributing](#-貢獻--contributing)
- [📜 授權 | License](#-授權--license)

---

## ✨ 特色亮點 | Highlights

| | 中文 | English |
|---|---|---|
| 🔮 **十五體系合一** | 在同一個介面中切換十五種占星體系＋跨體系比較，無需來回切換工具 | Switch between 15 astrology systems + cross-comparison in one unified interface |
| 🪐 **精密天文計算** | 使用瑞士星曆表 (Swiss Ephemeris) pyswisseph 進行高精度天文計算 | High-precision astronomical calculations powered by Swiss Ephemeris (pyswisseph) |
| 🌏 **全球化支援** | 內建全球多個主要城市，亦支援自訂經緯度即時排盤 | Built-in global city presets with custom latitude/longitude support |
| 🌐 **中英雙語** | 介面支援中文與英文切換 | Full Chinese and English bilingual interface |
| 🎨 **彩色互動介面** | Streamlit 驅動的現代化 Web UI，響應式排盤結果 | Modern interactive Web UI powered by Streamlit |
| 📱 **響應式設計** | 適配桌面與移動設備，隨時隨地查閱星盤 | Responsive design for desktop and mobile devices |
| 💾 **儲存與匯出** | 儲存／載入排盤參數，支援 TXT、CSV、PDF 匯出 | Save/load chart parameters, export to TXT, CSV, PDF |
| 🆓 **開源免費** | MIT 授權，完整原始碼可自由使用與擴展 | Open-source under MIT License, free to use and extend |

---

## 🧭 體系總覽 | Systems at a Glance

| # | 體系 System | 黃道 Zodiac | 子功能 Sub-features |
|:-:|---|---|---|
| 1 | 🀄 七政四餘 Chinese | 恆星 Sidereal | 本命盤・神煞・年限大運・流時對盤・張果星宗・擇日 |
| 2 | 🌟 紫微斗數 Zi Wei | 農曆 Lunar | 十四主星・十二宮位・五行局 |
| 3 | 🌍 西洋占星 Western | 回歸 Tropical | 本命盤・行星過運・太陽回歸・合盤比較・恆星・小行星 |
| 4 | 🙏 印度占星 Vedic | 恆星 Sidereal | 星座盤・大運 Dasha・Ashtakavarga・Yogas |
| 5 | 🈳 宿曜道 Sukkayodo | 恆星 Sidereal | 二十八宿・六曜・方盤 |
| 6 | 🐘 泰國占星 Thai | 恆星 Sidereal | 泰式盤面・九宮格占卜 |
| 7 | ✡ 卡巴拉 Kabbalah | 回歸 Tropical | 生命之樹・希伯來字母・塔羅 |
| 8 | ☪ 阿拉伯 Arabic | 回歸 Tropical | 阿拉伯點・Picatrix 星體魔法・太陽知識大全 |
| 9 | 🏺 瑪雅 Maya | 瑪雅曆 Maya Cal. | Tzolkin・Haab・Long Count |
| 10 | 🇲🇲 緬甸 Mahabote | 星期制 Weekday | 八方位・七宮・行星大運 |
| 11 | 🏛️ 古埃及 Decans | 回歸 Tropical | 36 Decans・塔羅・Dendera 輪盤圖 |
| 12 | 🔱 納迪 Nadi | 恆星 Sidereal | 三大脈輪・27 星宿・納迪宮分 |
| 13 | 🇲🇳 祖爾海 Zurkhai | 藏曆 Tibetan | 12 生肖・五行・擇吉 |
| 14 | 🏺 希臘 Hellenistic | 回歸 Tropical | Greek Lots・Egyptian Bounds・Profections・Zodiacal Releasing |
| 15 | 🐦‍⬛ 萬化仙禽 WanHua XianQin | 農曆 Lunar | 二十八宿禽星・十二宮・吞啗合戰・相胎賦・貴賤格 |
| | 🔀 跨體系比較 Cross-Compare | — | 中／西／印三系行星位置統一對照 |

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
<summary>📂 四個子分頁 | 4 Sub-tabs</summary>

| 子分頁 | 功能 |
|---|---|
| **本命盤 Natal** | 星盤輪圖、恆星合相（25 顆古典恆星）、小行星（Chiron、Ceres、Pallas、Juno、Vesta）、匯出 TXT/CSV/PDF |
| **行星過運 Transit** | 即時過運行星與本命盤的相位分析 |
| **太陽回歸 Solar Return** | Newton-Raphson 精密太陽回歸盤計算 |
| **合盤比較 Synastry** | 雙人交叉相位、和諧分數、元素相容性分析 |
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
<summary>📂 四個子分頁 | 4 Sub-tabs</summary>

| 子分頁 | 功能 |
|---|---|
| **星座盤 Rashi** | 南印度 / 北印度方盤、行星配置 |
| **大運 Dasha** | Vimshottari 120 年大運（含 Antardasha 子期）、Yogini 36 年大運 |
| **Ashtakavarga** | 七行星 Bhinnashtakavarga + Sarvashtakavarga 積分表 |
| **Yogas** | 12 種瑜伽檢測（Gajakesari、Kemdruma、Gandanta、5 Mahapurusha 等） |
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
<summary>📂 三個子分頁 | 3 Sub-tabs</summary>

| 子分頁 | 功能 |
|---|---|
| **阿拉伯盤 Chart** | 阿拉伯點計算、行星尊貴、日夜盤判定 |
| **Picatrix 星體魔法** | 28 月宿瀏覽、月宿查詢、行星時計算、護符推薦（資料來自 Greer & Warnock 2011、Attrell & Porreca 2019） |
| **太陽知識大全 Shams al-Maʻārif** | 行星屬性、星座特質、Riyada 靈性修煉、伊斯蘭祈禱、Wafq 數字方陣 |
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
<summary>📂 五個子分頁 | 5 Sub-tabs</summary>

| 子分頁 | 功能 |
|---|---|
| **Greek Chart θέμα** | SVG 方盤視覺化，仿古希臘碑文格式 |
| **Natal Analysis** | 行星狀態、Sect、尊貴摘要 |
| **Profections** | 年齡、推進星座、年度 Time Lord |
| **Zodiacal Releasing** | L1 主限週期表（各星座與統治星） |
| **Greek Lots** | 七大希臘點的星座、度數、宮位、含義 |
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
<summary>📂 四個子分頁 | 4 Sub-tabs</summary>

| 子分頁 | 功能 |
|---|---|
| **起盤結果** | 十二宮禽星排布、命星身星、衍生星、吞啗合戰分析、情性賦、格局判斷 |
| **古籍全文** | 《新刻劉伯溫萬化仙禽》原文全文閱覽 |
| **相胎賦** | 命星與胎星的 28 組配合論斷（形品、喜忌、斷曰） |
| **貴賤格** | 貴格（吉利格局）與賤格（凶煞格局）參考表 |
</details>

---

### 🔀 跨體系比較 | Cross-System Comparison

將中國七政四餘、西洋占星、印度占星三大系統的行星位置並排比較，一目了然。

*Side-by-side comparison of planetary positions across Chinese, Western, and Vedic astrology systems.*

- **三系行星位置 / Tri-System Planets**：同一星體在恆星黃道 vs 回歸黃道下的經度對照 — Longitude comparison of the same body under sidereal vs tropical zodiac
- **歲差差異 / Ayanamsa Offset**：直觀展示恆星黃道與回歸黃道之間的歲差偏移 — Visual demonstration of ayanamsa offset between zodiac systems

---

## 🚀 快速開始 | Quick Start

```bash
# 1. 複製儲存庫 / Clone the repository
git clone https://github.com/kentang2017/kinastro.git
cd kinastro

# 2. 安裝相依套件 / Install dependencies
pip install -r requirements.txt

# 3. 啟動應用 / Start the application
streamlit run app.py
```

> **需求 / Requirements**：Python 3.10+

---

## 📁 專案結構 | Project Structure

```
kinastro/
├── app.py                          # Streamlit 主應用程式 / Main Streamlit application
├── astro/
│   ├── i18n.py                     # 中英雙語國際化 / Chinese-English i18n module
│   ├── chart_theme.py              # 統一色彩主題 + 響應式 CSS / Unified theme + mobile CSS
│   │
│   │  ── 七政四餘（Chinese Traditional） ──
│   ├── calculator.py               # 核心計算引擎 / Core calculation engine
│   ├── chart_renderer.py           # UI 渲染（含 SVG 環形盤）/ UI renderer
│   ├── constants.py                # 常量與參考資料 / Constants & reference data
│   ├── shensha.py                  # 神煞計算 / Divine Stars
│   ├── qizheng_dasha.py            # 年限大運 / Planetary Periods
│   ├── qizheng_transit.py          # 流時對盤 / Transit Comparison
│   ├── qizheng_electional.py       # 擇日工具 / Electional Tool
│   ├── zhangguo.py                 # 張果星宗 / Zhangguo Star Readings
│   │
│   │  ── 紫微斗數（Zi Wei） ──
│   ├── ziwei.py                    # 紫微斗數排盤 / Zi Wei Dou Shu module
│   │
│   │  ── 西洋占星（Western） ──
│   ├── western.py                  # 本命盤 / Natal chart
│   ├── western_transit.py          # 行星過運 / Transit analysis
│   ├── western_return.py           # 太陽回歸 / Solar & Lunar Return
│   ├── western_synastry.py         # 合盤比較 / Synastry
│   ├── fixed_stars.py              # 恆星合相 / Fixed star conjunctions
│   ├── asteroids.py                # 小行星 / Asteroids (Chiron, Ceres…)
│   │
│   │  ── 印度占星（Vedic） ──
│   ├── indian.py                   # Vedic (Jyotish) 排盤 / Vedic chart
│   ├── vedic_dasha.py              # Vimshottari & Yogini 大運 / Dasha cycles
│   ├── ashtakavarga.py             # Ashtakavarga 積分 / Ashtakavarga scoring
│   ├── vedic_yogas.py              # Yoga 檢測 / Yoga detections
│   │
│   │  ── 其他體系（Other Systems） ──
│   ├── sukkayodo.py                # 宿曜道 / Japanese Sukkayodo
│   ├── thai.py                     # 泰國占星 / Thai astrology
│   ├── kabbalistic.py              # 卡巴拉占星 / Kabbalistic astrology
│   ├── arabic.py                   # 阿拉伯占星 / Arabic astrology
│   ├── maya.py                     # 瑪雅占星 / Maya astrology
│   ├── mahabote.py                 # 緬甸占星 / Myanmar (Mahabote)
│   ├── decans.py                   # 古埃及十度區間 / Egyptian Decans
│   ├── decans_data.py              # Decans 資料庫 / Decans data
│   ├── nadi.py                     # 納迪占星 / Nadi Jyotish
│   ├── zurkhai.py                  # 蒙古祖爾海 / Mongolian Zurkhai
│   ├── hellenistic.py              # 希臘占星 / Hellenistic astrology
│   │
│   │  ── 萬化仙禽（WanHua XianQin） ──
│   ├── chinstar/                   # 萬化仙禽模組 / Star-Animal Divination module
│   │   ├── chinstar.py             # 演禽起盤核心 / Core charting engine
│   │   ├── 新刻刘伯温万化仙禽.txt   # 古籍全文 / Classical text
│   │   ├── xiangtai_fu.json        # 相胎賦資料 / Birth Combination data
│   │   └── gui_jian_ge.json        # 貴賤格資料 / Noble/Ignoble Patterns data
│   │
│   │  ── 阿拉伯子模組（Arabic Sub-modules） ──
│   ├── picatrix_data.py            # Picatrix 28 月宿資料 / Picatrix mansions data
│   ├── picatrix_mansions.py        # Picatrix 月宿計算 / Picatrix calculations
│   ├── talisman_generator.py       # 護符生成器 / Talisman generator
│   ├── shams_maarif.py             # Shams al-Maʻārif 渲染 / Shams rendering
│   ├── arabic_planetaries.py       # 行星屬性 / Planetary properties
│   ├── arabic_zodiacsigns.py       # 星座屬性 / Zodiac sign properties
│   ├── arabic_spells.py            # 伊斯蘭祈禱 / Islamic Duas
│   ├── riyada.py                   # Riyada 靈性修煉 / Spiritual exercises
│   ├── wafq.py                     # Wafq 數字方陣 / Numeric squares
│   │
│   │  ── 共用模組（Shared Modules） ──
│   ├── cross_compare.py            # 跨體系比較 / Cross-system comparison
│   ├── ptolemy_dignities.py        # Ptolemy 尊貴表 / Ptolemy dignities
│   ├── export.py                   # TXT/CSV/PDF 匯出 / Chart export
│   ├── session_store.py            # 排盤儲存管理 / Chart save/load
│   └── data/                       # JSON 資料檔 / JSON data files
│
├── tests/
│   ├── test_calculator.py          # 計算模組單元測試 / Calculator unit tests
│   ├── test_new_astrology.py       # 多體系測試 / Multi-system tests
│   └── test_advanced_features.py   # 進階功能測試 / Advanced feature tests
├── docs/
│   └── CONTRIBUTING.md             # 貢獻指南 / Contributing guide
├── requirements.txt                # Python 相依套件 / Python dependencies
├── pyproject.toml                  # 專案中繼資料 / Project metadata
├── CHANGELOG.md                    # 變更日誌 / Changelog
├── README.md                       # 本說明文件 / This documentation
└── LICENSE                         # MIT 授權 / MIT License
```

---

## 🛠️ 技術棧 | Tech Stack

| 元件 Component | 技術 Technology |
|---|---|
| 前端框架 Frontend | [Streamlit](https://streamlit.io/) ≥ 1.52 — 互動式 Python Web 框架 |
| 星曆計算 Ephemeris | [pyswisseph](https://github.com/astrorigin/pyswisseph) ≥ 2.10 — 瑞士星曆表 |
| 視覺化 Visualization | [Plotly](https://plotly.com/) ≥ 6.0 — 互動式圖表；[svgwrite](https://github.com/mozman/svgwrite) — SVG 盤面 |
| PDF 匯出 Export | [fpdf2](https://py-pdf.github.io/fpdf2/) ≥ 2.7 — PDF 生成 |
| 語言 Language | Python 3.10+ |
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
