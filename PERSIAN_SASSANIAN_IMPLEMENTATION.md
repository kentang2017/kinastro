# 波斯薩珊占星系統實現總結

## 概述

已成功為 KinAstro 添加完整的波斯薩珊王朝占星系統（Sassanian Astrology, 224–651 CE），這是第 32 個占星系統。

## 實現的功能

### 1. 核心模組 (`astro/persian/sassanian_astrology.py`)

#### 主要函數
- `compute_sassanian_chart()` - 計算完整的薩珊占星星盤
- `calculate_firdar()` - Firdar 生命週期計算
- `calculate_hyleg_alcocoden()` - Hyleg & Alcocoden 壽命推算
- `calculate_profections()` - 波斯式年度主限
- `calculate_almuten_figuris()` - Almuten Figuris（命主星）計算
- `get_royal_stars_prominence()` - 皇家恆星顯著度
- `calculate_persian_lots()` - 波斯敏感點計算

#### 資料類別
- `SassanianChart` - 薩珊星盤
- `SassanianPlanet` - 行星位置
- `FirdarPeriod` / `FirdarSubPeriod` - Firdar 週期
- `HylegResult` / `AlcocodenResult` - Hyleg & Alcocoden
- `ProfectionYear` - 年度主限
- `AlmutenFiguris` - 命主星
- `RoyalStarProminence` - 皇家恆星
- `PersianLot` - 波斯敏感點

### 2. 核心技術實現

#### Firdar / Firdaria（行星生命週期）
- **白天出生**：Sun → Moon → Saturn → Jupiter → Mars → Venus → Mercury
- **夜晚出生**：Moon → Saturn → Jupiter → Mars → Sun → Venus → Mercury
- 每個主要週期再細分為 7 個子週期
- 自動計算當前的 Firdar 和子週期

#### Hyleg & Alcocoden（生命給予者與壽命給予者）
- Hyleg 判斷規則：
  1. 太陽（白天）/ 月亮（夜晚）- 如果在 1, 5, 7, 9, 10, 11 宮
  2. 幸運點 - 如果在上述宮位
  3. 上升點（預設）
- Alcocoden 根據 Hyleg 位置的尊嚴計算
- 相位修正：吉星增加年數，凶星減少年數

#### 波斯式年度主限
- 每年移動 30°（基於度數，非星座）
- 從上升點開始連續計算
- 與希臘占星的星座主限不同

#### Almuten Figuris（命主星）
- 計算關鍵點（上升、天頂、日月、幸運點）的尊嚴總分
- 尊嚴系統：Domicile (5 分), Exaltation (4 分), Triplicity (3 分), Term (2 分)

#### 四顆皇家恆星
- Aldebaran（畢宿五）~ 9° Gemini
- Regulus（軒轅十四）~ 29° Leo
- Antares（心宿二）~ 9° Sagittarius
- Fomalhaut（北落師門）~ 19° Pisces
- 容許度 3°以內的合相視為顯著

#### 波斯敏感點
- Part of Fortune（幸運點）
- Part of Spirit（精神點）
- 日夜盤公式不同

### 3. UI 整合 (`app.py`)

#### Sidebar 配置
- 分類：`cat_middle_east`（中東占星）
- 順序：Persian → Arabic → Yemeni
- 標籤：🔯 波斯傳統占星

#### 頁面 Tabs
1. **本命盤概覽** - 行星位置表、當前 Firdar
2. **📅 Firdar 生命週期** - 時間軸視圖、子週期詳情
3. **🌟 Hyleg & Alcocoden** - 生命力與壽命推算
4. **🔄 年度主限** - 前 30 年的主限運勢
5. **👑 Almuten Figuris** - 命主星與尊嚴分數
6. **⭐ 皇家恆星** - 四顆皇家恆星的合相
7. **📍 波斯敏感點** - 幸運點、精神點等

### 4. 國際化 (`astro/i18n.py`)

新增 18 個翻譯鍵（繁中/簡中/英文）：
- `tab_persian` - 系統標籤
- `sys_hint_persian` - 系統提示
- `desc_persian` - 詳細描述
- `persian_firdar_title` / `persian_firdar_help`
- `persian_hyleg_title` / `persian_hyleg_help`
- `persian_profections_title`
- `persian_almuten_title`
- `persian_royal_stars_title`
- `persian_lots_title`
- `persian_current_firdar` / `persian_current_sub`
- `persian_hyleg_label` / `persian_alcocoden_label`
- `persian_planetary_years` / `persian_modified_years`
- `persian_aspects` / `persian_dignity_score`
- `persian_no_prominent_stars`
- `spinner_persian`

### 5. 測試套件 (`tests/test_persian_sassanian.py`)

#### 測試案例
1. **白天出生** - 1990 年 7 月 15 日 12:00 台北
2. **夜晚出生** - 1990 年 1 月 15 日 02:00 台北
3. **Firdar 計算** - 驗證日夜盤起始順序
4. **年度主限** - 驗證每年 30°移動
5. **皇家恆星** - 驗證合相計算

#### 測試覆蓋
- 基本星盤計算
- Firdar 週期與子週期
- Hyleg & Alcocoden
- Almuten Figuris
- Profections
- Royal Stars
- Persian Lots

## 使用方式

### 1. 啟動應用
```bash
cd /mnt/c/Users/hooki/OneDrive/pastword/文件/Github/kinastro
streamlit run app.py
```

### 2. 使用波斯薩珊占星
1. 在 sidebar 選擇 **🌐 占星體系**
2. 展開 **🕌 中東占星** 分類
3. 點擊 **🔯 波斯傳統占星**
4. 輸入出生資料並計算
5. 瀏覽 7 個功能 tabs

### 3. 運行測試
```bash
python3 tests/test_persian_sassanian.py
```

## 技術細節

### 日夜判斷
- 基於太陽宮位（非鐘錶時間）
- 第 7-12 宮 = 白天（地平線以上）
- 第 1-6 宮 = 夜晚（地平線以下）

### 尊嚴系統
- **Domicile (廟)** - 5 分
- **Exaltation (旺)** - 4 分
- **Triplicity (三分)** - 3 分（日夜不同）
- **Term (界)** - 2 分

### 行星年數（Alcocoden）
- Sun: 19, Moon: 25, Saturn: 43
- Jupiter: 79, Mars: 66, Venus: 82, Mercury: 76

### 相位修正
- 合相（0°）：吉星 +20%，凶星 -20%
- 三分相（120°）：吉星 +15%
- 六分相（60°）：吉星 +10%
- 四分相（90°）：凶星 -10%
- 對分相（180°）：凶星 -15%

## 檔案清單

```
astro/persian/
├── __init__.py                    # 模組入口
└── sassanian_astrology.py         # 核心模組（1324 行）

tests/
└── test_persian_sassanian.py      # 測試套件（280 行）

astro/
└── i18n.py                        # 新增 18 個翻譯鍵

app.py                             # 新增波斯占星 UI（200 行）
```

## 歷史參考

實現基於以下古典文獻：
- **Umar al-Tabari** (8 世紀) — 《Kitab al-Qirat fi Ilm al-Nujum》
- **Masha'allah ibn Athari** (8-9 世紀) — 《On Reception》
- **Abu Ma'shar al-Balkhi** (9 世紀) — 《Introductorium in Astronomiam》
- **薩珊王朝占星文献** (5-7 世紀)

## 與其他系統的區別

### vs 阿拉伯占星
- 波斯薩珊是獨立體系，非阿拉伯占星的子集
- Firdar 技術是薩珊獨創
- 尊嚴規則有所不同
- 皇家恆星的使用更突出

### vs 希臘占星
- 年度主限使用度數移動（30°/年），非星座跳躍
- Hyleg 判斷規則更嚴格
- Alcocoden 計算更詳細

## 未來擴展建議

1. **更多波斯敏感點** - 愛情點、勇氣點、勝利點等
2. **Zodiacal Releasing** - 另一種薩珊時間主限技術
3. **Solar Return** - 波斯式返照星盤
4. **Mundane Astrology** - 世俗占星應用
5. **Rectification** - 生時校正技術

## 注意事項

- 使用熱帶黃道（Tropical Zodiac）
- 宮位制：Placidus
- 星曆表：Swiss Ephemeris
- 語言支援：繁體中文、簡體中文、英文

## 總結

波斯薩珊占星系統已成功整合到 KinAstro，提供完整的古典占星技法，包括獨特的 Firdar 生命週期、Hyleg/Alcocoden 壽命推算、波斯式年度主限等。所有核心功能均已測試通過，UI 整合完整，支援多語言。

此實現嚴格遵循古典文獻，同時保持與現代占星軟體的相容性。
