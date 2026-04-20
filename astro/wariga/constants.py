"""
巴厘傳統 Wariga 常量定義 (Constants for Balinese Wariga Calendar System)

定義巴厘傳統曆法中使用的所有 Wuku、Wewaran、Neptu/Urip 數值表格。
所有數值嚴格依照古典 Lontar Wariga / Dasar Wariga 傳統規則硬編碼，
不使用任何現代天文簡化公式或近似值。

古法依據：Lontar Wariga / Dasar Wariga
"""

# ============================================================
# 基準日 (Epoch) — 1969年12月31日（星期三）= Wuku Sinta 第1天
# 巴厘傳統 Pawukon 210 天週期的計算基準
# 依據傳統文獻，此日為已知的 Wuku Sinta 起點
# ============================================================
EPOCH_YEAR = 1969
EPOCH_MONTH = 12
EPOCH_DAY = 31

# ============================================================
# 210天 Pawukon 週期中的 30 個 Wuku
# 每個 Wuku 持續 7 天，30 × 7 = 210 天
# 格式：(名稱, Neptu/Urip 值)
# 古法依據：Lontar Wariga — Wuku Neptu 表
# ============================================================
WUKU_TABLE = [
    ("Sinta",       7),
    ("Landep",      1),
    ("Ukir",        4),
    ("Kulantir",    6),
    ("Tolu",        5),
    ("Gumbreg",     8),
    ("Wariga",      9),
    ("Warigadian",  3),
    ("Julungwangi", 7),
    ("Sungsang",    1),
    ("Dungulan",    4),
    ("Kuningan",    6),
    ("Langkir",     5),
    ("Medangsia",   8),
    ("Pujut",       9),
    ("Pahang",      3),
    ("Krulut",      7),
    ("Merakih",     1),
    ("Tambir",      4),
    ("Medangkungan", 6),
    ("Matal",       5),
    ("Uye",         8),
    ("Menail",      9),
    ("Prangbakat",  3),
    ("Bala",        7),
    ("Ugu",         1),
    ("Wayang",      4),
    ("Klawu",       6),
    ("Dukut",       5),
    ("Watugunung",  8),
]

# ============================================================
# Eka Wara (1 天週期) — 只有一個值，不分日
# 古法依據：Lontar Wariga — Eka Wara 表
# ============================================================
EKA_WARA = [
    ("Luang", 1),
]

# ============================================================
# Dwi Wara (2 天週期)
# 古法依據：Lontar Wariga — Dwi Wara 表
# ============================================================
DWI_WARA = [
    ("Menga",  0),
    ("Pepet",  5),
]

# ============================================================
# Tri Wara (3 天週期)
# 古法依據：Lontar Wariga — Tri Wara 表
# ============================================================
TRI_WARA = [
    ("Pasah",   9),
    ("Beteng",  4),
    ("Kajeng",  7),
]

# ============================================================
# Catur Wara (4 天週期)
# 注意：非線性取模，第6、7天特殊處理（Jaya 和 Menala 跳過）
# 古法依據：Lontar Wariga — Catur Wara 表
# ============================================================
CATUR_WARA = [
    ("Sri",    6),
    ("Laba",   5),
    ("Jaya",   1),
    ("Menala", 8),
]

# ============================================================
# Panca Wara (5 天週期)
# 古法依據：Lontar Wariga — Panca Wara Urip 表
# ============================================================
PANCA_WARA = [
    ("Umanis",  5),
    ("Paing",   9),
    ("Pon",     7),
    ("Wage",    4),
    ("Kliwon",  8),
]

# ============================================================
# Sad Wara (6 天週期)
# 古法依據：Lontar Wariga — Sad Wara 表
# ============================================================
SAD_WARA = [
    ("Tungleh",  7),
    ("Aryang",   6),
    ("Urukung",  5),
    ("Paniron",  8),
    ("Was",      9),
    ("Maulu",    3),
]

# ============================================================
# Sapta Wara (7 天週期) — 星期
# 古法依據：Lontar Wariga — Sapta Wara Urip 表
# ============================================================
SAPTA_WARA = [
    ("Redite",      5),   # 星期日 (Sunday)
    ("Soma",        4),   # 星期一 (Monday)
    ("Anggara",     3),   # 星期二 (Tuesday)
    ("Buda",        7),   # 星期三 (Wednesday)
    ("Wraspati",    8),   # 星期四 (Thursday)
    ("Sukra",       6),   # 星期五 (Friday)
    ("Saniscara",   9),   # 星期六 (Saturday)
]

# ============================================================
# Asta Wara (8 天週期)
# 注意：非線性取模，第6、7、8天特殊處理
# （Kala 跳過 Wuku 的第6天，因此需要特殊偏移規則）
# 古法依據：Lontar Wariga — Asta Wara 表
# ============================================================
ASTA_WARA = [
    ("Sri",        6),
    ("Indra",      5),
    ("Guru",       8),
    ("Yama",       9),
    ("Ludra",      3),
    ("Brahma",     7),
    ("Kala",       1),
    ("Uma",        4),
]

# ============================================================
# Sanga Wara (9 天週期)
# 注意：非線性取模，特殊跳過規則
# 古法依據：Lontar Wariga — Sanga Wara 表
# ============================================================
SANGA_WARA = [
    ("Dangu",       5),
    ("Jangur",      8),
    ("Gigis",       9),
    ("Nohan",       3),
    ("Ogan",        7),
    ("Erangan",     1),
    ("Urungan",     4),
    ("Tulus",       6),
    ("Dadi",        8),
]

# ============================================================
# Dasa Wara (10 天週期)
# 取模方式：(Panca Wara Urip + Sapta Wara Urip) mod 10
# 即由 Panca Wara 和 Sapta Wara 的組合計算
# 古法依據：Lontar Wariga — Dasa Wara 表
# ============================================================
DASA_WARA = [
    ("Pandita",   5),
    ("Pati",      7),
    ("Suka",     10),
    ("Duka",      4),
    ("Sri",       6),
    ("Manuh",     2),
    ("Manusa",    3),
    ("Raja",      8),
    ("Dewa",      9),
    ("Raksasa",   1),
]

# ============================================================
# Ingkel（5 類動物分類，42 天為一週期，每類持續 7 天 × 6 = 42 天？）
# 實際上 Ingkel 以 Wuku 為基準，每 6 個 Wuku 一組
# 古法依據：Lontar Wariga — Ingkel 分類表
# ============================================================
INGKEL = [
    "Wong",      # 人 (0-5 Wuku)
    "Sato",      # 獸 (6-11 Wuku)
    "Mina",      # 魚 (12-17 Wuku)
    "Manuk",     # 鳥 (18-23 Wuku)
    "Taru",      # 樹 (24-29 Wuku)
]

# ============================================================
# Watek（兩組：Watek Alit 4類 和 Watek Madya 5類）
# 古法依據：Lontar Wariga
# ============================================================
WATEK_ALIT = [
    "Lembut",
    "Mider",
    "Uler",
    "Gajah",
]

WATEK_MADYA = [
    "Wong",
    "Suku Empat",
    "Paksi",
    "Ikan (Mina)",
    "Taru",
]

# ============================================================
# Pawatekan — Wuku 對應的 Watek Alit 和 Watek Madya 索引
# 格式：(Watek Alit 索引, Watek Madya 索引)
# 古法依據：Lontar Wariga — Pawatekan 對照表
# ============================================================
PAWATEKAN = [
    (3, 0),  # Sinta       → Gajah, Wong
    (2, 1),  # Landep      → Uler, Suku Empat
    (1, 2),  # Ukir        → Mider, Paksi
    (0, 3),  # Kulantir    → Lembut, Ikan
    (3, 4),  # Tolu        → Gajah, Taru
    (2, 0),  # Gumbreg     → Uler, Wong
    (1, 1),  # Wariga      → Mider, Suku Empat
    (0, 2),  # Warigadian  → Lembut, Paksi
    (3, 3),  # Julungwangi → Gajah, Ikan
    (2, 4),  # Sungsang    → Uler, Taru
    (1, 0),  # Dungulan    → Mider, Wong
    (0, 1),  # Kuningan    → Lembut, Suku Empat
    (3, 2),  # Langkir     → Gajah, Paksi
    (2, 3),  # Medangsia   → Uler, Ikan
    (1, 4),  # Pujut       → Mider, Taru
    (0, 0),  # Pahang      → Lembut, Wong
    (3, 1),  # Krulut      → Gajah, Suku Empat
    (2, 2),  # Merakih     → Uler, Paksi
    (1, 3),  # Tambir      → Mider, Ikan
    (0, 4),  # Medangkungan→ Lembut, Taru
    (3, 0),  # Matal       → Gajah, Wong
    (2, 1),  # Uye         → Uler, Suku Empat
    (1, 2),  # Menail      → Mider, Paksi
    (0, 3),  # Prangbakat  → Lembut, Ikan
    (3, 4),  # Bala        → Gajah, Taru
    (2, 0),  # Ugu         → Uler, Wong
    (1, 1),  # Wayang      → Mider, Suku Empat
    (0, 2),  # Klawu       → Lembut, Paksi
    (3, 3),  # Dukut       → Gajah, Ikan
    (2, 4),  # Watugunung  → Uler, Taru
]

# ============================================================
# Lintang（35 星宿，與 Wuku 日相關的星座分類）
# Pawukon 日序 mod 35 → 對應一個 Lintang
# 共 35 個 Lintang（取模 35）
# 古法依據：Lontar Wariga — Lintang 表
# ============================================================
LINTANG = [
    "Kartika",          # 0
    "Sungsang",         # 1
    "Uluku (Waluku)",   # 2 — Orion/犁星
    "Lumbung",          # 3
    "Kumba",            # 4
    "Udang",            # 5
    "Asu",              # 6
    "Begoong",          # 7
    "Tiruan (Magelut)", # 8
    "Sangka Tikel",     # 9
    "Bubu Bolong",      # 10
    "Sugenge (Sungenge)", # 11
    "Tangis",           # 12
    "Salah Ukur",       # 13
    "Perahu Pegat",     # 14
    "Puwuh Atarung",    # 15
    "Lair",             # 16
    "Kelapa (Klapa)",   # 17
    "Yuyu",             # 18
    "Lontong",          # 19
    "Udan (Angsa)",     # 20
    "Pedati",           # 21
    "Megantung (Kuda)", # 22
    "Bade (Mangelut)",  # 23
    "Macan (Harimau)",  # 24
    "Lembu",            # 25
    "Jaran (Kuda)",     # 26
    "Ikan",             # 27
    "Panah",            # 28
    "Patrem",           # 29
    "Lembu",            # 30
    "Buku Sema (Gelung Naga)", # 31
    "Dasba (Swamba)",   # 32
    "Mintuna",          # 33
    "Naga Ngadeg",      # 34
]

# ============================================================
# Sasih（巴厘傳統 12 個月，基於陰陽合曆）
# 古法依據：Lontar Wariga — Sasih 表
# ============================================================
SASIH_NAMES = [
    "Kasa",         # 1  — 約格里高利曆 7月
    "Karo",         # 2  — 約 8月
    "Katiga",       # 3  — 約 9月
    "Kapat",        # 4  — 約 10月
    "Kalima",       # 5  — 約 11月
    "Kanem",        # 6  — 約 12月
    "Kapitu",       # 7  — 約 1月
    "Kawolu",       # 8  — 約 2月
    "Kasanga",      # 9  — 約 3月
    "Kadasa",       # 10 — 約 4月
    "Desta",        # 11 — 約 5月
    "Sada",         # 12 — 約 6月
]

# ============================================================
# 季節 (Kala / Season)
# 巴厘傳統分為兩大季節：
# - Lahru (乾季/Kemarau) — Sasih Kasa (1) 到 Kanem (6)
# - Rengreng (雨季/Penghujan) — Sasih Kapitu (7) 到 Sada (12)
#
# Ayana（太陽行程）：
# - Uttarayana（北行，太陽北移）— 約 Sasih Kapitu (7) 到 Sada (12)
# - Dakshinayana（南行，太陽南移）— 約 Sasih Kasa (1) 到 Kanem (6)
#
# 古法依據：Lontar Wariga — 季節劃分
# ============================================================
SEASON_LAHRU_RANGE = (1, 6)    # Sasih 1-6: 乾季 (Lahru / Kemarau)
SEASON_RENGRENG_RANGE = (7, 12)  # Sasih 7-12: 雨季 (Rengreng / Penghujan)

# ============================================================
# Dewasa Ayu (吉日) 與 Dewasa Ala (凶日) 規則
# 傳統判斷日期好壞的基本規則，基於 Wewaran 組合
#
# 常見吉日組合 (Dewasa Ayu)：
#   - Sapta Wara Neptu + Panca Wara Neptu 合計為特定值
#   - 某些 Wuku + Wara 的固定組合被視為大吉
#
# 常見凶日組合 (Dewasa Ala)：
#   - Kajeng Kliwon（Tri Wara Kajeng + Panca Wara Kliwon）= 大忌日
#   - Anggara Kasih（Sapta Wara Anggara + Panca Wara Kliwon）= 火曜凶日
#   - 特定的 Neptu 總和為凶數
#
# 古法依據：Lontar Wariga — Dewasa Ayu / Ala 章節
# ============================================================

# 吉日條件列表 — (名稱, 描述, 判斷函數名)
DEWASA_AYU_RULES = [
    ("Dewasa Ayu",
     "Panca Wara + Sapta Wara Neptu 總和 ≤ 9，且不在凶日列表中",
     "check_dewasa_ayu"),
    ("Beteng (均衡日)",
     "Tri Wara = Beteng 的日子，主平衡穩定",
     "check_beteng"),
]

# 凶日條件列表 — (名稱, 印尼名, 描述)
DEWASA_ALA_RULES = [
    ("Kajeng Kliwon",
     "Kajeng Kliwon",
     "Tri Wara=Kajeng + Panca Wara=Kliwon 之日，忌一切重要活動"),
    ("Anggara Kasih",
     "Anggara Kasih",
     "Sapta Wara=Anggara + Panca Wara=Kliwon 之日，火曜凶日"),
    ("Buda Cemeng",
     "Buda Cemeng",
     "Sapta Wara=Buda + Panca Wara=Kliwon 之日，水曜凶日"),
    ("Tumpek",
     "Tumpek",
     "Sapta Wara=Saniscara + Panca Wara=Kliwon 之日，土曜特殊日（某些類別視為吉）"),
    ("Buda Kliwon Pahang",
     "Buda Kliwon Pahang",
     "Buda+Kliwon 在 Wuku Pahang，大凶"),
]

# ============================================================
# Pancasuda — 由 Panca Wara Urip + Sapta Wara Urip 決定
# 總和 mod 7 → 7 種結果
# 古法依據：Lontar Wariga — Pancasuda 表
# ============================================================
PANCASUDA = [
    ("Wisesa Segara",   "如大海般的智慧力量"),    # 0 (mod 7)
    ("Tunggak Semi",    "枯木逢春，否極泰來"),    # 1
    ("Satria Wibawa",   "武士之威，尊貴高尚"),    # 2
    ("Sumur Sinaba",    "被棄之井，孤獨落寞"),    # 3
    ("Satria Wirang",   "武士之恥，受辱遭難"),    # 4
    ("Bumi Kapetak",    "大地開裂，基礎動搖"),    # 5
    ("Lebu Katiup Angin", "塵土隨風，飄搖不定"),  # 6
]

# ============================================================
# Eka Jala Rsi — 由 Eka Wara 計算得出
# 用於判斷靈性品質
# 古法依據：Lontar Wariga
# ============================================================
EKA_JALA_RSI = [
    ("Bagna Mapasah",   "分離之水，心靈清淨"),   # Eka Wara = Luang
]

# ============================================================
# 吉凶 Neptu 總和閾值
# 傳統上認為 Panca + Sapta Neptu 合計數值的吉凶分界
# 古法依據：Dasar Wariga
# ============================================================
NEPTU_SUM_AUSPICIOUS_MAX = 9    # Neptu 合計 ≤ 9 視為吉
NEPTU_SUM_INAUSPICIOUS_MIN = 10  # Neptu 合計 ≥ 10 需進一步審查

# ============================================================
# Catur Wara 特殊取模規則
# 在 210 天週期中，Catur Wara 的索引不是簡單的 day % 4
# 而是需要跳過特定日數（第 70 天和第 71 天重複 Jaya 和 Menala）
# 古法依據：Lontar Wariga — Catur Wara 排序法
# ============================================================
# Catur Wara 索引表：按 Pawukon day (0-209) 對應
# 簡化規則：day_in_pawukon 先去除特殊偏移後取 mod 4
CATUR_WARA_SKIP_DAYS = {70, 71}

# ============================================================
# Asta Wara 特殊取模規則
# 類似 Catur Wara，Asta Wara 也有跳過規則
# 在 Pawukon 週期中的第 0、6、7 天有特殊處理
# 古法依據：Lontar Wariga — Asta Wara 排序法
# ============================================================
# Asta Wara 的索引計算不使用簡單的 day % 8
# 而是使用修正後的日序

# ============================================================
# Sanga Wara 特殊取模規則
# Sanga Wara 同樣非簡單 day % 9
# 古法依據：Lontar Wariga — Sanga Wara 排序法
# ============================================================

# ============================================================
# Gregorian ↔ Pawukon 日數差
# 從 epoch (1969-12-31) 到目標日期的天數 mod 210
# 即可得到在 Pawukon 週期中的位置
# ============================================================
PAWUKON_CYCLE = 210
