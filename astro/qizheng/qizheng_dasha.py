"""
七政四餘年限大運模組 (Planetary Period / Dasha Module)

七政四餘的大限（年限大運）系統：
  - 以命度（上升點）所在星次為起點
  - 根據各星次的主星分配不同年限
  - 男命順行、女命逆行

行限規則 (各星主管年限)：
  太陽: 19年, 太陰: 25年, 火星: 7年, 水星: 20年,
  木星: 12年, 金星: 15年, 土星: 22年

流年限度 (Flow Year)：
  根據大運起始年齡和當年歲數，推算流年所在宮位。
"""

from dataclasses import dataclass, field


# ============================================================
# 星曜年限 (Planet Period Years)
# ============================================================

# 七政四餘行限年數：
# 傳統七政四餘的行限根據十二宮主星各有不同年限
# 此處依照果老星宗的簡化法：以七政五行屬性分配
PLANET_PERIOD_YEARS = {
    "太陽": 19,
    "太陰": 25,
    "火星": 7,
    "水星": 20,
    "木星": 12,
    "金星": 15,
    "土星": 22,
}

# 十二宮主星對應（七政四餘傳統）：
# 每個宮位（地支）有一個主星，決定該宮行限年數
# 戌宮→太陽, 酉宮→太陰, 申宮→火星, 未宮→水星,
# 午宮→木星, 巳宮→金星, 辰宮→土星, 卯宮→太陽,
# 寅宮→木星, 丑宮→土星, 子宮→金星, 亥宮→水星
BRANCH_LORD = {
    10: "火星",   # 戌
    9: "金星",    # 酉
    8: "水星",    # 申
    7: "太陰",    # 未
    6: "太陽",    # 午
    5: "水星",    # 巳
    4: "金星",    # 辰
    3: "木星",    # 卯
    2: "火星",    # 寅
    1: "土星",    # 丑
    0: "土星",    # 子
    11: "木星",   # 亥
}

EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳",
                    "午", "未", "申", "酉", "戌", "亥"]


@dataclass
class DashaPeriod:
    """單個大運時段"""
    palace_index: int       # 宮位索引 (在 houses 中的位置)
    branch: int             # 地支索引
    branch_name: str        # 地支名稱
    palace_name: str        # 宮位名稱
    lord: str               # 主星名稱
    years: int              # 年限
    start_age: int          # 起始年齡
    end_age: int            # 結束年齡
    start_year: int         # 起始西曆年
    end_year: int           # 結束西曆年


@dataclass
class DashaResult:
    """大運計算結果"""
    periods: list = field(default_factory=list)    # List[DashaPeriod]
    current_period_idx: int = -1                   # 當前大運索引
    current_age: int = 0                           # 當前年齡
    flow_year_branch: int = -1                     # 流年所在地支
    flow_year_palace: str = ""                     # 流年所在宮位


def compute_dasha(
    birth_year: int,
    ming_gong_branch: int,
    gender: str,
    houses: list,
    current_year: int = 0,
) -> DashaResult:
    """
    計算年限大運。

    Parameters:
        birth_year: 出生年份
        ming_gong_branch: 命宮地支索引
        gender: 性別 ("male" / "female")
        houses: 十二宮位列表 (HouseData)
        current_year: 當前年份 (用於計算流年)

    Returns:
        DashaResult
    """
    # 建立 branch → house 映射
    branch_to_house = {}
    for h in houses:
        branch_to_house[h.branch] = h

    # 大運方向: 男命順行(地支遞減=宮位索引遞增), 女命逆行
    direction = -1 if gender == "male" else 1

    periods = []
    age = 0

    for i in range(12):
        branch = (ming_gong_branch + direction * i) % 12
        lord = BRANCH_LORD[branch]
        years = PLANET_PERIOD_YEARS[lord]
        house = branch_to_house.get(branch)
        palace_name = house.name if house else ""
        palace_index = house.index if house else i

        period = DashaPeriod(
            palace_index=palace_index,
            branch=branch,
            branch_name=EARTHLY_BRANCHES[branch],
            palace_name=palace_name,
            lord=lord,
            years=years,
            start_age=age,
            end_age=age + years - 1,
            start_year=birth_year + age,
            end_year=birth_year + age + years - 1,
        )
        periods.append(period)
        age += years

    # 計算當前年齡和大運
    current_age = current_year - birth_year if current_year else 0
    current_period_idx = -1
    for idx, p in enumerate(periods):
        if p.start_age <= current_age <= p.end_age:
            current_period_idx = idx
            break

    # 計算流年 (flow year)：
    # 流年地支 = 流年太歲地支 = (year - 4) % 12
    flow_year_branch = (current_year - 4) % 12 if current_year else -1
    flow_year_palace = ""
    if flow_year_branch >= 0:
        fh = branch_to_house.get(flow_year_branch)
        flow_year_palace = fh.name if fh else ""

    return DashaResult(
        periods=periods,
        current_period_idx=current_period_idx,
        current_age=current_age,
        flow_year_branch=flow_year_branch,
        flow_year_palace=flow_year_palace,
    )
