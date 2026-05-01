"""
七政四餘常量定義 (Constants for Seven Governors and Four Remainders)

定義中國傳統占星術中使用的星曜、宮位、二十八宿等常量。
"""

import swisseph as swe

# ============================================================
# 七政 (Seven Governors) - 七顆主要星曜
# ============================================================
SEVEN_GOVERNORS = {
    "太陽": swe.SUN,
    "太陰": swe.MOON,
    "水星": swe.MERCURY,
    "金星": swe.VENUS,
    "火星": swe.MARS,
    "木星": swe.JUPITER,
    "土星": swe.SATURN,
}

# ============================================================
# 四餘 (Four Remainders) - 四顆虛星
# 傳統七政四餘定義 (Traditional Chinese 七政四餘 definitions):
# 羅睺 (Rahu) = 降交點 / South Node (= 計都 + 180°，計算時由 calculator 推導)
# 計都 (Ketu) = 升交點 / North Node (Mean Node，傳統七政四餘使用平均交點)
# 月孛 (Yuebei) = 平均遠地點 (Mean Apogee / Lilith)
# 紫氣 (Ziqi) = 真實遠地點 (Osculating / True Apogee)
# ============================================================
FOUR_REMAINDERS = {
    "羅睺": None,                 # 降交點 / South Node = MEAN_NODE + 180° (computed in calculator)
    "計都": swe.MEAN_NODE,       # 升交點 / North Node (Mean Node)
    "月孛": swe.MEAN_APOG,       # Mean Apogee / Lilith
    "紫氣": swe.OSCU_APOG,       # Osculating Apogee (True Apogee)
}

# ============================================================
# 十二地支 (Twelve Earthly Branches)
# ============================================================
EARTHLY_BRANCHES = [
    "子", "丑", "寅", "卯", "辰", "巳",
    "午", "未", "申", "酉", "戌", "亥",
]

# ============================================================
# 十二宮 (Twelve Houses/Palaces)
# ============================================================
TWELVE_PALACES = [
    "命宮", "財帛宮", "兄弟宮", "田宅宮",
    "男女宮", "奴僕宮", "夫妻宮", "疾厄宮",
    "遷移宮", "官祿宮", "福德宮", "相貌宮",
]

# ============================================================
# 十二星次 (Twelve Star Stations) - 中國黃道十二宮
# 對應西方黃道十二宮，但起始點和名稱不同
# ============================================================
TWELVE_SIGNS_CHINESE = [
    "戌宮(降婁)", "酉宮(大梁)", "申宮(實沈)", "未宮(鶉首)",
    "午宮(鶉火)", "巳宮(鶉尾)", "辰宮(壽星)", "卯宮(大火)",
    "寅宮(析木)", "丑宮(星紀)", "子宮(玄枵)", "亥宮(娵訾)",
]

TWELVE_SIGNS_WESTERN = [
    "白羊", "金牛", "雙子", "巨蟹",
    "獅子", "處女", "天秤", "天蠍",
    "射手", "摩羯", "水瓶", "雙魚",
]

# ============================================================
# 二十八宿 (Twenty-Eight Lunar Mansions)
# 每宿對應的黃經度數範圍
# 宿界參考 MOIRA (BahnAstro/MOIRA_chinese_astrology) 精確距星黃經
# 注意: MOIRA 使用 27 個邊界點，缺少 室宿距星(α Pegasi)，
# 此處依傳統取 α Pegasi ≈ 353.49° 補全為 28 個邊界。
# ============================================================
TWENTY_EIGHT_MANSIONS = [
    # 東方青龍七宿
    {"name": "角", "element": "木", "animal": "蛟", "group": "東方青龍", "start_lon": 203.8375},
    {"name": "亢", "element": "金", "animal": "龍", "group": "東方青龍", "start_lon": 214.4899},
    {"name": "氐", "element": "土", "animal": "貉", "group": "東方青龍", "start_lon": 225.0216},
    {"name": "房", "element": "日", "animal": "兔", "group": "東方青龍", "start_lon": 242.9360},
    {"name": "心", "element": "月", "animal": "狐", "group": "東方青龍", "start_lon": 249.7584},
    {"name": "尾", "element": "火", "animal": "虎", "group": "東方青龍", "start_lon": 256.1517},
    {"name": "箕", "element": "水", "animal": "豹", "group": "東方青龍", "start_lon": 271.2576},
    # 北方玄武七宿
    {"name": "斗", "element": "木", "animal": "獬", "group": "北方玄武", "start_lon": 280.1775},
    {"name": "牛", "element": "金", "animal": "牛", "group": "北方玄武", "start_lon": 304.0435},
    {"name": "女", "element": "土", "animal": "蝠", "group": "北方玄武", "start_lon": 311.7193},
    {"name": "虛", "element": "日", "animal": "鼠", "group": "北方玄武", "start_lon": 323.3912},
    {"name": "危", "element": "月", "animal": "燕", "group": "北方玄武", "start_lon": 333.3486},
    {"name": "室", "element": "火", "animal": "豬", "group": "北方玄武", "start_lon": 353.49},
    {"name": "壁", "element": "水", "animal": "貐", "group": "北方玄武", "start_lon": 9.1522},
    # 西方白虎七宿
    {"name": "奎", "element": "木", "animal": "狼", "group": "西方白虎", "start_lon": 22.3721},
    {"name": "婁", "element": "金", "animal": "狗", "group": "西方白虎", "start_lon": 33.9661},
    {"name": "胃", "element": "土", "animal": "雉", "group": "西方白虎", "start_lon": 46.9312},
    {"name": "昴", "element": "日", "animal": "雞", "group": "西方白虎", "start_lon": 59.4080},
    {"name": "畢", "element": "月", "animal": "烏", "group": "西方白虎", "start_lon": 68.4612},
    {"name": "觜", "element": "火", "animal": "猴", "group": "西方白虎", "start_lon": 83.7030},
    {"name": "參", "element": "水", "animal": "猿", "group": "西方白虎", "start_lon": 84.6775},
    # 南方朱雀七宿
    {"name": "井", "element": "木", "animal": "犴", "group": "南方朱雀", "start_lon": 95.2980},
    {"name": "鬼", "element": "金", "animal": "羊", "group": "南方朱雀", "start_lon": 125.7246},
    {"name": "柳", "element": "土", "animal": "獐", "group": "南方朱雀", "start_lon": 130.3005},
    {"name": "星", "element": "日", "animal": "馬", "group": "南方朱雀", "start_lon": 147.2753},
    {"name": "張", "element": "月", "animal": "鹿", "group": "南方朱雀", "start_lon": 155.6874},
    {"name": "翼", "element": "火", "animal": "蛇", "group": "南方朱雀", "start_lon": 173.6856},
    {"name": "軫", "element": "水", "animal": "蚓", "group": "南方朱雀", "start_lon": 190.7218},
]

# ============================================================
# 星曜顏色 (Planet Colors for Display)
# ============================================================
PLANET_COLORS = {
    "太陽": "#FF4500",
    "太陰": "#C0C0C0",
    "水星": "#4169E1",
    "金星": "#FFD700",
    "火星": "#DC143C",
    "木星": "#228B22",
    "土星": "#8B4513",
    "羅睺": "#800080",
    "計都": "#4B0082",
    "月孛": "#2F4F4F",
    "紫氣": "#9400D3",
}

# ============================================================
# 五行 (Five Elements)
# ============================================================
FIVE_ELEMENTS = {
    "太陽": "日",
    "太陰": "月",
    "水星": "水",
    "金星": "金",
    "火星": "火",
    "木星": "木",
    "土星": "土",
    "羅睺": "火",
    "計都": "土",
    "月孛": "水",
    "紫氣": "木",
}

# ============================================================
# 十二宮五行屬性 (Zodiac Sign Elements)
# 參考 MOIRA (BahnAstro/MOIRA_chinese_astrology) 五行分配
# 索引對應西方星座: 0=白羊, 1=金牛, ..., 11=雙魚
# ============================================================
ZODIAC_SIGN_ELEMENTS = [
    "火",   # 白羊 (Aries) — fire
    "金",   # 金牛 (Taurus) — metal
    "水",   # 雙子 (Gemini) — water
    "月",   # 巨蟹 (Cancer) — moon
    "日",   # 獅子 (Leo) — sun
    "水",   # 處女 (Virgo) — water
    "金",   # 天秤 (Libra) — metal
    "火",   # 天蠍 (Scorpio) — fire
    "木",   # 射手 (Sagittarius) — wood
    "土",   # 摩羯 (Capricorn) — earth
    "土",   # 水瓶 (Aquarius) — earth
    "木",   # 雙魚 (Pisces) — wood
]
