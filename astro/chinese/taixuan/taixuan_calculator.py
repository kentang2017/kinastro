# -*- coding: utf-8 -*-
"""
taixuan_calculator.py — 太玄數核心計算類別
TaiXuanCalculator: 本命起盤 + 即時問卜 + 干支聯動

使用 taixuanshifa 套件（pip install taixuanshifa），
若套件不可用則自行實現等效邏輯。
"""

from __future__ import annotations

import math
import pickle
import os
import random
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, Dict, List, Tuple

# ── 載入太玄字典 ────────────────────────────────────────────
try:
    from taixuanshifa.taixuanshifa import qigua as _taixuan_qigua, qigua_number as _taixuan_qigua_number
    _TAIXUAN_DICT_PATH = os.path.join(
        os.path.dirname(
            __import__("taixuanshifa").__file__
        ),
        "data",
        "taixuandict.p",
    )
    _TAIXUAN_DICT: Dict = pickle.load(open(_TAIXUAN_DICT_PATH, "rb"))
    _PKG_AVAILABLE = True
except Exception:
    _PKG_AVAILABLE = False
    _TAIXUAN_DICT = {}

# ── 常數 ────────────────────────────────────────────────────
# 九贊名稱（九個爻）
ZHAN_NAMES: List[str] = ["初一", "次二", "次三", "次四", "次五", "次六", "次七", "次八", "上九"]
# 數字→漢字映射
_NUM_TO_ZH: Dict[str, str] = {"1": "一", "2": "二", "3": "三"}
# 首序號（1-80）→ 字典鍵的有序列表
_SORTED_KEYS: List[int] = sorted(_TAIXUAN_DICT.keys()) if _TAIXUAN_DICT else []

# 太玄計算常數
DAYS_PER_YEAR: float = 365.25          # 儒略年天數
TOTAL_SHOU_COUNT: int = 80             # 太玄八十首總數
ZHAN_COUNT: int = 9                    # 每首九贊
HOURS_PER_DAY: int = 24                # 每日二十四小時

# 四時段定義（小時範圍）
# 注意：夜中（21, 3）為跨午夜段，_hour_to_sishi 使用 else 語句處理
SISHI_MAP: Dict[str, Tuple[int, int]] = {
    "旦": (3, 9),       # 03:00–08:59
    "日中": (9, 15),    # 09:00–14:59
    "夕": (15, 21),     # 15:00–20:59
    "夜中": (21, 3),    # 21:00–02:59（跨午夜，實際以 else 判斷）
}

# 四時段 → 贊索引範圍（對應 ZHAN_NAMES，0-based）
SISHI_ZHAN_RANGE: Dict[str, Tuple[int, int]] = {
    "旦": (0, 2),    # 初一、次二、次三
    "日中": (3, 5),  # 次四、次五、次六
    "夕": (6, 7),    # 次七、次八
    "夜中": (8, 8),  # 上九
}

# 二十八宿（與太玄首一一對應，每首對應若干宿）
TWENTY_EIGHT_MANSIONS: List[str] = [
    "角", "亢", "氐", "房", "心", "尾", "箕",
    "斗", "牛", "女", "虛", "危", "室", "壁",
    "奎", "婁", "胃", "昴", "畢", "觜", "參",
    "井", "鬼", "柳", "星", "張", "翼", "軫",
]

# 天干地支（用於干支聯動）
TIANGAN: List[str] = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
DIZHI: List[str] = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
WUXING: Dict[str, str] = {
    "甲": "木", "乙": "木", "丙": "火", "丁": "火",
    "戊": "土", "己": "土", "庚": "金", "辛": "金",
    "壬": "水", "癸": "水",
    "子": "水", "丑": "土", "寅": "木", "卯": "木",
    "辰": "土", "巳": "火", "午": "火", "未": "土",
    "申": "金", "酉": "金", "戌": "土", "亥": "水",
}

# 七政四餘行星與太玄首的對應（傳統配屬）
PLANET_SHOU_MAP: Dict[str, List[int]] = {
    "太陽": [1, 10, 19, 28, 37, 46, 55, 64, 73],
    "太陰": [2, 11, 20, 29, 38, 47, 56, 65, 74],
    "金星": [3, 12, 21, 30, 39, 48, 57, 66, 75],
    "木星": [4, 13, 22, 31, 40, 49, 58, 67, 76],
    "水星": [5, 14, 23, 32, 41, 50, 59, 68, 77],
    "火星": [6, 15, 24, 33, 42, 51, 60, 69, 78],
    "土星": [7, 16, 25, 34, 43, 52, 61, 70, 79],
    "羅喉": [8, 17, 26, 35, 44, 53, 62, 71, 80],
    "計都": [9, 18, 27, 36, 45, 54, 63, 72],
}


# ── 輔助函數 ────────────────────────────────────────────────

def _julian_day(year: int, month: int, day: int) -> float:
    """計算儒略日數（整數）"""
    if month <= 2:
        year -= 1
        month += 12
    A = math.floor(year / 100)
    B = 2 - A + math.floor(A / 4)
    return math.floor(365.25 * (year + 4716)) + math.floor(30.6001 * (month + 1)) + day + B - 1524.5


def _winter_solstice_jd(year: int) -> float:
    """估算某年冬至（12月）的儒略日（近似值）
    
    冬至通常落在 12月21-22日，此處取12月22日為近似值。
    """
    return _julian_day(year, 12, 22)


def _hour_to_sishi(hour: int) -> str:
    """將小時（0-23）轉換為四時段名稱"""
    if 3 <= hour < 9:
        return "旦"
    elif 9 <= hour < 15:
        return "日中"
    elif 15 <= hour < 21:
        return "夕"
    else:
        return "夜中"


def _ganzhi_year(year: int) -> Tuple[str, str]:
    """計算某年的天干地支"""
    tg_idx = (year - 4) % 10
    dz_idx = (year - 4) % 12
    return TIANGAN[tg_idx], DIZHI[dz_idx]


def _ganzhi_month(year: int, month: int) -> Tuple[str, str]:
    """計算農曆月的天干地支（簡化節氣法）"""
    # 簡化：以節為分界
    dz_idx = (month + 1) % 12
    # 月干取決於年干
    year_tg_idx = (year - 4) % 10
    tg_base = (year_tg_idx % 5) * 2
    tg_idx = (tg_base + month - 1) % 10
    return TIANGAN[tg_idx], DIZHI[dz_idx]


def _ganzhi_day(year: int, month: int, day: int) -> Tuple[str, str]:
    """計算日柱天干地支"""
    jd = _julian_day(year, month, day)
    idx = int(jd) + 49
    tg_idx = idx % 10
    dz_idx = idx % 12
    return TIANGAN[tg_idx], DIZHI[dz_idx]


def _ganzhi_hour(hour: int, day_tg: str) -> Tuple[str, str]:
    """計算時柱天干地支"""
    dz_idx = (hour // 2) % 12
    day_tg_idx = TIANGAN.index(day_tg)
    tg_base = (day_tg_idx % 5) * 2
    tg_idx = (tg_base + dz_idx) % 10
    return TIANGAN[tg_idx], DIZHI[dz_idx]


def _serial_to_key(serial: int) -> Optional[int]:
    """將首序號（1-80）轉為字典鍵"""
    if not _SORTED_KEYS:
        return None
    idx = max(0, min(serial - 1, len(_SORTED_KEYS) - 1))
    return _SORTED_KEYS[idx]


def _key_to_name(key: int) -> str:
    """將字典鍵（如 2133）轉為首名稱（如「二方一州三部三家」）"""
    s = str(key)
    return (
        _NUM_TO_ZH.get(s[0], s[0]) + "方"
        + _NUM_TO_ZH.get(s[1], s[1]) + "州"
        + _NUM_TO_ZH.get(s[2], s[2]) + "部"
        + _NUM_TO_ZH.get(s[3], s[3]) + "家"
    )


def _key_to_serial(key: int) -> int:
    """將字典鍵轉為首序號（1-based）"""
    if key in _SORTED_KEYS:
        return _SORTED_KEYS.index(key) + 1
    return 0


def _mansion_for_serial(serial: int) -> str:
    """根據首序號（1-80）取二十八宿"""
    idx = ((serial - 1) * len(TWENTY_EIGHT_MANSIONS)) // 80
    return TWENTY_EIGHT_MANSIONS[idx % len(TWENTY_EIGHT_MANSIONS)]


def _planet_for_serial(serial: int) -> str:
    """根據首序號取對應七政行星"""
    for planet, serials in PLANET_SHOU_MAP.items():
        if serial in serials:
            return planet
    return "——"


# ── 資料類別 ────────────────────────────────────────────────

@dataclass
class TaiXuanShou:
    """太玄一首的完整資料"""
    serial: int          # 序號 1-80
    key: int             # 字典鍵，如 1111
    name: str            # 首名稱，如「一方一州一一家」
    gua_title: str       # 卦名（首名），如「中」
    gua_text: str        # 卦辭
    zhan_name: str       # 當值贊名，如「次四」
    zhan_text: str       # 贊辭 + 測曰
    sishi: str           # 四時段
    mansion: str         # 對應二十八宿
    planet: str          # 對應七政行星
    all_zhan: Dict[str, str] = field(default_factory=dict)  # 全部九贊


@dataclass
class TaiXuanResult:
    """太玄排盤完整結果"""
    mode: str                   # "natal" | "qigua"
    shou: TaiXuanShou
    birth_dt: Optional[datetime]
    # 干支四柱
    year_gz: str = ""
    month_gz: str = ""
    day_gz: str = ""
    hour_gz: str = ""
    # 聯動資訊
    wuxing_year: str = ""
    wuxing_day: str = ""
    sishi: str = ""             # 四時段
    # 行年大限（流年首）
    annual_shou_list: List[Dict] = field(default_factory=list)
    # 完整 81 首表
    all_shou_table: List[Dict] = field(default_factory=list)


# ── 主計算類別 ───────────────────────────────────────────────

class TaiXuanCalculator:
    """
    太玄數計算器

    支援兩種模式：
    1. 本命排盤（natal）：輸入出生年月日時，計算命宮首與干支聯動
    2. 即時問卜（qigua）：以蓍草亂數法求首、求贊

    參數
    ----
    year  : int
    month : int
    day   : int
    hour  : int  (0-23)
    mode  : "natal" | "qigua"
    """

    def __init__(
        self,
        year: int = 2000,
        month: int = 1,
        day: int = 1,
        hour: int = 12,
        mode: str = "natal",
    ) -> None:
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.mode = mode

    # ── 公開入口 ────────────────────────────────────────────

    def calculate(self) -> TaiXuanResult:
        """執行計算，返回 TaiXuanResult"""
        if self.mode == "qigua":
            return self._calc_qigua()
        return self._calc_natal()

    # ── 本命排盤 ────────────────────────────────────────────

    def _calc_natal(self) -> TaiXuanResult:
        """本命起盤：以出生年月日計算命宮首"""
        # 1. 計算儒略日
        birth_jd = _julian_day(self.year, self.month, self.day)
        # 2. 找當年冬至（前一年冬至為太玄年起點）
        ws_year = self.year - 1 if self.month < 12 else self.year
        ws_jd = _winter_solstice_jd(ws_year)
        # 3. 距冬至天數
        days_since_ws = birth_jd - ws_jd
        if days_since_ws < 0:
            ws_jd = _winter_solstice_jd(ws_year - 1)
            days_since_ws = birth_jd - ws_jd
        # 4. 每首覆蓋天數 ≈ DAYS_PER_YEAR / TOTAL_SHOU_COUNT ≈ 4.566 天
        days_per_shou = DAYS_PER_YEAR / TOTAL_SHOU_COUNT
        serial = int(days_since_ws / days_per_shou) % TOTAL_SHOU_COUNT + 1
        # 5. 四時段 & 贊
        sishi = _hour_to_sishi(self.hour)
        zhan_idx = self._pick_zhan_by_hour(self.hour)
        # 6. 取首資料
        shou = self._build_shou(serial, sishi, zhan_idx)
        # 7. 干支四柱
        year_tg, year_dz = _ganzhi_year(self.year)
        month_tg, month_dz = _ganzhi_month(self.year, self.month)
        day_tg, day_dz = _ganzhi_day(self.year, self.month, self.day)
        hour_tg, hour_dz = _ganzhi_hour(self.hour, day_tg)
        # 8. 行年大限（未來 81 年，每 4.5 年一首）
        annual_list = self._calc_annual_shous(serial, self.year)
        # 9. 完整 81 首表
        all_table = self._build_all_table()

        dt = datetime(self.year, self.month, self.day, self.hour)
        return TaiXuanResult(
            mode="natal",
            shou=shou,
            birth_dt=dt,
            year_gz=f"{year_tg}{year_dz}",
            month_gz=f"{month_tg}{month_dz}",
            day_gz=f"{day_tg}{day_dz}",
            hour_gz=f"{hour_tg}{hour_dz}",
            wuxing_year=WUXING.get(year_tg, "") + WUXING.get(year_dz, ""),
            wuxing_day=WUXING.get(day_tg, "") + WUXING.get(day_dz, ""),
            sishi=sishi,
            annual_shou_list=annual_list,
            all_shou_table=all_table,
        )

    # ── 即時問卜 ────────────────────────────────────────────

    def _calc_qigua(self) -> TaiXuanResult:
        """即時問卜：蓍草亂數法"""
        if _PKG_AVAILABLE:
            gua_number, gua_name, gua, gua_details, zhan_number, zhan = _taixuan_qigua()
            serial = _key_to_serial(gua_number)
            sishi = _hour_to_sishi(datetime.now().hour)
            zhan_idx = ZHAN_NAMES.index(zhan_number) if zhan_number in ZHAN_NAMES else 0
            shou = self._build_shou_from_dict(
                serial=serial,
                key=gua_number,
                name=gua_name,
                gua_details=gua_details,
                sishi=sishi,
                zhan_idx=zhan_idx,
            )
        else:
            # 備援：直接亂數
            serial = random.randint(1, 80)
            zhan_idx = random.randint(0, 8)
            sishi = random.choice(list(SISHI_MAP.keys()))
            shou = self._build_shou(serial, sishi, zhan_idx)

        dt = datetime.now()
        return TaiXuanResult(
            mode="qigua",
            shou=shou,
            birth_dt=dt,
            all_shou_table=self._build_all_table(),
        )

    # ── 輔助構建方法 ────────────────────────────────────────

    def _pick_zhan_by_hour(self, hour: int) -> int:
        """根據小時選擇九贊索引（0-based），將 24 小時均分為 9 段"""
        zhan_idx = (hour * ZHAN_COUNT) // HOURS_PER_DAY
        return min(zhan_idx, ZHAN_COUNT - 1)

    def _build_shou(self, serial: int, sishi: str, zhan_idx: int) -> TaiXuanShou:
        """根據序號構建 TaiXuanShou"""
        key = _serial_to_key(serial)
        if key is None or key not in _TAIXUAN_DICT:
            # 空首佔位
            return TaiXuanShou(
                serial=serial, key=0, name="——", gua_title="——",
                gua_text="", zhan_name="——", zhan_text="",
                sishi=sishi, mansion="——", planet="——",
            )
        gua_details = _TAIXUAN_DICT[key]
        return self._build_shou_from_dict(
            serial=serial, key=key,
            name=_key_to_name(key),
            gua_details=gua_details,
            sishi=sishi, zhan_idx=zhan_idx,
        )

    def _build_shou_from_dict(
        self,
        serial: int,
        key: int,
        name: str,
        gua_details: dict,
        sishi: str,
        zhan_idx: int,
    ) -> TaiXuanShou:
        """從字典資料構建 TaiXuanShou"""
        # 卦辭
        gua_dict = gua_details.get("卦", {})
        gua_title = next(iter(gua_dict.keys()), "——") if gua_dict else "——"
        gua_text = gua_dict.get(gua_title, "")
        # 九贊
        all_zhan: Dict[str, str] = {}
        for zn in ZHAN_NAMES:
            all_zhan[zn] = gua_details.get(zn, "")
        # 當值贊
        zhan_name = ZHAN_NAMES[zhan_idx]
        zhan_text = all_zhan.get(zhan_name, "")
        return TaiXuanShou(
            serial=serial,
            key=key,
            name=name,
            gua_title=gua_title,
            gua_text=gua_text,
            zhan_name=zhan_name,
            zhan_text=zhan_text,
            sishi=sishi,
            mansion=_mansion_for_serial(serial),
            planet=_planet_for_serial(serial),
            all_zhan=all_zhan,
        )

    def _calc_annual_shous(self, natal_serial: int, birth_year: int) -> List[Dict]:
        """計算行年大限（流年首），未來 81 年"""
        result = []
        # 每 4.566 天一首 → 每年 ≈ 80 首 → 每首持續 ≈ 4.566 天
        # 行年大限：每年以流年干支起首，從本命首起順推
        for offset in range(0, 81):
            year = birth_year + offset
            serial = (natal_serial - 1 + offset) % TOTAL_SHOU_COUNT + 1
            key = _serial_to_key(serial)
            name = _key_to_name(key) if key else "——"
            gua_title = "——"
            if key and key in _TAIXUAN_DICT:
                gua_dict = _TAIXUAN_DICT[key].get("卦", {})
                gua_title = next(iter(gua_dict.keys()), "——")
            year_tg, year_dz = _ganzhi_year(year)
            result.append({
                "年份": year,
                "年齡": offset,
                "年干支": f"{year_tg}{year_dz}",
                "首序": serial,
                "首鍵": key,
                "首名": name,
                "首卦名": gua_title,
                "五行": WUXING.get(year_tg, ""),
            })
        return result

    def _build_all_table(self) -> List[Dict]:
        """建立完整 80 首參考表"""
        result = []
        for i, key in enumerate(_SORTED_KEYS):
            serial = i + 1
            gua_details = _TAIXUAN_DICT.get(key, {})
            gua_dict = gua_details.get("卦", {})
            gua_title = next(iter(gua_dict.keys()), "——") if gua_dict else "——"
            gua_text = gua_dict.get(gua_title, "")
            result.append({
                "序": serial,
                "鍵": key,
                "首名": _key_to_name(key),
                "卦名": gua_title,
                "卦辭": gua_text,
                "二十八宿": _mansion_for_serial(serial),
                "七政": _planet_for_serial(serial),
            })
        return result

    # ── 問卜靜態方法 ────────────────────────────────────────

    @staticmethod
    def qigua_raw() -> Tuple[int, str, str, Dict[str, str], str, str]:
        """
        直接呼叫 taixuanshifa 問卜，返回原始 tuple：
        (gua_number, gua_name, gua_title, all_zhan, zhan_number, zhan_text)
        """
        if _PKG_AVAILABLE:
            gua_number, gua_name, gua, gua_details, zhan_number, zhan = _taixuan_qigua()
            gua_dict = gua if isinstance(gua, dict) else {}
            gua_title = next(iter(gua_dict.keys()), "——")
            all_zhan = {k: v for k, v in gua_details.items() if k != "卦"}
            return gua_number, gua_name, gua_title, all_zhan, zhan_number, zhan
        # 備援
        serial = random.randint(1, 80)
        key = _serial_to_key(serial)
        if key and key in _TAIXUAN_DICT:
            gua_details = _TAIXUAN_DICT[key]
            gua_dict = gua_details.get("卦", {})
            gua_title = next(iter(gua_dict.keys()), "——")
            all_zhan = {k: v for k, v in gua_details.items() if k != "卦"}
            zhan_number = ZHAN_NAMES[random.randint(0, 8)]
            return key, _key_to_name(key), gua_title, all_zhan, zhan_number, all_zhan.get(zhan_number, "")
        return 1111, "一方一州一部一家", "中", {}, "初一", ""
