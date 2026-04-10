"""
七政四餘神煞計算模組 (Shen Sha / Divine Stars Module)

根據年柱、月柱、日柱、時柱的天干地支，推算各種神煞，
將其分配到十二宮（地支）以便在排盤圖中顯示。

神煞分類：
  - 年支系（以年支為基準推算）
  - 日支系（以日支為基準推算）
  - 年干系（以年干為基準推算）
  - 月支系（以月支為基準推算）
"""

from dataclasses import dataclass, field

# ============================================================
# 天干地支
# ============================================================
HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳",
                    "午", "未", "申", "酉", "戌", "亥"]


@dataclass
class ShenShaItem:
    """單個神煞"""
    name: str              # 神煞名稱
    branch: int            # 所在地支索引 (0-11)
    category: str          # 類別：吉 / 凶 / 中
    source: str            # 來源：年支 / 日支 / 年干 / 月支


@dataclass
class ShenShaResult:
    """神煞計算結果"""
    items: list = field(default_factory=list)         # List[ShenShaItem]
    branch_map: dict = field(default_factory=dict)    # branch_idx -> list of names


# ============================================================
# 年支系神煞查表
# 年支索引: 子=0, 丑=1, 寅=2, ..., 亥=11
# 值: 神煞所落入的地支索引
# ============================================================

# 天乙貴人 (以年干查) — 移至年干系
# 驛馬 (以年支查)
# 寅申巳亥為四驛馬, 申子辰→寅, 寅午戌→申, 巳酉丑→亥, 亥卯未→巳
YIMA = {0: 2, 1: 11, 2: 8, 3: 5, 4: 2, 5: 11, 6: 8, 7: 5, 8: 2, 9: 11, 10: 8, 11: 5}

# 桃花 (咸池, 以年支查)
# 申子辰→酉, 寅午戌→卯, 巳酉丑→午, 亥卯未→子
TAOHUA = {0: 9, 1: 6, 2: 3, 3: 0, 4: 9, 5: 6, 6: 3, 7: 0, 8: 9, 9: 6, 10: 3, 11: 0}

# 華蓋 (以年支查)
# 申子辰→辰, 寅午戌→戌, 巳酉丑→丑, 亥卯未→未
HUAGAI = {0: 4, 1: 1, 2: 10, 3: 7, 4: 4, 5: 1, 6: 10, 7: 7, 8: 4, 9: 1, 10: 10, 11: 7}

# 劫煞 (以年支查)
# 申子辰→巳, 寅午戌→亥, 巳酉丑→寅, 亥卯未→申
JIESHA = {0: 5, 1: 2, 2: 11, 3: 8, 4: 5, 5: 2, 6: 11, 7: 8, 8: 5, 9: 2, 10: 11, 11: 8}

# 亡神 (以年支查)
# 申子辰→亥, 寅午戌→巳, 巳酉丑→申, 亥卯未→寅
WANGSHEN = {0: 11, 1: 8, 2: 5, 3: 2, 4: 11, 5: 8, 6: 5, 7: 2, 8: 11, 9: 8, 10: 5, 11: 2}

# 天空 (以年支查)
# 子→丑, 丑→寅, 寅→卯, 卯→辰, 辰→巳, 巳→午,
# 午→未, 未→申, 申→酉, 酉→戌, 戌→亥, 亥→子
TIANKONG = {i: (i + 1) % 12 for i in range(12)}

# 孤辰 (以年支查)
# 亥子丑→寅, 寅卯辰→巳, 巳午未→申, 申酉戌→亥
GUCHEN = {0: 2, 1: 2, 2: 5, 3: 5, 4: 5, 5: 8, 6: 8, 7: 8, 8: 11, 9: 11, 10: 11, 11: 2}

# 寡宿 (以年支查)
# 亥子丑→戌, 寅卯辰→丑, 巳午未→辰, 申酉戌→未
GUASU = {0: 10, 1: 10, 2: 1, 3: 1, 4: 1, 5: 4, 6: 4, 7: 4, 8: 7, 9: 7, 10: 7, 11: 10}

# 月殺 (以年支查) — 歲破對沖
# 子→午, 丑→未, 寅→申, 卯→酉, 辰→戌, 巳→亥...
YUESHA = {i: (i + 6) % 12 for i in range(12)}

# 天哭 (以年支查)
# 子→午, 丑→巳, 寅→辰, ..., 亥→未 (逆推)
TIANKU = {0: 6, 1: 5, 2: 4, 3: 3, 4: 2, 5: 1, 6: 0, 7: 11, 8: 10, 9: 9, 10: 8, 11: 7}

# 天虛 (以年支查)
# 子→午+1, ... 天哭+1
TIANXU = {i: (TIANKU[i] + 2) % 12 for i in range(12)}

# 天狗 (以年支查)
# 子→戌, 丑→亥, 寅→子, ...
TIANGOU = {i: (10 + i) % 12 for i in range(12)}

# 弔客 (以年支查)
# 子→戌+2, = 子
DIAOKE = {i: (i + 2) % 12 for i in range(12)}

# 白虎 (以年支查)
# 子→申, ...
BAIHU = {i: (i + 8) % 12 for i in range(12)}

# ============================================================
# 年干系神煞
# 年干索引: 甲=0, 乙=1, 丙=2, 丁=3, 戊=4,
#           己=5, 庚=6, 辛=7, 壬=8, 癸=9
# ============================================================

# 天乙貴人 (以年干查, 有兩個位置)
# 甲→丑未, 乙→子申, 丙→亥酉, 丁→亥酉, 戊→丑未
# 己→子申, 庚→丑未, 辛→寅午, 壬→卯巳, 癸→卯巳
TIANYI_GUIREN = {
    0: [1, 7],    # 甲→丑,未
    1: [0, 8],    # 乙→子,申
    2: [11, 9],   # 丙→亥,酉
    3: [11, 9],   # 丁→亥,酉
    4: [1, 7],    # 戊→丑,未
    5: [0, 8],    # 己→子,申
    6: [1, 7],    # 庚→丑,未
    7: [2, 6],    # 辛→寅,午
    8: [3, 5],    # 壬→卯,巳
    9: [3, 5],    # 癸→卯,巳
}

# 文昌 (以年干查)
# 甲→巳, 乙→午, 丙→申, 丁→酉, 戊→申,
# 己→酉, 庚→亥, 辛→子, 壬→寅, 癸→卯
WENCHANG = {0: 5, 1: 6, 2: 8, 3: 9, 4: 8, 5: 9, 6: 11, 7: 0, 8: 2, 9: 3}

# 天德 (以月支查)
# 正月→丁, 二月→申, 三月→壬, 四月→辛, 五月→亥, 六月→甲,
# 七月→癸, 八月→寅, 九月→丙, 十月→乙, 十一月→巳, 十二月→庚
# 這裡存地支索引（天德本為天干/地支，簡化為落入的地支位置）
# 正月(寅月)=丁→未(7), 二月(卯月)=申(8), ...
# 簡化：天德以月支查（寅=2起），結果為地支索引
TIANDE_BY_MONTH = {
    2: 7, 3: 8, 4: 0, 5: 9, 6: 11, 7: 4,
    8: 3, 9: 2, 10: 5, 11: 1, 0: 5, 1: 6,
}

# 月德 (以月支查)
# 寅午戌月→丙(巳), 申子辰月→壬(亥), 巳酉丑月→庚(酉), 亥卯未月→甲(寅)
YUEDE_BY_MONTH = {
    2: 5, 6: 5, 10: 5,     # 寅午戌→巳(5)
    8: 11, 0: 11, 4: 11,   # 申子辰→亥(11)
    5: 9, 9: 9, 1: 9,      # 巳酉丑→酉(9)
    11: 2, 3: 2, 7: 2,     # 亥卯未→寅(2)
}

# 祿神 (以年干查)
# 甲→寅, 乙→卯, 丙→巳, 丁→午, 戊→巳, 己→午, 庚→申, 辛→酉, 壬→亥, 癸→子
LUSHEN = {0: 2, 1: 3, 2: 5, 3: 6, 4: 5, 5: 6, 6: 8, 7: 9, 8: 11, 9: 0}

# 羊刃 (以年干查): 祿+1
YANGREN = {k: (v + 1) % 12 for k, v in LUSHEN.items()}

# 天官 (以年干查)
# 甲→未, 乙→辰, 丙→巳, 丁→寅, 戊→卯, 己→子, 庚→丑, 辛→戌, 壬→亥, 癸→申
TIANGUAN = {0: 7, 1: 4, 2: 5, 3: 2, 4: 3, 5: 0, 6: 1, 7: 10, 8: 11, 9: 8}

# 天廚 (以年干查)
# 甲→巳, 乙→午, 丙→巳, 丁→未, 戊→巳, 己→午, 庚→申, 辛→未, 壬→申, 癸→酉
TIANCHU = {0: 5, 1: 6, 2: 5, 3: 7, 4: 5, 5: 6, 6: 8, 7: 7, 8: 8, 9: 9}

# ============================================================
# 日支系神煞
# ============================================================

# 天喜 (以日支查, 與年支同法)
# 子→酉, 丑→申, 寅→未, 卯→午, 辰→巳, 巳→辰,
# 午→卯, 未→寅, 申→丑, 酉→子, 戌→亥, 亥→戌
TIANXI = {i: (9 - i + 12) % 12 for i in range(12)}

# 紅鸞 (以年支查): 天喜對沖
# 子→卯, 丑→寅, 寅→丑, 卯→子, 辰→亥, 巳→戌,
# 午→酉, 未→申, 申→未, 酉→午, 戌→巳, 亥→辰
HONGLUAN = {i: (3 - i + 12) % 12 for i in range(12)}


# ============================================================
# 十二長生 (Twelve Stages of Life Cycle)
# 根據五行查年干對應長生起點，然後順/逆佈十二長生
# ============================================================
TWELVE_LIFE_STAGES = [
    "長生", "沐浴", "冠帶", "臨官", "帝旺", "衰",
    "病", "死", "墓", "絕", "胎", "養",
]

# 年干的長生起點（地支索引）及方向
# 陽干順行, 陰干逆行
# 甲→亥(11)順, 乙→午(6)逆, 丙→寅(2)順, 丁→酉(9)逆,
# 戊→寅(2)順, 己→酉(9)逆, 庚→巳(5)順, 辛→子(0)逆,
# 壬→申(8)順, 癸→卯(3)逆
CHANGSHENG_START = {
    0: (11, 1),   # 甲: 亥起, 順
    1: (6, -1),   # 乙: 午起, 逆
    2: (2, 1),    # 丙: 寅起, 順
    3: (9, -1),   # 丁: 酉起, 逆
    4: (2, 1),    # 戊: 寅起, 順
    5: (9, -1),   # 己: 酉起, 逆
    6: (5, 1),    # 庚: 巳起, 順
    7: (0, -1),   # 辛: 子起, 逆
    8: (8, 1),    # 壬: 申起, 順
    9: (3, -1),   # 癸: 卯起, 逆
}


# ============================================================
# 主要計算函數
# ============================================================

def get_year_stem(year: int) -> int:
    """取得年干索引 (甲=0 ... 癸=9)"""
    return (year - 4) % 10


def get_year_branch(year: int) -> int:
    """取得年支索引 (子=0 ... 亥=11)"""
    return (year - 4) % 12


def get_month_branch(solar_month: int) -> int:
    """
    取得月支索引。節氣月1=寅(2), 2=卯(3), ..., 12=丑(1)
    """
    return (solar_month + 1) % 12


def get_day_stem_branch(jd: float):
    """
    由儒略日計算日干支。
    基準: JD 2451911.0 = 2001-01-01 = 辛巳年庚子月丙午日
    丙=2(干), 午=6(支)
    """
    day_num = int(jd + 0.5)
    base_jd = 2451911  # 2001-01-01
    diff = day_num - base_jd
    day_stem = (2 + diff) % 10
    day_branch = (6 + diff) % 12
    return day_stem, day_branch


def get_hour_stem(day_stem: int, hour_branch: int) -> int:
    """
    由日干和時支推算時干。
    甲己日子時起甲子, 乙庚日子時起丙子, 丙辛日子時起戊子,
    丁壬日子時起庚子, 戊癸日子時起壬子
    """
    base = (day_stem % 5) * 2
    return (base + hour_branch) % 10


def compute_twelve_life_stages(year_stem: int):
    """
    計算十二長生在十二地支的分佈。
    返回 dict: branch_idx -> stage_name
    """
    start_branch, direction = CHANGSHENG_START[year_stem]
    result = {}
    for i in range(12):
        branch = (start_branch + direction * i) % 12
        result[branch] = TWELVE_LIFE_STAGES[i]
    return result


def compute_shensha(
    year: int,
    solar_month: int,
    julian_day: float,
    hour_branch: int,
) -> ShenShaResult:
    """
    計算神煞。

    Parameters:
        year: 西曆年份
        solar_month: 節氣月 (1-12)
        julian_day: 儒略日
        hour_branch: 時辰地支索引 (0-11)

    Returns:
        ShenShaResult: 包含所有神煞及其宮位分配
    """
    year_stem = get_year_stem(year)
    year_branch = get_year_branch(year)
    month_branch = get_month_branch(solar_month)
    day_stem, day_branch = get_day_stem_branch(julian_day)

    items = []

    def _add(name, branch, category, source):
        items.append(ShenShaItem(
            name=name, branch=branch, category=category, source=source,
        ))

    # ---- 年支系 ----
    _add("驛馬", YIMA[year_branch], "中", "年支")
    _add("桃花", TAOHUA[year_branch], "中", "年支")
    _add("華蓋", HUAGAI[year_branch], "吉", "年支")
    _add("劫煞", JIESHA[year_branch], "凶", "年支")
    _add("亡神", WANGSHEN[year_branch], "凶", "年支")
    _add("天空", TIANKONG[year_branch], "凶", "年支")
    _add("孤辰", GUCHEN[year_branch], "凶", "年支")
    _add("寡宿", GUASU[year_branch], "凶", "年支")
    _add("天哭", TIANKU[year_branch], "凶", "年支")
    _add("天虛", TIANXU[year_branch], "凶", "年支")
    _add("天狗", TIANGOU[year_branch], "凶", "年支")
    _add("弔客", DIAOKE[year_branch], "凶", "年支")
    _add("白虎", BAIHU[year_branch], "凶", "年支")

    # ---- 年支系 (吉) ----
    _add("紅鸞", HONGLUAN[year_branch], "吉", "年支")
    _add("天喜", TIANXI[year_branch], "吉", "年支")

    # ---- 年干系 ----
    for b in TIANYI_GUIREN[year_stem]:
        _add("天乙貴人", b, "吉", "年干")
    _add("文昌", WENCHANG[year_stem], "吉", "年干")
    _add("祿神", LUSHEN[year_stem], "吉", "年干")
    _add("羊刃", YANGREN[year_stem], "凶", "年干")
    _add("天官", TIANGUAN[year_stem], "吉", "年干")
    _add("天廚", TIANCHU[year_stem], "吉", "年干")

    # ---- 月支系 ----
    td = TIANDE_BY_MONTH.get(month_branch)
    if td is not None:
        _add("天德", td, "吉", "月支")
    yd = YUEDE_BY_MONTH.get(month_branch)
    if yd is not None:
        _add("月德", yd, "吉", "月支")

    # ---- 十二長生 ----
    life_stages = compute_twelve_life_stages(year_stem)
    for branch_idx, stage_name in life_stages.items():
        _add(stage_name, branch_idx, "中", "年干")

    # Build branch_map
    branch_map: dict[int, list[str]] = {}
    for item in items:
        if item.branch not in branch_map:
            branch_map[item.branch] = []
        branch_map[item.branch].append(item.name)

    return ShenShaResult(items=items, branch_map=branch_map)


def get_bazi_stems_branches(
    year: int,
    solar_month: int,
    julian_day: float,
    hour_branch: int,
):
    """
    計算八字四柱天干地支。

    Returns:
        dict with keys: year_stem, year_branch, month_stem, month_branch,
                        day_stem, day_branch, hour_stem, hour_branch
              and their corresponding name strings.
    """
    ys = get_year_stem(year)
    yb = get_year_branch(year)
    mb = get_month_branch(solar_month)
    # 月干 = 年干 * 2 + 月支偏移 (虎月起法)
    yin_stem = (2 * (ys % 5) + 2) % 10
    ms = (yin_stem + (mb - 2 + 12) % 12) % 10
    ds, db = get_day_stem_branch(julian_day)
    hs = get_hour_stem(ds, hour_branch)

    return {
        "year_stem": ys, "year_branch": yb,
        "month_stem": ms, "month_branch": mb,
        "day_stem": ds, "day_branch": db,
        "hour_stem": hs, "hour_branch": hour_branch,
        "year_pillar": HEAVENLY_STEMS[ys] + EARTHLY_BRANCHES[yb],
        "month_pillar": HEAVENLY_STEMS[ms] + EARTHLY_BRANCHES[mb],
        "day_pillar": HEAVENLY_STEMS[ds] + EARTHLY_BRANCHES[db],
        "hour_pillar": HEAVENLY_STEMS[hs] + EARTHLY_BRANCHES[hour_branch],
    }
