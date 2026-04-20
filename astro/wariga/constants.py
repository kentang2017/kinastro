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

# ============================================================
# Panca Dauh — 5 時辰劃分（每 Dauh 約 4.8 小時）
# 巴厘傳統將一日分為 5 個 Dauh，每 Dauh 歸屬特定神明
# 格式：(名稱, 起始小時(含), 終止小時(不含), 神明/主宰, 吉凶, 說明)
# 範圍使用半開區間 [start, end)，無邊界重疊
# 古法依據：Lontar Wariga — Panca Dauh 時辰表
# ============================================================
PANCA_DAUH = [
    ("Pagi",       0,   6,  "Dewa Surya",    "中性", "日出前，萬物甦醒"),
    ("Tengai",     6,  11,  "Dewa Brahma",   "吉",   "上午，創造之時"),
    ("Tangeh",    11,  16,  "Dewa Wisnu",    "吉",   "正午，維護之時"),
    ("Sandikala", 16,  20,  "Dewa Siwa",     "凶",   "黃昏，轉化之時"),
    ("Wengi",     20,  24,  "Dewa Yama",     "凶",   "夜間，靜思之時"),
]

# ============================================================
# Asta Dauh — 8 時辰劃分（每 Dauh 3 小時）
# 更精細的時辰系統，嚴格按照 Lontar Wariga Gemet 傳統
# 格式：(名稱, 起始小時(含), 終止小時(不含), 方位, 吉凶, 說明)
# 範圍使用半開區間 [start, end)，無邊界重疊
# 古法依據：Lontar Wariga Gemet — Asta Dauh 時辰劃分
# ============================================================
ASTA_DAUH = [
    ("Pagi",        0,  3,  "Timur",        "中性",  "黎明前，Dewa Iswara 方，宜靜修"),
    ("Kala Pagi",   3,  6,  "Tenggara",     "凶",    "Dewa Maheswara 方，忌出行"),
    ("Tengai",      6,  9,  "Selatan",      "吉",    "Dewa Brahma 方，宜開始重要事"),
    ("Kala Tengai", 9, 12,  "Barat Daya",   "凶",    "Dewa Rudra 方，忌簽約"),
    ("Tangeh",     12, 15,  "Barat",        "吉",    "Dewa Mahadewa 方，宜農耕"),
    ("Kala Tangeh",15, 18,  "Barat Laut",   "凶",    "Dewa Sangkara 方，忌動土"),
    ("Sandikala",  18, 21,  "Utara",        "中性",  "Dewa Wisnu 方，宜祭祀"),
    ("Wengi",      21, 24,  "Timur Laut",   "凶",    "Dewa Sambu 方，宜休息"),
]

# ============================================================
# Penanggal — 月盈期 (1-15)，從新月到滿月
# 格式：(序號, 巴厘名稱, 梵語名, Neptu/Urip)
# 古法依據：Lontar Wariga — Penanggal 數值表
# ============================================================
PENANGGAL_NAMES = [
    (1,  "Penanggal Ping Pisan",   "Pratipada",  5),
    (2,  "Penanggal Ping Dua",     "Dvitiya",    4),
    (3,  "Penanggal Ping Tiga",    "Tritiya",    3),
    (4,  "Penanggal Ping Empat",   "Caturthi",   7),
    (5,  "Penanggal Ping Lima",    "Pancami",    1),
    (6,  "Penanggal Ping Enam",    "Sashti",     8),
    (7,  "Penanggal Ping Pitu",    "Saptami",    9),
    (8,  "Penanggal Ping Wolu",    "Ashtami",    6),
    (9,  "Penanggal Ping Songo",   "Navami",     5),
    (10, "Penanggal Ping Dasa",    "Dashami",    4),
    (11, "Penanggal Ping Sewelas", "Ekadashi",   3),
    (12, "Penanggal Ping Rolas",   "Dvadashi",   7),
    (13, "Penanggal Ping Telulas", "Trayodashi", 1),
    (14, "Penanggal Ping Pat Blas","Caturdashi", 8),
    (15, "Penanggal Ping Limolas", "Purnama",    9),
]

# ============================================================
# Panglong — 月虧期 (1-15)，從滿月到新月
# 格式：(序號, 巴厘名稱, 梵語名, Neptu/Urip)
# 古法依據：Lontar Wariga — Panglong 數值表
# ============================================================
PANGLONG_NAMES = [
    (1,  "Panglong Ping Pisan",    "Pratipada",  5),
    (2,  "Panglong Ping Dua",      "Dvitiya",    4),
    (3,  "Panglong Ping Tiga",     "Tritiya",    3),
    (4,  "Panglong Ping Empat",    "Caturthi",   7),
    (5,  "Panglong Ping Lima",     "Pancami",    1),
    (6,  "Panglong Ping Enam",     "Sashti",     8),
    (7,  "Panglong Ping Pitu",     "Saptami",    9),
    (8,  "Panglong Ping Wolu",     "Ashtami",    6),
    (9,  "Panglong Ping Songo",    "Navami",     5),
    (10, "Panglong Ping Dasa",     "Dashami",    4),
    (11, "Panglong Ping Sewelas",  "Ekadashi",   3),
    (12, "Panglong Ping Rolas",    "Dvadashi",   7),
    (13, "Panglong Ping Telulas",  "Trayodashi", 1),
    (14, "Panglong Ping Pat Blas", "Caturdashi", 8),
    (15, "Panglong Ping Limolas",  "Tilem",      9),
]

# ============================================================
# 特殊聖日 — Purnama（滿月）與 Tilem（新月）
# 古法依據：Lontar Wariga — 月相聖日
# ============================================================
PURNAMA_TILEM = {
    "Purnama": "滿月聖日（Penanggal 15），宜祈福祭神",
    "Tilem":   "新月聖日（Panglong 15），宜靜修內觀",
}

# ============================================================
# Wuku 符號對應 — 用於傳統視覺呈現
# 格式：(Wuku名稱, 方位神, 顏色, 動物象徵, 吉凶傾向)
# 古法依據：Palalintangan 傳統對應表
# ============================================================
WUKU_ATTRIBUTES = [
    ("Sinta",        "Timur",     "#FF6B6B", "獅子", "大吉"),
    ("Landep",       "Tenggara",  "#4ECDC4", "鹿",   "吉"),
    ("Ukir",         "Selatan",   "#FFE66D", "牛",   "吉"),
    ("Kulantir",     "Barat Daya","#A8E6CF", "孔雀", "中"),
    ("Tolu",         "Barat",     "#FF8B94", "蛇",   "中"),
    ("Gumbreg",      "Barat Laut","#C3A6FF", "象",   "吉"),
    ("Wariga",       "Utara",     "#85E89D", "猴",   "吉"),
    ("Warigadian",   "Timur Laut","#FFC3A0", "鳥",   "中"),
    ("Julungwangi",  "Timur",     "#FF6B6B", "龜",   "大吉"),
    ("Sungsang",     "Tenggara",  "#4ECDC4", "魚",   "凶"),
    ("Dungulan",     "Selatan",   "#FFE66D", "豬",   "中"),
    ("Kuningan",     "Barat Daya","#A8E6CF", "鳳凰", "大吉"),
    ("Langkir",      "Barat",     "#FF8B94", "牛",   "凶"),
    ("Medangsia",    "Barat Laut","#C3A6FF", "鱷魚", "凶"),
    ("Pujut",        "Utara",     "#85E89D", "獅子", "吉"),
    ("Pahang",       "Timur Laut","#FFC3A0", "蜈蚣", "凶"),
    ("Krulut",       "Timur",     "#FF6B6B", "蜘蛛", "凶"),
    ("Merakih",      "Tenggara",  "#4ECDC4", "犀牛", "中"),
    ("Tambir",       "Selatan",   "#FFE66D", "象",   "吉"),
    ("Medangkungan", "Barat Daya","#A8E6CF", "蜜蜂", "吉"),
    ("Matal",        "Barat",     "#FF8B94", "牛",   "中"),
    ("Uye",          "Barat Laut","#C3A6FF", "蝴蝶", "吉"),
    ("Menail",       "Utara",     "#85E89D", "鷹",   "中"),
    ("Prangbakat",   "Timur Laut","#FFC3A0", "蝙蝠", "凶"),
    ("Bala",         "Timur",     "#FF6B6B", "虎",   "凶"),
    ("Ugu",          "Tenggara",  "#4ECDC4", "鸚鵡", "中"),
    ("Wayang",       "Selatan",   "#FFE66D", "猴",   "吉"),
    ("Klawu",        "Barat Daya","#A8E6CF", "蛙",   "中"),
    ("Dukut",        "Barat",     "#FF8B94", "蚯蚓", "凶"),
    ("Watugunung",   "Barat Laut","#C3A6FF", "龍",   "大吉"),
]

# ============================================================
# 完整 Ala Ayuning Dewasa 規則表
# 嚴格依照 Lontar Wariga Dewasa 的傳統吉凶組合
# 格式：(名稱, 觸發條件說明, 吉/凶, Lontar古法描述)
# 古法依據：Lontar Wariga Dewasa
# ============================================================
ALA_AYUNING_DEWASA = [
    # === 吉日 (Dewasa Ayu) ===
    ("Hari Raya Galungan",
     "Wuku Dungulan，Sapta Wara=Buda，Panca Wara=Kliwon",
     "大吉", "天神降臨人間之聖日，宜祭典慶祝"),
    ("Hari Raya Kuningan",
     "Wuku Kuningan，Sapta Wara=Saniscara，Panca Wara=Kliwon",
     "大吉", "天神返回天界前最後護佑之日，宜獻供"),
    ("Sugihan Bali",
     "Wuku Sungsang，Sapta Wara=Saniscara",
     "吉", "淨化巴厘島大地之日，宜清掃祭所"),
    ("Sugihan Jawa",
     "Wuku Sungsang，Sapta Wara=Wraspati",
     "吉", "淨化自身靈魂之日，宜沐浴冥想"),
    ("Purnama",
     "月相=滿月（Penanggal 15）",
     "大吉", "滿月聖日，宜祈福禱告，忌不潔之事"),
    ("Buda Cemeng Klawu",
     "Wuku Klawu，Sapta Wara=Buda，Panca Wara=Kliwon",
     "吉", "依 Lontar Wariga，此日宜靜心修行"),
    ("Tumpek Landep",
     "Wuku Landep，Sapta Wara=Saniscara，Panca Wara=Kliwon",
     "吉", "祝福器具、武器之日，宜磨刀器"),
    ("Tumpek Uduh",
     "Wuku Wariga，Sapta Wara=Saniscara，Panca Wara=Kliwon",
     "吉", "祝福植物、農作之日，宜種植"),
    ("Tumpek Kuningan",
     "Wuku Kuningan，Sapta Wara=Saniscara，Panca Wara=Kliwon",
     "大吉", "祖靈降臨之日，宜祭拜先祖"),
    ("Tumpek Krulut",
     "Wuku Krulut，Sapta Wara=Saniscara，Panca Wara=Kliwon",
     "吉", "祝福音樂藝術之日，宜演奏歌詠"),
    ("Tumpek Kandang",
     "Wuku Uye，Sapta Wara=Saniscara，Panca Wara=Kliwon",
     "吉", "祝福牲畜家禽之日，宜照料動物"),
    ("Tumpek Wayang",
     "Wuku Wayang，Sapta Wara=Saniscara，Panca Wara=Kliwon",
     "吉", "祝福皮影藝術之日，宜觀賞 Wayang"),
    # === 凶日 (Dewasa Ala) ===
    ("Kajeng Kliwon",
     "Tri Wara=Kajeng + Panca Wara=Kliwon",
     "凶", "傳統大忌日，惡靈出沒，忌一切重要活動"),
    ("Anggara Kasih",
     "Sapta Wara=Anggara + Panca Wara=Kliwon",
     "凶", "火曜凶日，忌重大決定、訴訟、出行"),
    ("Buda Cemeng",
     "Sapta Wara=Buda + Panca Wara=Kliwon（非 Wuku Klawu）",
     "凶", "水曜凶日，宜謹慎行事，忌簽約"),
    ("Tilem",
     "月相=新月（Panglong 15）",
     "凶", "新月聖日，靈界活躍，忌出行冒險"),
    ("Buda Kliwon Pahang",
     "Wuku Pahang，Sapta Wara=Buda，Panca Wara=Kliwon",
     "大凶", "Lontar 記載最凶之日，萬事皆忌"),
    ("Manis Galungan",
     "Wuku Dungulan，Sapta Wara=Kamis（Wraspati）",
     "中", "Galungan 翌日，宜訪問親友"),
    ("Penampahan Galungan",
     "Wuku Dungulan，Sapta Wara=Anggara",
     "中", "Galungan 前一日，宜準備祭品"),
]

# ============================================================
# Dewasa Ayu 詳細說明 — 各 Wewaran 組合的吉日描述
# 格式：(分類, 傳統活動描述)
# 古法依據：Lontar Wariga Dewasa — 宜事章節
# ============================================================
DEWASA_AYU_ACTIVITIES = {
    "pernikahan":  ("宜婚嫁", "Pahing Umanis、Sukra Umanis、Soma Umanis 為婚嫁吉日"),
    "perniagaan":  ("宜經商", "Wraspati Pon 為最宜開業之日"),
    "pertanian":   ("宜農耕", "Redite Wage 宜播種，Soma Pon 宜收割"),
    "pembangunan": ("宜建築", "Buda Kliwon Sinta 宜動土，Wraspati Pahing 宜上梁"),
    "perjalanan":  ("宜出行", "Sukra Umanis 宜長途旅行"),
    "pengobatan":  ("宜醫療", "Soma Kliwon 宜開始治療"),
}

# ============================================================
# Pangider-ider — 八方位神明（風向玫瑰）
# 巴厘傳統九宮格方位體系，中央 + 八方
# 古法依據：Lontar Wariga — Nawa Sanga（九聖）
# ============================================================
PANGIDER_IDER = {
    "Timur":      ("Dewa Iswara",   "白色", "besi",   "♁"),
    "Tenggara":   ("Dewa Maheswara","pink",  "perak",  "☽"),
    "Selatan":    ("Dewa Brahma",   "Merah", "tembaga","☀"),
    "Barat Daya": ("Dewa Rudra",    "Jingga","besi",   "♂"),
    "Barat":      ("Dewa Mahadewa", "Kuning","emas",   "♃"),
    "Barat Laut": ("Dewa Sangkara", "Hijau", "besi",   "♄"),
    "Utara":      ("Dewa Wisnu",    "Hitam", "besi",   "♆"),
    "Timur Laut": ("Dewa Sambu",    "Biru",  "besi",   "♅"),
    "Tengah":     ("Dewa Siwa",     "Pancawarna","emas","☯"),
}
