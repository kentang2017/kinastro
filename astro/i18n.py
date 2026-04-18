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
        "zh": "✨ 輸入你的出生資料，一鍵了解你的命運走向",
        "en": "✨ Enter your birth info and discover your destiny in one click",
    },
    # ── Sidebar ─────────────────────────────────────────────────────────────
    "sidebar_header": {
        "zh": "📝 你的出生資料",
        "en": "📝 Your Birth Info",
    },
    "date_time": {
        "zh": "出生日期和時間",
        "en": "Birth Date & Time",
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
        "zh": "你在哪裡出生？",
        "en": "Where were you born?",
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
        "zh": "你的性別",
        "en": "Your Gender",
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
        "zh": "🀄 七政四餘",
        "en": "🀄 Qi Zheng Si Yu (Chinese Astrology)",
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
        "zh": "🈳 日本宿曜道",
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
        "zh": "🔱 印度納迪占星",
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
    "tab_shams": {
        "zh": "☪ 太陽知識大全",
        "en": "☪ Shams al-Maʻārif",
    },
    # ── Arabic sub-tab labels ─────────────────────────────────────────────────
    "arabic_subtab_chart": {
        "zh": "☪ 阿拉伯占星",
        "en": "☪ Arabic Astrology",
    },
    "arabic_subtab_picatrix": {
        "zh": "📜 Picatrix 星體魔法",
        "en": "📜 Picatrix Stellar Magic",
    },
    "arabic_subtab_shams": {
        "zh": "☪ 太陽知識大全",
        "en": "☪ Shams al-Maʻārif",
    },
    "arabic_subtab_reference": {"zh": "古籍知識庫", "en": "Reference Library"},
    "arabic_subtab_ms164": {"zh": "📜 MS.164 手稿", "en": "📜 MS.164 Manuscript"},
    # ── Chinese (七政四餘) sub-tab labels ──────────────────────────────────────
    "ch_subtab_natal": {
        "zh": "🎯 本命盤",
        "en": "🎯 Natal Chart",
    },
    "ch_subtab_shensha": {
        "zh": "🔮 神煞",
        "en": "🔮 Shen Sha",
    },
    "ch_subtab_dasha": {
        "zh": "📅 年限大運",
        "en": "📅 Planetary Periods",
    },
    "ch_subtab_transit": {
        "zh": "🔄 流時對盤",
        "en": "🔄 Transit Chart",
    },
    "ch_subtab_zhangguo": {
        "zh": "📜 張果星宗",
        "en": "📜 Zhang Guo Star Readings",
    },
    "show_transit_overlay": {
        "zh": "在圓盤上顯示流時星曜",
        "en": "Show transit planets on ring chart",
    },
    "transit_header": {
        "zh": "🔄 流時對盤",
        "en": "🔄 Transit Chart Comparison",
    },
    "transit_date": {
        "zh": "流時日期",
        "en": "Transit date",
    },
    "transit_time": {
        "zh": "流時時間",
        "en": "Transit time",
    },
    "transit_tz": {
        "zh": "流時時區",
        "en": "Transit TZ",
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
    "thai_subtab_brahma": {
        "zh": "📖 พรหมชาติ (泰國命理)",
        "en": "📖 Brahma Jati (Thai Fate Reading)",
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
    "shams_subheader": {
        "zh": "☪ 《太陽知識大全》 (Shams al-Maʻārif al-Kubrā)",
        "en": "☪ Shams al-Maʻārif al-Kubrā",
    },
    "shams_source": {
        "zh": "資料來源：《Shams al-Maʻārif al-Kubrā wa Laṭāʼif al-ʻAwārif》— 1927 McGill 版",
        "en": "Source: Shams al-Maʻārif al-Kubrā wa Laṭāʼif al-ʻAwārif — 1927 McGill edition",
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
    "desc_shams": {
        "zh": """
### 什麼是《太陽知識大全》(Shams al-Maʻārif)？

**《شمس المعارف الكبرى》(Shams al-Maʻārif al-Kubrā)**
是伊斯蘭神秘學最重要的經典之一，由 Aḥmad ibn ʿAlī al-Būnī（1225年卒）所著：

- **七大行星特性**：日、月、水、金、火、木、土的體質、元素、顏色與護符用途
- **十二星座徵兆**：各星座在護符與預言中的意義
- **方陣 (Wafq)**：3×3 至 9×9 魔方方陣，用於護符製作
- **九十九美名 (Asmāʼ al-Ḥusnā)**：每個美名對應行星、用途與時辰
- **修持法 (Riyāḍa)**：結合誦念、香料、齋戒的靈性修行
- **祈禱文 (Du'a)**：各種場景的咒語與祈禱

資料來源：《Shams al-Maʻārif al-Kubrā wa Laṭāʼif al-ʻAwārif》— 1927 McGill 版
""",
        "en": """
### What is Shams al-Maʻārif?

**Shams al-Maʻārif al-Kubrā (شمس المعارف الكبرى, "The Great Sun of Gnosis")**
is one of the most important texts in Islamic esoteric tradition, attributed to
Aḥmad ibn ʿAlī al-Būnī (d. 1225):

- **Seven Planetary Properties**: Temperaments, elements, colours, and talisman uses for each planet
- **Twelve Zodiac Sign Omens**: Significance of each sign in talismanic and divinatory contexts
- **Wafq (Magic Squares)**: 3×3 to 9×9 magic squares for talisman construction
- **99 Beautiful Names (Asmāʼ al-Ḥusnā)**: Each Name mapped to a planet, purpose, and timing
- **Riyāḍa (Spiritual Exercises)**: Practices combining recitation, incense, and fasting
- **Du'a (Invocations)**: Prayers and invocations for various purposes

Source: Shams al-Maʻārif al-Kubrā wa Laṭāʼif al-ʻAwārif — 1927 McGill edition
""",
    },

    # ── 萬化仙禽 (WanHua XianQin) ───────────────────────────
    "tab_chinstar": {"zh": "🐦 中國萬化仙禽", "en": "🐦 WanHua XianQin"},
    "desc_chinstar": {
        "zh": (
            "**萬化仙禽（新刻劉伯溫萬化仙禽）**\n\n"
            "依據明代古籍《新刻劉伯溫萬化仙禽》（朱國祥著）之演禽推算系統。\n"
            "涵蓋三元起宿、推胎宮、推胎星、推命宮（時加至卯）、推身宮、"
            "推命星、推身星、十二宮衍生星、吞啗合戰判斷、情性賦及格局分析。\n\n"
            "⚠️ 本系統以**農曆**年月日起盤，請在下方輸入農曆出生資料。"
        ),
        "en": (
            "**WanHua XianQin (萬化仙禽)**\n\n"
            "Star-Animal Divination based on the classical Ming-dynasty text "
            "«新刻劉伯溫萬化仙禽» by Zhu Guoxiang.\n"
            "Covers 三元起宿, Fetus Palace, Natal Star, Life Palace, Body Palace, "
            "12 Derived Stars, Swallow-Bite analysis, Personality verse and Chart Pattern.\n\n"
            "⚠️ This system uses the **Lunar Calendar**. Please enter your lunar birth date below."
        ),
    },
    "spinner_chinstar": {"zh": "計算萬化仙禽盤中...", "en": "Computing WanHua XianQin chart…"},
    "chinstar_lunar_input_header": {"zh": "🗓️ 農曆出生資料", "en": "🗓️ Lunar Birth Data"},
    "chinstar_lunar_year": {"zh": "農曆年（公曆年）", "en": "Lunar Year (solar year)"},
    "chinstar_lunar_month": {"zh": "農曆月", "en": "Lunar Month"},
    "chinstar_lunar_day": {"zh": "農曆日", "en": "Lunar Day"},
    "chinstar_use_auto": {"zh": "自動從公曆換算農曆", "en": "Auto-convert from solar date"},
    "chinstar_auto_result": {"zh": "換算結果：{year}年{month}月{day}日 {hour}時", "en": "Converted: {year}-{month}-{day} {hour} hour"},
    "chinstar_subtab_chart": {"zh": "起盤結果", "en": "Chart Result"},
    "chinstar_subtab_text": {"zh": "古籍全文", "en": "Classical Text"},
    "chinstar_subtab_xiangtai": {"zh": "相胎賦", "en": "Birth Combination Reading"},
    "chinstar_subtab_gui_jian": {"zh": "貴賤格", "en": "Noble/Ignoble Patterns"},
    "chinstar_leap_month": {"zh": "（閏月）", "en": " (Leap Month)"},
    "chinstar_auto_convert_failed": {"zh": "自動換算失敗，請手動輸入農曆日期：", "en": "Auto-conversion failed, please enter lunar date manually: "},
    "chinstar_no_swallow": {"zh": "無吞啗關係", "en": "No swallow/bite relationship"},
    "chinstar_text_not_found": {"zh": "古籍文本文件未找到", "en": "Classical text file not found"},
    "chinstar_birth_info": {"zh": "**出生**：{year}年{month}月{day}日 {hour}時　{gender}命　{day_night}　{season}季　**三元**：{san_yuan}", "en": "**Birth**: {year}-{month}-{day} {hour}h　{gender}　{day_night}　{season}　**Three Cycles**: {san_yuan}"},
    "chinstar_twelve_palaces_header": {"zh": "#### 十二宮排布（命宮起逆行）", "en": "#### Twelve Palaces (counter-clockwise from Life Palace)"},
    "chinstar_derived_stars_header": {"zh": "#### 衍生星", "en": "#### Derived Stars"},
    "chinstar_swallow_analysis_header": {"zh": "#### 吞啗 / 合戰分析", "en": "#### Swallow-Bite / Alliance-Battle Analysis"},
    "chinstar_personality_header": {"zh": "#### 情性賦", "en": "#### Personality Verse"},
    "chinstar_pattern_header": {"zh": "#### 格局：{grade}", "en": "#### Chart Pattern: {grade}"},
    "chinstar_full_text_expander": {"zh": "📄 完整文字輸出", "en": "📄 Full Text Output"},
    "chinstar_full_text_label": {"zh": "新刻劉伯溫萬化仙禽（全文）", "en": "WanHua XianQin Classical Text (Full)"},
    "chinstar_xiangtai_title": {"zh": "#### 相胎賦 — 主星胎星配合論斷", "en": "#### Birth Combination Reading — Main Star + Birth Star"},
    "chinstar_xiangtai_match": {"zh": "**命星 {zhu} × 胎星 {tai}** 配合斷語", "en": "**Life Star {zhu} × Birth Star {tai}** Combination Reading"},
    "chinstar_xiangtai_xingpin": {"zh": "形品", "en": "Appearance"},
    "chinstar_xiangtai_xiji": {"zh": "喜忌", "en": "Favored/Avoided"},
    "chinstar_xiangtai_desc": {"zh": "論斷", "en": "Reading"},
    "chinstar_xiangtai_poem": {"zh": "斷曰", "en": "Poem"},
    "chinstar_xiangtai_no_match": {"zh": "⚠️ 未找到命星與胎星的相胎賦配合", "en": "⚠️ No matching birth combination reading found"},
    "chinstar_xiangtai_ref": {"zh": "📖 相胎賦全覽（28組主胎配合）", "en": "📖 All 28 Birth Combination Readings"},
    "chinstar_gui_title": {"zh": "#### 貴格 — 吉利格局", "en": "#### Noble Patterns — Auspicious Configurations"},
    "chinstar_jian_title": {"zh": "#### 賤格 — 凶煞格局", "en": "#### Ignoble Patterns — Inauspicious Configurations"},
    "chinstar_fulu_title": {"zh": "#### 福祿上格", "en": "#### Auspicious High Rank Patterns"},
    "chinstar_pinjian_title": {"zh": "#### 貧賤下命", "en": "#### Inauspicious Low Rank Patterns"},
    "chinstar_gui_for_star": {"zh": "**{star}** 貴格", "en": "**{star}** Noble Patterns"},
    "chinstar_jian_for_star": {"zh": "**{star}** 賤格", "en": "**{star}** Ignoble Patterns"},
    "chinstar_no_gui": {"zh": "無貴格記錄", "en": "No noble patterns recorded"},
    "chinstar_no_jian": {"zh": "無賤格記錄", "en": "No ignoble patterns recorded"},

    # ── Hellenistic Astrology ───────────────────────────────
    "tab_hellenistic": {"zh": "🏛️ 希臘占星", "en": "🏛️ Hellenistic"},
    "desc_hellenistic": {
        "zh": "**希臘占星（Hellenistic Astrology）**\n\n源自古希臘-羅馬的占星傳統，包含希臘點、埃及界主、年限推進、黃道釋放、行星狀態評分等經典技法。",
        "en": "**Hellenistic Astrology**\n\nThe Greco-Roman tradition featuring Greek Lots, Egyptian Bounds, Annual Profections, Zodiacal Releasing, and Planetary Condition scoring.",
    },
    "spinner_hellenistic": {"zh": "計算希臘占星盤中...", "en": "Computing Hellenistic chart…"},
    "hellen_subtab_chart": {"zh": "星盤圖", "en": "Chart"},
    "hellen_subtab_natal": {"zh": "本命盤", "en": "Natal"},
    "hellen_subtab_profections": {"zh": "年限推進", "en": "Profections"},
    "hellen_subtab_zr": {"zh": "黃道釋放", "en": "Zodiacal Releasing"},
    "hellen_subtab_lots": {"zh": "希臘點", "en": "Lots"},
    "hellen_subtab_centiloquy": {"zh": "百論", "en": "Centiloquy"},

    # ── Western sub-tabs ────────────────────────────────────
    "western_subtab_natal": {"zh": "本命盤", "en": "Natal"},
    "western_subtab_transit": {"zh": "流年過運", "en": "Transits"},
    "western_subtab_return": {"zh": "返照盤", "en": "Solar Return"},
    "western_subtab_synastry": {"zh": "合盤", "en": "Synastry"},
    "western_subtab_dignity": {"zh": "行星尊卑", "en": "Dignities"},
    "transit_target_date": {"zh": "過運日期", "en": "Transit Date"},
    "return_year_label": {"zh": "返照年份", "en": "Return Year"},
    "synastry_header": {"zh": "合盤比較", "en": "Synastry Comparison"},
    "synastry_person_b": {"zh": "對象 B 出生資料", "en": "Person B Birth Data"},

    # ── Vedic sub-tabs ──────────────────────────────────────
    "vedic_subtab_rashi": {"zh": "星盤 Rashi", "en": "Rashi Chart"},
    "vedic_subtab_navamsa": {"zh": "九分盤 D9", "en": "Navamsa D9"},
    "vedic_subtab_dasha": {"zh": "大運 Dasha", "en": "Dasha"},
    "vedic_subtab_ashtaka": {"zh": "八分力量", "en": "Ashtakavarga"},
    "vedic_subtab_yogas": {"zh": "瑜伽組合", "en": "Yogas"},
    "vedic_subtab_bphs": {"zh": "帕拉夏拉大占星經", "en": "BPHS Classic"},

    # ── Ziwei sub-tabs ──────────────────────────────────────
    "ziwei_subtab_natal": {"zh": "本命盤", "en": "Natal"},
    "ziwei_subtab_daxian": {"zh": "大限流年", "en": "Daxian / Liunian"},

    # ── Qizheng electional ──────────────────────────────────
    "ch_subtab_electional": {"zh": "擇日", "en": "Electional"},

    # ── Fixed stars & asteroids ─────────────────────────────
    "show_fixed_stars": {"zh": "顯示恆星合相", "en": "Show Fixed Star Conjunctions"},
    "show_asteroids": {"zh": "顯示小行星", "en": "Show Asteroids"},

    # ── Export ──────────────────────────────────────────────
    "export_header": {"zh": "匯出", "en": "Export"},
    # PDF keys removed — PDF generation has been removed

    # ── Natal summary / Interpretations ────────────────────
    "natal_summary_header": {"zh": "📝 命盤解讀 / Natal Summary", "en": "📝 Natal Summary"},
    "transit_readings_header": {"zh": "📖 流年解讀 / Transit Readings", "en": "📖 Transit Readings"},
    "synastry_readings_header": {"zh": "📖 合盤解讀 / Synastry Readings", "en": "📖 Synastry Readings"},
    "dasha_reading_header": {"zh": "📖 大限解讀", "en": "📖 Dasha Interpretation"},

    # ── Error boundary ─────────────────────────────────────
    "error_tab_compute": {
        "zh": "此體系計算時發生錯誤",
        "en": "An error occurred computing this system",
    },

    # ── Sidebar astrology selector ─────────────────────────
    "sidebar_system_home": {
        "zh": "🏠 首頁（世界地圖）",
        "en": "🏠 Home (World Map)",
    },

    # ── World map homepage ─────────────────────────────────
    "map_title": {
        "zh": "🗺️ 世界占星地圖 — 點選地區探索占星體系",
        "en": "🗺️ World Astrology Map — Click a region to explore",
    },
    "map_subtitle": {
        "zh": "將滑鼠移到地區上方可查看該地區的占星體系，點擊按鈕即可進入",
        "en": "Hover over a region to see its astrology systems, click a button to enter",
    },

    # ── AI Analysis (AI 分析) ──────────────────────────────────
    "ai_settings_header": {
        "zh": "🤖 AI 分析設置",
        "en": "🤖 AI Analysis Settings",
    },
    "ai_model_label": {
        "zh": "AI 模型",
        "en": "AI Model",
    },
    "ai_select_prompt": {
        "zh": "選擇系統提示",
        "en": "Select System Prompt",
    },
    "ai_select_prompt_help": {
        "zh": "選擇用於 AI 模型的系統提示，指導其分析排盤結果",
        "en": "Select a system prompt for the AI model to guide chart analysis",
    },
    "ai_edit_prompt": {
        "zh": "編輯提示內容",
        "en": "Edit Prompt Content",
    },
    "ai_edit_prompt_placeholder": {
        "zh": "在此編輯系統提示內容…",
        "en": "Edit the system prompt content here…",
    },
    "ai_update_prompt_btn": {
        "zh": "💾 更新提示",
        "en": "💾 Update Prompt",
    },
    "ai_delete_prompt_btn": {
        "zh": "🗑️ 刪除提示",
        "en": "🗑️ Delete Prompt",
    },
    "ai_add_prompt_expander": {
        "zh": "➕ 新增自訂提示",
        "en": "➕ Add Custom Prompt",
    },
    "ai_new_prompt_name": {
        "zh": "提示名稱",
        "en": "Prompt Name",
    },
    "ai_new_prompt_content": {
        "zh": "提示內容",
        "en": "Prompt Content",
    },
    "ai_new_prompt_placeholder": {
        "zh": "輸入 AI 分析指令…",
        "en": "Enter AI analysis instructions…",
    },
    "ai_save_new_prompt_btn": {
        "zh": "💾 儲存新提示",
        "en": "💾 Save New Prompt",
    },
    "ai_prompt_updated": {
        "zh": "✅ 已更新提示「{}」",
        "en": '✅ Prompt "{}" updated',
    },
    "ai_prompt_deleted": {
        "zh": "🗑️ 已刪除提示「{}」",
        "en": '🗑️ Prompt "{}" deleted',
    },
    "ai_prompt_saved": {
        "zh": "✅ 已新增提示「{}」",
        "en": '✅ Prompt "{}" saved',
    },
    "ai_max_tokens": {
        "zh": "最大回應長度",
        "en": "Max Response Tokens",
    },
    "ai_max_tokens_help": {
        "zh": "控制 AI 回應的最大長度",
        "en": "Control the maximum length of AI responses",
    },
    "ai_temperature": {
        "zh": "溫度 (Temperature)",
        "en": "Temperature",
    },
    "ai_temperature_help": {
        "zh": "較高的溫度會產生更有創意的回應，較低則更精確",
        "en": "Higher temperature produces more creative responses, lower is more precise",
    },
    "ai_analyze_btn": {
        "zh": "🔍 使用 AI 分析排盤結果",
        "en": "🔍 Analyze Chart with AI",
    },
    "ai_analyzing": {
        "zh": "AI 正在分析排盤結果…",
        "en": "AI is analyzing the chart…",
    },
    "ai_key_missing": {
        "zh": "⚠️ 未設置 Cerebras API Key。請在 Streamlit Secrets 或環境變數中設定 CEREBRAS_API_KEY。",
        "en": "⚠️ Cerebras API Key not found. Set CEREBRAS_API_KEY in Streamlit Secrets or environment variables.",
    },
    "ai_error": {
        "zh": "❌ 調用 AI 時發生錯誤：{}",
        "en": "❌ Error calling AI: {}",
    },
    "ai_rate_limit": {
        "zh": "⏳ AI 服務目前流量過高，已自動重試但仍未成功。請稍後再試。",
        "en": "⏳ AI service is experiencing high traffic. Automatic retries were exhausted. Please try again shortly.",
    },
    "ai_result_header": {
        "zh": "🤖 AI 分析結果",
        "en": "🤖 AI Analysis Result",
    },
    "ai_no_chart": {
        "zh": "請先計算排盤後再進行 AI 分析。",
        "en": "Please compute a chart first before running AI analysis.",
    },
    "tab_contact": {"zh": "📬 關於 / 聯繫", "en": "📬 About / Contact"},
    "contact_title": {"zh": "開發者資訊", "en": "Developer Info"},
    "contact_wechat": {"zh": "微信公眾號：**探究三式**", "en": "WeChat Official Account: **探究三式**"},
    "contact_wechat_id": {
        "zh": "如有任何建議或合作事宜，可加本人微信聯繫，或搜 **gnatnek**（請註明是在 GitHub 加我的）",
        "en": "For suggestions or collaboration, add WeChat ID **gnatnek** (please mention you found me on GitHub)",
    },
    "contact_qq": {
        "zh": "或加入 QQ 群組「堅三式軟件交流群」（群號 **770621021**）",
        "en": "Or join QQ Group 「堅三式軟件交流群」 (Group ID **770621021**)",
    },
    "contact_other_apps": {"zh": "其他相關應用", "en": "Other Related Apps"},

    # ── GUI Optimization: System categories ─────────────────
    "cat_popular": {"zh": "⭐ 最熱門", "en": "⭐ Most Popular"},
    "cat_chinese": {"zh": "🏮 中華傳統", "en": "🏮 Chinese Traditions"},
    "cat_western": {"zh": "🌍 西方體系", "en": "🌍 Western Systems"},
    "cat_asian": {"zh": "🌏 亞洲體系", "en": "🌏 Asian Systems"},
    "cat_middle_east": {"zh": "☪ 中東體系", "en": "☪ Middle Eastern Systems"},
    "cat_ancient": {"zh": "📜 古文明", "en": "📜 Ancient Civilizations"},

    # ── GUI Optimization: Short beginner-friendly system descriptions ──
    "sys_hint_western": {"zh": "最廣為人知的星座運勢", "en": "The most well-known horoscope system"},
    "sys_hint_ziwei": {"zh": "中國最流行的命理系統", "en": "China's most popular destiny system"},
    "sys_hint_chinese": {"zh": "中國古代天文星象占卜", "en": "Ancient Chinese astronomical divination"},
    "sys_hint_indian": {"zh": "印度古老吠陀占星", "en": "Ancient Vedic astrology from India"},
    "sys_hint_thai": {"zh": "泰國傳統命理解讀", "en": "Traditional Thai fate reading"},
    "sys_hint_kabbalistic": {"zh": "猶太神祕主義占星", "en": "Jewish mystical astrology"},
    "sys_hint_arabic": {"zh": "伊斯蘭黃金時代占星術", "en": "Islamic Golden Age astrology"},
    "sys_hint_maya": {"zh": "瑪雅文明曆法占卜", "en": "Mayan calendar-based divination"},
    "sys_hint_mahabote": {"zh": "緬甸出生星期推算", "en": "Myanmar weekday-based astrology"},
    "sys_hint_decans": {"zh": "古埃及十度區間預測", "en": "Ancient Egyptian decan predictions"},
    "sys_hint_nadi": {"zh": "南印度棕櫚葉手稿", "en": "South Indian palm-leaf readings"},
    "sys_hint_zurkhai": {"zh": "蒙古藏傳佛教占星", "en": "Mongolian Tibetan Buddhist astrology"},
    "sys_hint_hellenistic": {"zh": "古希臘羅馬占星傳統", "en": "Greco-Roman astrological tradition"},
    "sys_hint_sukkayodo": {"zh": "日本宿曜道擇日占卜", "en": "Japanese lunar mansion divination"},
    "sys_hint_chinstar": {"zh": "明代演禽命理推算", "en": "Ming dynasty bird-star divination"},

    # ── GUI Optimization: Welcome / onboarding ─────────────
    "welcome_hero_title": {
        "zh": "歡迎來到堅占星 ⭐",
        "en": "Welcome to Kin Astro ⭐",
    },
    "welcome_hero_body": {
        "zh": "不用懂占星也能了解自己！只需 3 步，即可獲得你的專屬命理分析。",
        "en": "No astrology knowledge needed! Just 3 steps to get your personal destiny reading.",
    },
    "welcome_step1_title": {"zh": "填寫出生資料", "en": "Enter Birth Info"},
    "welcome_step1_body": {
        "zh": "在左邊欄填入出生日期、時間、地點",
        "en": "Fill in your birth date, time, and place in the sidebar",
    },
    "welcome_step2_title": {"zh": "選擇占星類型", "en": "Pick a System"},
    "welcome_step2_body": {
        "zh": "推薦從「西洋占星」或「紫微斗數」開始",
        "en": "Start with Western Astrology or Zi Wei Dou Shu",
    },
    "welcome_step3_title": {"zh": "AI 幫你解讀", "en": "AI Reads for You"},
    "welcome_step3_body": {
        "zh": "點擊 AI 分析按鈕，用白話文解讀你的命盤",
        "en": "Click AI Analysis to get a plain-language reading",
    },
    "welcome_quick_start": {
        "zh": "👈 先在左邊欄輸入你的出生資料，再選擇一個占星體系吧！",
        "en": "👈 Start by entering your birth info in the sidebar, then pick a system!",
    },
    "sidebar_system_label": {
        "zh": "選擇你想了解的命理",
        "en": "Pick Your Destiny Reading",
    },

    # ── GUI Optimization: Simplified info prompt ───────────
    "info_calc_prompt": {
        "zh": "👈 請在左邊欄填寫你的出生資料，然後點選你想了解的占星類型。",
        "en": "👈 Enter your birth info on the left, then pick the astrology system you want.",
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
