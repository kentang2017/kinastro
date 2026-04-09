"""
i18n.py — Internationalisation strings for Kin Astro
Supports: 繁體中文 (zh-TW) and English (en)
"""

TRANSLATIONS = {
    # ── App title / subtitle ────────────────────────────────────────────────
    "app_title": {
        "zh": "⭐ 堅占星 Kin Astro",
        "en": "⭐ Kin Astro",
    },
    "app_subtitle": {
        "zh": (
            "多體系占星排盤系統 — "
            "支援七政四餘（中國）、紫微斗數、西洋占星、印度占星（Jyotish）、宿曜道、泰國占星、"
            "卡巴拉占星、阿拉伯占星、瑪雅占星、緬甸占星（Mahabote）、古埃及十度區間（Decans）、"
            "納迪占星（Nadi Jyotish）、蒙古祖爾海（Zurkhai）、Picatrix 星體魔法。"
        ),
        "en": (
            "Multi-System Astrology — "
            "Chinese (Seven Governors), Zi Wei Dou Shu, Western, Indian (Jyotish), "
            "Sukkayodo, Thai, Kabbalistic, Arabic, Maya, Myanmar (Mahabote), "
            "Egyptian Decans, Nadi Jyotish, Mongolian Zurkhai, Picatrix Stellar Magic."
        ),
    },
    # ── Sidebar ─────────────────────────────────────────────────────────────
    "sidebar_header": {
        "zh": "📝 排盤資料",
        "en": "📝 Chart Data",
    },
    "date_time": {
        "zh": "日期與時間",
        "en": "Date & Time",
    },
    "birth_date": {
        "zh": "出生日期",
        "en": "Birth Date",
    },
    "birth_time": {
        "zh": "出生時間",
        "en": "Birth Time",
    },
    "birth_location": {
        "zh": "出生地點",
        "en": "Birth Location",
    },
    "city_preset": {
        "zh": "預設城市",
        "en": "City Preset",
    },
    "latitude": {
        "zh": "緯度",
        "en": "Latitude",
    },
    "longitude": {
        "zh": "經度",
        "en": "Longitude",
    },
    "timezone": {
        "zh": "時區 (UTC)",
        "en": "Timezone (UTC)",
    },
    "custom": {
        "zh": "自訂",
        "en": "Custom",
    },
    "custom_location": {
        "zh": "自訂地點",
        "en": "Custom Location",
    },
    "calculate_btn": {
        "zh": "🔮 開始排盤",
        "en": "🔮 Calculate Chart",
    },
    "gender_header": {
        "zh": "性別",
        "en": "Gender",
    },
    "gender_label": {
        "zh": "性別（影響七政四餘宮位排列方向）",
        "en": "Gender (affects house direction for Chinese Astrology)",
    },
    "male": {
        "zh": "男命",
        "en": "Male",
    },
    "female": {
        "zh": "女命",
        "en": "Female",
    },
    # ── City names ───────────────────────────────────────────────────────────
    "city_beijing": {"zh": "北京", "en": "Beijing"},
    "city_shanghai": {"zh": "上海", "en": "Shanghai"},
    "city_hongkong": {"zh": "香港", "en": "Hong Kong"},
    "city_taipei": {"zh": "台北", "en": "Taipei"},
    "city_tokyo": {"zh": "東京", "en": "Tokyo"},
    "city_seoul": {"zh": "首爾", "en": "Seoul"},
    "city_singapore": {"zh": "新加坡", "en": "Singapore"},
    "city_london": {"zh": "倫敦", "en": "London"},
    "city_newyork": {"zh": "紐約", "en": "New York"},
    "city_yangon": {"zh": "仰光", "en": "Yangon"},
    "city_ulaanbaatar": {"zh": "烏蘭巴托", "en": "Ulaanbaatar"},
    # ── Tab labels ───────────────────────────────────────────────────────────
    "tab_chinese": {
        "zh": "🀄 七政四餘（中國）",
        "en": "🀄 Seven Governors (Chinese)",
    },
    "tab_ziwei": {
        "zh": "🌟 紫微斗數",
        "en": "🌟 Zi Wei Dou Shu",
    },
    "tab_western": {
        "zh": "🌍 西洋占星",
        "en": "🌍 Western Astrology",
    },
    "tab_indian": {
        "zh": "🙏 印度占星",
        "en": "🙏 Indian Astrology",
    },
    "tab_sukkayodo": {
        "zh": "🈳 宿曜道",
        "en": "🈳 Sukkayodo",
    },
    "tab_thai": {
        "zh": "🐘 泰國占星",
        "en": "🐘 Thai Astrology",
    },
    "tab_kabbalistic": {
        "zh": "✡ 卡巴拉占星",
        "en": "✡ Kabbalistic Astrology",
    },
    "tab_arabic": {
        "zh": "☪ 阿拉伯占星",
        "en": "☪ Arabic Astrology",
    },
    "tab_maya": {
        "zh": "🏺 瑪雅占星",
        "en": "🏺 Maya Astrology",
    },
    "tab_mahabote": {
        "zh": "🇲🇲 緬甸占星",
        "en": "🇲🇲 Myanmar (Mahabote)",
    },
    "tab_decans": {
        "zh": "🏛️ 古埃及十度區間",
        "en": "🏛️ Egyptian Decans",
    },
    "tab_nadi": {
        "zh": "🔱 納迪占星",
        "en": "🔱 Nadi Jyotish",
    },
    "tab_zurkhai": {
        "zh": "🇲🇳 蒙古祖爾海",
        "en": "🇲🇳 Mongolian Zurkhai",
    },
    "tab_picatrix": {
        "zh": "📜 Picatrix 星體魔法",
        "en": "📜 Picatrix Stellar Magic",
    },
    # ── Spinner messages ──────────────────────────────────────────────────────
    "spinner_indian": {
        "zh": "正在計算印度占星排盤...",
        "en": "Calculating Indian astrology chart...",
    },
    "spinner_chinese": {
        "zh": "正在計算七政四餘位置...",
        "en": "Calculating Seven Governors chart...",
    },
    "spinner_ziwei": {
        "zh": "正在計算紫微斗數命盤...",
        "en": "Calculating Zi Wei Dou Shu chart...",
    },
    "spinner_western": {
        "zh": "正在計算西洋占星排盤...",
        "en": "Calculating Western astrology chart...",
    },
    "spinner_thai": {
        "zh": "正在計算泰國占星排盤...",
        "en": "Calculating Thai astrology chart...",
    },
    "spinner_kabbalistic": {
        "zh": "正在計算卡巴拉占星排盤...",
        "en": "Calculating Kabbalistic astrology chart...",
    },
    "spinner_arabic": {
        "zh": "正在計算阿拉伯占星排盤...",
        "en": "Calculating Arabic astrology chart...",
    },
    "spinner_maya": {
        "zh": "正在計算瑪雅占星排盤...",
        "en": "Calculating Maya astrology chart...",
    },
    "spinner_mahabote": {
        "zh": "正在計算緬甸 Mahabote 排盤...",
        "en": "Calculating Myanmar Mahabote chart...",
    },
    "spinner_decans": {
        "zh": "正在計算古埃及十度區間排盤...",
        "en": "Calculating Egyptian Decans chart...",
    },
    "spinner_nadi": {
        "zh": "正在計算納迪占星排盤...",
        "en": "Calculating Nadi Jyotish chart...",
    },
    "spinner_zurkhai": {
        "zh": "正在計算蒙古祖爾海排盤...",
        "en": "Calculating Mongolian Zurkhai chart...",
    },
    # ── Sidereal checkbox ──────────────────────────────────────────────────
    "sidereal_label": {
        "zh": "🌟 使用恆星黃道 (Sidereal Zodiac / Lahiri Ayanamsa)",
        "en": "🌟 Use Sidereal Zodiac (Lahiri Ayanamsa)",
    },
    "sidereal_help": {
        "zh": "恆星黃道以實際星座位置計算，含歲差修正（印度占星用同一體系）",
        "en": "Sidereal zodiac calculates with actual star positions including precession correction (same system used in Indian astrology)",
    },
    # ── Sukkayodo subheader & info ────────────────────────────────────────
    "sukkayodo_subheader": {
        "zh": "🈳 日本宿曜道 (Yojōdō)",
        "en": "🈳 Japanese Sukkayodo (Yojōdō)",
    },
    "sukkayodo_info": {
        "zh": "宿曜道建基於印度占星排盤，請至「🙏 印度占星」分頁查看完整印度占星排盤。",
        "en": "Sukkayodo is based on Indian astrology. See the '🙏 Indian Astrology' tab for the full Vedic chart.",
    },
    # ── Thai sub-tab labels ────────────────────────────────────────────────
    "thai_subtab_chart": {
        "zh": "🐘 ผังดวงชาตา (占星排盤)",
        "en": "🐘 ผังดวงชาตา (Astrology Chart)",
    },
    "thai_subtab_nine": {
        "zh": "🔮 ตาราง 9 ช่อง & 九宮占卜 (9宮格數字學 · 九宮占卜)",
        "en": "🔮 9-Palace Grid & Divination (Numerology · Divination)",
    },
    # ── Picatrix section ───────────────────────────────────────────────────
    "picatrix_subheader": {
        "zh": "📜 Picatrix 星體魔法 (Picatrix Stellar Magic)",
        "en": "📜 Picatrix Stellar Magic",
    },
    "picatrix_source": {
        "zh": (
            "資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim) — "
            "Greer & Warnock 2011 translation / Attrell & Porreca 2019"
        ),
        "en": (
            "Source: Picatrix (Ghayat al-Hakim) — "
            "Greer & Warnock 2011 translation / Attrell & Porreca 2019"
        ),
    },
    "picatrix_subtab_mansion": {
        "zh": "🌙 月宿查詢器",
        "en": "🌙 Mansion Lookup",
    },
    "picatrix_subtab_hours": {
        "zh": "⏰ 行星時計算器",
        "en": "⏰ Planetary Hours",
    },
    "picatrix_subtab_talisman": {
        "zh": "🔮 護符生成器",
        "en": "🔮 Talisman Generator",
    },
    "picatrix_subtab_browse": {
        "zh": "📚 Picatrix 參考總覽",
        "en": "📚 Picatrix Reference",
    },
    "picatrix_talisman_subheader": {
        "zh": "🔮 護符生成器（無需排盤）",
        "en": "🔮 Talisman Generator (no chart needed)",
    },
    # ── "Please calculate" info messages ───────────────────────────────────
    "info_calc_prompt": {
        "zh": "👈 請在左側輸入排盤資料，然後點擊「開始排盤」按鈕。",
        "en": "👈 Enter birth data on the left and click 'Calculate Chart'.",
    },
    "info_decans_prompt": {
        "zh": (
            "👈 請在左側輸入排盤資料，然後點擊「開始排盤」按鈕查看個人十度區間排盤。"
            "下方可先瀏覽古埃及 36 Decans 總覽。"
        ),
        "en": (
            "👈 Enter birth data on the left and click 'Calculate Chart' to view your personal Decans chart. "
            "Browse all 36 Egyptian Decans below."
        ),
    },
    "info_picatrix_prompt": {
        "zh": (
            "👈 請在左側輸入排盤資料，然後點擊「開始排盤」按鈕查看個人月宿排盤。"
            "下方可先瀏覽 Picatrix 28 月宿完整參考。"
        ),
        "en": (
            "👈 Enter birth data on the left and click 'Calculate Chart' to view your personal Moon Mansion chart. "
            "Browse all 28 Picatrix Mansions below."
        ),
    },
    # ── Tab description markdown ────────────────────────────────────────────
    "desc_chinese": {
        "zh": """
### 什麼是七政四餘？

**七政四餘**是中國傳統占星術的核心體系：

- **七政（日月五星）**：太陽、太陰（月亮）、水星、金星、火星、木星、土星
- **四餘（虛星）**：羅睺（北交點）、計都（南交點）、月孛（平均遠地點）、紫氣

本系統使用 **pyswisseph**（瑞士星曆表）進行精確的天文計算，
提供星曜的黃經位置、所在星次、二十八宿對應、十二宮位分布等資訊。
""",
        "en": """
### What are the Seven Governors (七政四餘)?

The **Seven Governors and Four Remainders** form the core of traditional Chinese astrology:

- **Seven Governors (Sun, Moon & Five Planets)**: Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn
- **Four Remainders (Virtual Stars)**: Rāhu (North Node), Ketu (South Node), Moon Apogee, Purple Vapour

This system uses **pyswisseph** (Swiss Ephemeris) for precise astronomical calculations,
providing planetary longitudes, lunar mansion correspondences, and twelve-house distributions.
""",
    },
    "desc_ziwei": {
        "zh": """
### 什麼是紫微斗數？

**紫微斗數**是中國傳統命理學最重要的排盤體系之一，相傳由五代末宋初的
**陳希夷**（陳摶）整理創立：

- **十四主星**：紫微（帝王星）、天機、太陽、武曲、天同、廉貞（紫微六系）；
  天府、太陰、貪狼、巨門、天相、天梁、七殺、破軍（天府八系）
- **十二宮位**：命宮、兄弟宮、夫妻宮、子女宮、財帛宮、疾厄宮、
  遷移宮、交友宮、官祿宮、田宅宮、福德宮、父母宮
- **五行局**：由命宮天干決定，分水二、木三、金四、土五、火六局，
  影響紫微星安星方式
- **農曆排盤**：以農曆生辰（年、月、日、時辰）為基礎
""",
        "en": """
### What is Zi Wei Dou Shu (紫微斗數)?

**Zi Wei Dou Shu** is one of the most important Chinese fortune-telling systems,
traditionally attributed to **Chen Xiyi** (Chen Tuan) of the late Five Dynasties / early Song period:

- **14 Major Stars**: Zi Wei (Emperor Star), Tian Ji, Tai Yang, Wu Qu, Tian Tong, Lian Zhen (Zi Wei group);
  Tian Fu, Tai Yin, Tan Lang, Ju Men, Tian Xiang, Tian Liang, Qi Sha, Po Jun (Tian Fu group)
- **12 Palaces**: Life, Siblings, Spouse, Children, Wealth, Health,
  Travel, Friends, Career, Property, Virtue, Parents
- **Five-Element Bureau**: Determined by the Life Palace heavenly stem; Water-2, Wood-3, Gold-4, Earth-5, Fire-6
- **Lunar Calendar**: Based on lunar birth year, month, day, and hour
""",
    },
    "desc_western": {
        "zh": """
### 什麼是西洋占星？

**西洋占星**使用回歸黃道（Tropical Zodiac）計算行星位置：

- **行星**：太陽、月亮、水星、金星、火星、木星、土星、天王星、海王星、冥王星
- **十二星座**：白羊座至雙魚座
- **宮位制**：Placidus 等分宮制
- **相位**：合、沖、刑、三合、六合等
""",
        "en": """
### What is Western Astrology?

**Western Astrology** uses the Tropical Zodiac to calculate planetary positions:

- **Planets**: Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto
- **12 Signs**: Aries through Pisces
- **House System**: Placidus equal house system
- **Aspects**: Conjunction, opposition, square, trine, sextile, etc.
""",
    },
    "desc_indian": {
        "zh": """
### 什麼是印度占星 (Jyotish)？

**印度占星**使用恆星黃道（Sidereal Zodiac）搭配 Lahiri 歲差：

- **九曜 (Navagraha)**：太陽、月亮、火星、水星、木星、金星、土星、羅睺、計都
- **十二星座 (Rashi)**：Mesha 至 Meena
- **二十七宿 (Nakshatra)**：Ashwini 至 Revati，每宿分四足 (Pada)
- **南印度式方盤 (South Indian Chart)**
- **七曜管宿**：每顆曜主管 3 個 Nakshatra，構成 27 宿體系

| 曜 | 主宿 |
|:--:|:-----|
| Sun | Krittika、Uttara Phalguni、Uttara Ashadha |
| Moon | Rohini、Hasta、Shravana |
| Mars | Mrigashira、Chitra、Dhanishta |
| Mercury | Ashlesha、Jyeshtha、Revati |
| Jupiter | Punarvasu、Vishakha、Purva Bhadrapada |
| Venus | Bharani、Purva Phalguni、Purva Ashadha |
| Saturn | Pushya、Anuradha、Uttara Bhadrapada |
| Rahu | Ardra、Swati、Shatabhisha |
| Ketu | Ashwini、Magha、Mula |
""",
        "en": """
### What is Indian Astrology (Jyotish)?

**Jyotish** uses the Sidereal Zodiac with the Lahiri ayanamsa:

- **Nine Planets (Navagraha)**: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu
- **12 Signs (Rashi)**: Mesha through Meena
- **27 Lunar Mansions (Nakshatra)**: Ashwini through Revati, each divided into 4 Padas
- **South Indian Chart** style
- **Planetary Rulerships**: Each planet rules 3 Nakshatras

| Planet | Ruled Nakshatras |
|:------:|:-----------------|
| Sun | Krittika, Uttara Phalguni, Uttara Ashadha |
| Moon | Rohini, Hasta, Shravana |
| Mars | Mrigashira, Chitra, Dhanishta |
| Mercury | Ashlesha, Jyeshtha, Revati |
| Jupiter | Punarvasu, Vishakha, Purva Bhadrapada |
| Venus | Bharani, Purva Phalguni, Purva Ashadha |
| Saturn | Pushya, Anuradha, Uttara Bhadrapada |
| Rahu | Ardra, Swati, Shatabhisha |
| Ketu | Ashwini, Magha, Mula |
""",
    },
    "desc_sukkayodo": {
        "zh": """
### 什麼是宿曜道？

**宿曜道**由空海大師於 9 世紀自印度傳入日本，是融合佛密與道教的占星體系：

- **二十八宿 (Nakshatra)**：比印度 Jyotish 多出 **Abhijit（牛宿）**，共 28 宿
- **六曜 (Rokuyō)**：先勝・友引・先負・仏滅・大安・赤口，由 **Moon 所在宿** 決定
- **宿曜道方盤**：以 Moon 為中心，二十八宿沿圓環排列

宿曜道可用於擇日、占卜日常生活中各類事務的吉凶。
""",
        "en": """
### What is Sukkayodo (宿曜道)?

**Sukkayodo** was brought to Japan from India by Master Kukai in the 9th century,
blending Esoteric Buddhism and Taoist astrology:

- **28 Lunar Mansions (Nakshatra)**: Includes **Abhijit (牛宿)** not found in Indian Jyotish, totalling 28
- **Six Day Cycle (Rokuyō)**: Sensho, Tomobiki, Senbu, Butsumetsu, Taian, Shakko — determined by the Moon's mansion
- **Sukkayodo Wheel Chart**: Moon at centre, 28 mansions arranged in a ring

Sukkayodo is used for date selection and divination of auspiciousness in daily life matters.
""",
    },
    "desc_thai": {
        "zh": """
### 什麼是泰國占星？

**泰國占星**以印度 Jyotish 為基礎，融合泰國傳統文化：

- **九曜**：太陽、月亮、火星、水星、木星、金星、土星、羅睺、計都
- **十二星座 (ราศี)**：使用泰語命名的恆星黃道星座
- **日主星 (ดาวประจำวัน)**：根據出生星期判定守護星
- **泰式方盤 (ผังดวงชาตา)**
""",
        "en": """
### What is Thai Astrology?

**Thai Astrology** is based on Indian Jyotish, blended with Thai traditional culture:

- **Nine Planets**: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu
- **12 Signs (ราศี)**: Sidereal zodiac signs named in Thai
- **Day Ruler (ดาวประจำวัน)**: Guardian planet determined by day of birth
- **Thai Chart (ผังดวงชาตา)**
""",
    },
    "desc_kabbalistic": {
        "zh": """
### 什麼是卡巴拉占星？

**卡巴拉占星**結合猶太神祕主義（Kabbalah）與占星術：

- **生命之樹 (Tree of Life)**：十個質點（Sephiroth）對應不同行星
- **希伯來字母**：22 個字母分別對應黃道星座與行星
- **塔羅對應**：每個星座對應一張塔羅大牌
- **回歸黃道 (Tropical Zodiac)**：使用西洋占星的回歸黃道系統
""",
        "en": """
### What is Kabbalistic Astrology?

**Kabbalistic Astrology** combines Jewish mysticism (Kabbalah) with astrology:

- **Tree of Life**: Ten Sephiroth corresponding to different planets
- **Hebrew Letters**: 22 letters corresponding to zodiac signs and planets
- **Tarot Correspondences**: Each sign corresponds to a Major Arcana card
- **Tropical Zodiac**: Uses the Western tropical zodiac system
""",
    },
    "desc_arabic": {
        "zh": """
### 什麼是阿拉伯占星？

**阿拉伯占星**源自中世紀伊斯蘭黃金時代，融合希臘與波斯天文傳統：

- **阿拉伯點 (Arabic Parts / Lots)**：透過上升點與行星經度加減運算，
  推導出幸運點、精神點、愛情點等各生活主題的敏感度數
- **日夜盤 (Sect)**：根據太陽位置區分日盤與夜盤，影響阿拉伯點公式
- **行星廟旺落陷 (Essential Dignities)**：入廟、入旺、落陷、入弱
- **回歸黃道 (Tropical Zodiac)**：使用 Placidus 宮位制
""",
        "en": """
### What is Arabic Astrology?

**Arabic Astrology** originated in the medieval Islamic Golden Age, blending Greek and Persian astronomical traditions:

- **Arabic Parts (Lots)**: Sensitive points derived by adding/subtracting the Ascendant and planetary longitudes —
  Fortune, Spirit, Love, and other life themes
- **Diurnal/Nocturnal Sect**: Whether Sun is above or below the horizon affects Arabic Part formulas
- **Essential Dignities**: Domicile, Exaltation, Fall, Detriment
- **Tropical Zodiac**: Uses Placidus house system
""",
    },
    "desc_maya": {
        "zh": """
### 什麼是瑪雅占星？

**瑪雅占星**源自瓜地馬拉瑪雅文明的天文與曆法傳統：

- **Long Count（長紀年）**：以 B'ak'tun、Ka'tun、Tu'n、Winal、K'in 計算天數
- **Tzolkin（神聖曆）**：260 天循環，13 數字 × 20 神明名
- **Haab（民用曆）**：365 天，18 月 × 20 日 + 5 Wayeb 無日
- **Calendar Round**：Tzolkin × Haab 同步循環，約 52 年一輪
- **行星疊加**：結合西方占星行星位置對應 Tzolkin 能量
""",
        "en": """
### What is Maya Astrology?

**Maya Astrology** draws from the astronomical and calendrical traditions of Guatemalan Maya civilisation:

- **Long Count**: Days counted in B'ak'tun, Ka'tun, Tu'n, Winal, K'in units
- **Tzolkin (Sacred Calendar)**: 260-day cycle — 13 numbers × 20 day signs
- **Haab (Civil Calendar)**: 365 days — 18 months × 20 days + 5 Wayeb nameless days
- **Calendar Round**: Tzolkin × Haab synchronised cycle, ~52 years per round
- **Planetary Overlay**: Western planetary positions mapped to Tzolkin energies
""",
    },
    "desc_mahabote": {
        "zh": """
### 什麼是緬甸 Mahabote 占星？

**Mahabote** (မဟာဘုတ်) 是緬甸傳統占星術，意為「大創造」：

- **七曜行星**：日、月、火、水、木、金、土，對應星期日至星期六
- **羅睺 (Rahu)**：星期三傍晚出生者歸羅睺管轄
- **八方位**：每顆行星對應一個羅盤方位（東北至北）
- **七宮位**：本命、壽命、意識、身體、權勢、死亡、道德
- **行星大運 (Atar)**：七星循環共 96 年，主宰人生各階段
- **計算公式**：Mahabote 值 = (緬甸年 + 星期數) mod 7
""",
        "en": """
### What is Myanmar Mahabote Astrology?

**Mahabote** (မဟာဘုတ်) is traditional Myanmar astrology, meaning "Great Creation":

- **Seven Planets**: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn — corresponding to Sunday through Saturday
- **Rahu**: Those born Wednesday evening fall under Rahu's rulership
- **Eight Directions**: Each planet corresponds to a compass direction (NE through N)
- **Seven Houses**: Birth, Life, Mind, Body, Power, Death, Morality
- **Planetary Periods (Atar)**: Seven-planet cycle totalling 96 years
- **Calculation**: Mahabote value = (Myanmar year + weekday number) mod 7
""",
    },
    "desc_nadi": {
        "zh": """
### 什麼是納迪占星 (Nadi Jyotish)？

**納迪占星**源自南印度泰米爾那德邦數千年前的古代棕櫚葉手稿（Nadi Granthas）：

- **三大納迪脈輪**：每顆行星依其所在星宿歸屬三種脈輪能量
  - 🌬️ **Aadi Nadi（初脈）**：風型 (Vata)，主神經與思維
  - 🔥 **Madhya Nadi（中脈）**：火型 (Pitta)，主代謝與意志
  - 💧 **Antya Nadi（末脈）**：水型 (Kapha)，主免疫與耐力
- **命主納迪 (Janma Nadi)**：由出生月亮所在星宿決定，影響體質與性格
- **上升納迪 (Lagna Nadi)**：由上升點所在星宿決定，影響外在表現
- **納迪宮分 (Nadi Amsha)**：每宮 30° 分成 150 份（每份 12'），提供最精細分析
- **Nadi Dosha（脈衝衝突）**：婚配雙方若同屬一種納迪，傳統認為需特別注意
""",
        "en": """
### What is Nadi Jyotish?

**Nadi Jyotish** originates from ancient palm-leaf manuscripts (Nadi Granthas) from Tamil Nadu, South India:

- **Three Nadi Channels**: Each planet's Nakshatra belongs to one of three energy channels
  - 🌬️ **Aadi Nadi (First Pulse)**: Vata (Wind) — governs nerves and mind
  - 🔥 **Madhya Nadi (Middle Pulse)**: Pitta (Fire) — governs metabolism and will
  - 💧 **Antya Nadi (Last Pulse)**: Kapha (Water) — governs immunity and endurance
- **Birth Nadi (Janma Nadi)**: Determined by Moon's Nakshatra at birth — affects constitution and character
- **Ascendant Nadi (Lagna Nadi)**: Determined by Ascendant's Nakshatra — affects outer expression
- **Nadi Amsha**: Each 30° house divided into 150 parts (12' each) for the finest analysis
- **Nadi Dosha**: If both partners share the same Nadi, traditional teaching advises special attention
""",
    },
    "desc_zurkhai": {
        "zh": """
### 什麼是蒙古祖爾海 (Zurkhai)？

**祖爾海 (Зурхай / Zurkhai)** 是蒙古傳統占星術，源自藏傳佛教曆算體系：

- **12 生肖**：鼠（Hulgana）、牛（Ükher）、虎（Bar）、兔（Tuulai）、
  龍（Luu）、蛇（Mogoi）、馬（Mori）、羊（Honi）、猴（Bich）、
  雞（Tahia）、狗（Nokhoi）、豬（Gakhai）
- **五行 (元素)**：木（Mod）、火（Gal）、土（Shoroo）、
  金（Temür）、水（Us），各分陰陽
- **60 年循環**：12 生肖 × 5 元素的大循環
- **擇吉**：結婚、出行、建屋、醫療等活動的吉日計算
- **松巴堪布體系**：基於 Sumpa Khenpo Yeshe Peljor 的德古斯布揚圖祖爾海
""",
        "en": """
### What is Mongolian Zurkhai (蒙古祖爾海)?

**Zurkhai (Зурхай)** is traditional Mongolian astrology, rooted in the Tibetan Buddhist calendrical system:

- **12 Animal Signs**: Rat (Hulgana), Ox (Ükher), Tiger (Bar), Rabbit (Tuulai),
  Dragon (Luu), Snake (Mogoi), Horse (Mori), Sheep (Honi), Monkey (Bich),
  Rooster (Tahia), Dog (Nokhoi), Pig (Gakhai)
- **Five Elements**: Wood (Mod), Fire (Gal), Earth (Shoroo), Metal (Temür), Water (Us), each with Yin/Yang
- **60-Year Cycle**: 12 animals × 5 elements
- **Auspicious Date Selection**: Marriage, travel, construction, medicine, and other life events
- **Sumpa Khenpo System**: Based on Sumpa Khenpo Yeshe Peljor's Tegus Buyantu Zurkhai
""",
    },
    "desc_picatrix": {
        "zh": """
### 什麼是 Picatrix 星體魔法？

**Picatrix《賢者之目的》(Ghayat al-Hakim)** 是中世紀阿拉伯魔法占星學的
最重要典籍，約成書於 10-11 世紀：

- **28 阿拉伯月宿 (Manazil al-Qamar)**：以月亮所在度數確定月宿，
  每宿有其統治行星、魔法圖像、香料、金屬與咒語
- **行星時 (Planetary Hours)**：以迦勒底序輪轉，日間夜間各 12 時，
  每時辰由不同行星主導
- **護符魔法 (Talisman Magic)**：結合月宿、行星時、材質，
  製作針對特定意圖（愛情、財富、治病等）的護符

資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim)
— Greer & Warnock 2011 translation / Attrell & Porreca 2019
""",
        "en": """
### What is Picatrix Stellar Magic?

**Picatrix (Ghayat al-Hakim, "The Goal of the Wise")** is the most important medieval Arabic magical-astrological
text, compiled around the 10th–11th century:

- **28 Arabic Lunar Mansions (Manazil al-Qamar)**: Determined by Moon's degree;
  each mansion has its ruling planet, magical image, incense, metal, and invocation
- **Planetary Hours**: Chaldean order rotates through day and night, 12 hours each,
  with a different planet ruling each hour
- **Talisman Magic**: Combining mansion, planetary hour, and materials to create
  talismans for specific intentions (love, wealth, healing, etc.)

Source: Picatrix (Ghayat al-Hakim) — Greer & Warnock 2011 / Attrell & Porreca 2019
""",
    },
}


def get_lang() -> str:
    """Return current language code: 'zh' or 'en'."""
    import streamlit as st
    return st.session_state.get("lang", "zh")


def t(key: str) -> str:
    """Return the translated string for *key* in the current language."""
    lang = get_lang()
    entry = TRANSLATIONS.get(key)
    if entry is None:
        return key
    return entry.get(lang, entry.get("zh", key))
