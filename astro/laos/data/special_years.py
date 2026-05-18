# astro/lao/data/special_years.py
"""
老撾占星術 (ໄທຣາສາດລາວ) 特殊年份計算模組
包含三種核心特殊年份：
    1. ປີອະທິກະສຸຣະທິບ (Adhikasurathib)
    2. ປີອະທິກະມາດ (Adhikamat)
    3. ປີອະທິກະອານ (Adhikawan)
"""

from .constants import SPECIAL_YEAR_CYCLES, BUDDHIST_ERA_OFFSET


def is_adhikasurathib_year(year: int) -> bool:
    """
    判斷是否為 ປີອະທິກະສຸຣະທິບ (11年週期)
    書中第105頁規則
    """
    rule = SPECIAL_YEAR_CYCLES["ອະທິກະສຸຣະທິບ"]
    return (year - rule["offset"]) % rule["cycle"] == 0


def is_adhikamat_year(year: int) -> bool:
    """
    判斷是否為 ປີອະທິກະມາດ (7年週期)
    書中第109頁規則
    """
    rule = SPECIAL_YEAR_CYCLES["ອະທິກະມາດ"]
    return (year - rule["offset"]) % rule["cycle"] == 0


def is_adhikawan_year(year: int) -> bool:
    """
    判斷是否為 ປີອະທິກະອານ (19年週期)
    書中第115頁規則
    """
    rule = SPECIAL_YEAR_CYCLES["ອະທິກະອານ"]
    return (year - rule["offset"]) % rule["cycle"] == 0


def get_special_year_type(year: int) -> dict:
    """
    回傳該年的所有特殊年份類型（可同時多種）
    返回格式：
    {
        "ອະທິກະສຸຣະທິບ": {...},
        "ອະທິກະມາດ": {...},
        ...
    }
    """
    results = {}
    for name, rule in SPECIAL_YEAR_CYCLES.items():
        if (year - rule["offset"]) % rule["cycle"] == 0:
            results[name] = rule.copy()
            results[name]["is_special"] = True
    return results


def is_special_year(year: int) -> bool:
    """快速判斷該年是否為任一特殊年份"""
    return bool(get_special_year_type(year))


def get_lao_year_from_gregorian(gregorian_year: int) -> int:
    """西元年轉老撾佛曆年（常用於計算特殊年份）"""
    return gregorian_year + BUDDHIST_ERA_OFFSET


def get_gregorian_year_from_lao(lao_year: int) -> int:
    """老撾佛曆年轉西元年"""
    return lao_year - BUDDHIST_ERA_OFFSET


# 綜合判斷函數（推薦在 calculator.py 中使用）
def analyze_special_year(year: int, era: str = "lao") -> dict:
    """
    完整分析特殊年份
    era 可為 "lao" (佛曆) 或 "gregorian" (西元年)
    """
    if era == "gregorian":
        year = get_lao_year_from_gregorian(year)
    
    special = get_special_year_type(year)
    return {
        "lao_year": year,
        "gregorian_year": get_gregorian_year_from_lao(year),
        "is_special": bool(special),
        "special_types": special,
        "description": "、".join(special.keys()) if special else "普通年份"
    }


# 測試用（開發時可直接執行本檔案）
if __name__ == "__main__":
    test_year = 2026
    print(f"西元 {test_year} 年（老撾佛曆 {get_lao_year_from_gregorian(test_year)}）")
    print(analyze_special_year(test_year, era="gregorian"))
    
    # 範例輸出：
    # {'lao_year': 2569, 'gregorian_year': 2026, 'is_special': True, ...}
