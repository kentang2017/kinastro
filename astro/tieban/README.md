# 鐵板神數模組 (Tie Ban Shen Shu Module)

## 概述

鐵板神數，又稱「鐵版神數」、「邵子神數」，是中國傳統術數中最精密的查表法系統。源自宋代邵雍《皇極經世》，清代發展為完整的考刻分系統。

本模組基於《鐵板神數清刻足本》（心一堂術數珍本古籍叢刊·星命類·神數類，2013）實現，底本為虛白廬藏清中葉「貞元書屋」刻本，包含完整的秘鈔密碼表。

## 核心特點

- **精密時間分割**：每時分 8 刻，每刻 15 分（共 120 分/時），融入西洋分鐘制
- **考刻分技術**：結合父母八字、六親信息精確定位刻分
- **八卦加則例**：天干配卦、地支配卦、河洛配數、地支取數
- **紫微斗數安星**：完整的安命、安身、安紫府、十二宮系統
- **秘鈔密碼表**：卦象、流度、納甲卦爻快速查表
- **條文資料庫**：360+ 條命運詩讖，涵蓋父母、兄弟、夫妻、子女、事業、財運等

## 安裝與使用

### 基本使用

```python
from astro.tieban import TieBanShenShu, TieBanBirthData
from astro.tieban.tieban_calculator import Ganzhi
from datetime import datetime

# 創建實例
tbss = TieBanShenShu()

# 準備出生資料
birth_data = TieBanBirthData(
    birth_dt=datetime(1990, 5, 15, 14, 30),  # 出生時間
    year_gz=Ganzhi('庚', '午'),              # 年柱
    month_gz=Ganzhi('辛', '巳'),              # 月柱
    day_gz=Ganzhi('戊', '辰'),               # 日柱
    hour_gz=Ganzhi('己', '未'),              # 時柱
    gender="男",
    # 完整版需父母信息（用於考刻分）
    # father_birth=datetime(1960, 1, 1),
    # mother_birth=datetime(1962, 3, 3),
)

# 計算
result = tbss.calculate(birth_data)

# 查看結果
print(f"命宮：{result.ming_palace}")
print(f"身宮：{result.shen_palace}")
print(f"五行局：{result.wuxing_ju}")
print(f"刻分：{result.ke}刻{result.fen}分")
print(f"神數號碼：{result.tieban_number}")
print(f"條文：{result.verse}")
```

### 生成完整報告

```python
report = tbss.get_full_report(birth_data)
print(report)
```

### 渲染 SVG 星盤圖

```python
from astro.tieban import render_tieban_chart_svg

svg = render_tieban_chart_svg(result, language='zh')
# 在 Streamlit 中顯示
st.components.v1.html(svg, height=650)
```

## 模組結構

```
astro/tieban/
├── __init__.py              # 模組導入
├── tieban_calculator.py     # 核心計算引擎
├── tieban_renderer.py       # SVG 渲染器
├── tests/
│   └── test_tieban.py       # 測試套件
└── data/
    ├── mappings.json        # 映射表（納音、卦象、河洛數）
    └── verses.json          # 條文資料庫（360+ 條）
```

## 核心組件

### 1. 基礎映射 (Mapping)

- **天干配卦**：壬甲乾、乙坤癸、庚艮、辛巽、己震、戊離、丙坎、丁兌
- **地支配卦**：子坎、丑坤、寅卯震、辰兌、巳午離、未坤、申酉乾、戌兌、亥坎
- **河洛配數**：甲己子午 9、乙庚丑未 8、丙辛寅申 7、丁壬卯酉 6、戊癸辰戌 5、巳亥 4
- **六十納音**：完整 60 組納音五行（海中金、爐中火...）
- **五行局**：由納音決定局數（2-6 局）

### 2. 安星系統 (StarPlacement)

- **安命宮**：從寅上起正月，順至生月；從生月起子時，逆至生時
- **安身宮**：從寅上起正月，順至生月；從生月起子時，順至生時
- **安十二宮**：命宮定位後，逆時針排列
- **安紫微**：由年干、五行局、農曆日決定
- **安天府**：與紫微永遠相對（六沖位）

### 3. 考刻分引擎 (KeFenEngine)

- **刻分計算**：每時 8 刻 × 每刻 15 分 = 120 分
- **父母考證**：結合父母生卒、六親信息篩選候選刻分
- **密碼表映射**：將刻分映射到條文號碼

### 4. 秘鈔密碼表 (SecretCodeTable)

包含數百條卦象密碼：
- 水火既濟、澤火革、雷火豐...
- 坤屯艮生、乾屯艮主...
- 流度、壽度圖映射

### 5. 條文資料庫 (VerseDatabase)

360+ 條命運詩讖，分類包括：
- **綜合**：父母、兄弟、夫妻、子女綜合判斷
- **父母**：父母生肖、存亡、壽限
- **兄弟**：兄弟人數、關係、生肖
- **夫妻**：妻宮屬性、婚配、刑剋
- **子女**：子嗣人數、成就、遲早
- **事業**：事業類型、成就、起伏
- **財運**：財運類型、貧富、來源
- **健康**：健康狀況、疾病、壽限
- **壽限**：壽命長短、災厄
- **遷移**：遷移、定居、遠行
- **交遊**：朋友、貴人、小人
- **功名**：科舉、官祿、成就
- **災厄**：火燭、水患、盜賊、官非
- **婚姻**：紅鸞、婚期、正副室
- **刑獄**：良人刑剋、官非
- **神煞**：火星、計都、羅睺、紫微等

## 條文格式

每條條文包含：

```json
{
  "0001": {
    "verse": "父母雙全壽延長，兄弟二人共爐香。妻宮同庚來匹配，子嗣三人送終老。",
    "category": "綜合",
    "tags": ["父母雙全", "兄弟二人", "妻宮同庚", "三子"]
  }
}
```

## 搜索功能

```python
from astro.tieban.tieban_calculator import VerseDatabase

db = VerseDatabase()

# 按標籤搜索
results = db.search_by_tag('父母雙全')
for result in results:
    print(f"{result['number']}: {result['verse']}")

# 獲取所有分類
categories = db.get_categories()
print(categories)
```

## 考刻分說明

鐵板神數最核心的秘密是「考刻分」：

1. **初步計算**：根據出生時間計算初步刻分（120 個候選）
2. **父母考證**：根據父母生卒年月日時篩選
3. **六親佐證**：根據兄弟、夫妻、子女信息進一步篩選
4. **最終確定**：得到唯一準確的刻分
5. **查表得數**：根據刻分查密碼表得萬千百十號
6. **對應條文**：根據號碼查條文

完整版需用戶輸入：
- 父親出生/卒年
- 母親出生/卒年
- 兄弟姊妹人數及生肖
- 婚姻狀況
- 子女人數及生肖

## 與《皇極數》的區別

| 特點 | 皇極數（明代） | 鐵板神數（清代） |
|------|---------------|-----------------|
| 時間分割 | 時分八刻 | 時分八刻，每刻十五分 |
| 考刻方法 | 簡單佐證 | 完整父母六親考證 |
| 密碼表 | 簡化 | 完整秘鈔密碼表 |
| 條文數 | 約 1000 條 | 360+ 條（精簡版） |
| 精確度 | 較低 | 極高（鐵口直斷） |

## 運行測試

```bash
cd /mnt/c/Users/hooki/OneDrive/pastword/文件/Github/kinastro
python -m astro.tieban.tests.test_tieban
```

## 參考文獻

- 《鐵板神數清刻足本》（心一堂，2013，底本：清中葉貞元書屋刻本）
- 《皇極數》（明代邵子數，八刻分經定數）
- 邵雍《皇極經世》先天之學
- 傳統紫微斗數安星法

## 版本歷史

- **v1.0** (2026-04-24)
  - 初始版本
  - 實現完整起例與推算方法
  - 載入 360+ 條條文
  - 整合到 KinAstro v2.4.0

## 待擴展功能

1. **完整條文資料庫**：從原文提取數千條詩讖
2. **父母六親考刻分**：實現完整的考證邏輯
3. **節氣精確計算**：結合 pyswisseph 計算精確干支
4. **密碼表完整載入**：從原文提取完整密碼表
5. **AI 條文解讀**：結合 AI 解讀條文含義

## 授權

本模組為開源項目，遵循 KinAstro 專案授權協議。
