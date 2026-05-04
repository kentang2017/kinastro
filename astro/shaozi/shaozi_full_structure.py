#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
邵子神數 完整結構化模組 (shaozi_full_structure.py)
===================================================

專為 https://github.com/kentang2017/kinastro 專案設計

核心功能：
1. 完整起數秘訣實作（天干起數、地支起數、配卦、河洛配數、天數成卦、地數成卦、八卦加則）
2. 64個鑰匙表格進階整合（坤集最核心實戰工具）
3. 進階起盤函式（結合基礎計算 + 64鑰匙細調 + 時辰/運限查詢）
4. 條文資料庫載入
5. 與鐵板神數一致的設計風格與 API

使用方式：
    from shaozi_full_structure import ShaoziShenShu

    shaozi = ShaoziShenShu()
    result = shaozi.cast_plate(
        year_gz="甲子", month_gz="丙寅",
        day_gz="戊辰", hour_gz="庚午",
        ke="初刻"          # 可選：指定刻數進行細調
    )
"""

from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import json

# ====================== 1. 匯入64鑰匙表格 ======================
try:
    from .shaozi_64_keys import (
        SHAOZI_64_KEYS,
        get_key_info,
        get_special_notes,
        get_key_name
    )
except ImportError:
    from shaozi_64_keys import (
        SHAOZI_64_KEYS,
        get_key_info,
        get_special_notes,
        get_key_name
    )

# ====================== 2. 起數秘訣表（完整版） ======================

TIANGAN_QISHU: Dict[str, int] = {
    "戊": 1, "乙": 2, "癸": 2, "庚": 3, "辛": 4,
    "壬": 6, "甲": 6, "丁": 7, "丙": 8, "己": 9,
}

DIZHI_QISHU: Dict[str, int] = {
    "亥": 1, "子": 1, "寅": 3, "卯": 3,
    "巳": 2, "午": 2, "申": 4, "酉": 4,
    "辰": 5, "戌": 5, "丑": 5, "未": 5,
}

TIANGAN_PEIGUA: Dict[str, str] = {
    "壬": "乾", "甲": "乾", "乙": "坤", "癸": "坤",
    "庚": "震", "辛": "巽", "丙": "艮", "己": "離",
    "戊": "坎", "丁": "兌",
}

DIZHI_PEIGUA: Dict[int, str] = {
    1: "坎", 2: "坤", 3: "震", 4: "巽",
    5: "中宮", 6: "乾", 7: "兌", 8: "艮", 9: "離",
}

HELUO_SHU: Dict[str, int] = {
    "甲己": 9, "子午": 9, "乙庚": 8, "丑未": 8,
    "丙辛": 7, "寅申": 7, "丁壬": 6, "卯酉": 6,
    "戊癸": 5, "辰戌": 5, "巳亥": 4,
}

# ====================== 3. 核心計算函式 ======================

def calculate_tiangan_number(tg: str) -> int:
    return TIANGAN_QISHU.get(tg, 5)

def calculate_dizhi_number(dz: str) -> int:
    return DIZHI_QISHU.get(dz, 5)

def calculate_he_luo(tg: str, dz: str) -> int:
    key1 = f"{tg}{dz}"
    key2 = f"{dz}{tg}"
    return HELUO_SHU.get(key1, HELUO_SHU.get(key2, 5))

def get_peigua(tg: str, dz: str) -> str:
    tg_gua = TIANGAN_PEIGUA.get(tg, "中宮")
    dz_num = calculate_dizhi_number(dz)
    dz_gua = DIZHI_PEIGUA.get(dz_num, "中宮")
    return f"{tg_gua}{dz_gua}"

def tian_shu_cheng_gua(tian_total: int) -> int:
    if tian_total == 25:
        return 5
    elif tian_total < 25:
        return tian_total
    else:
        remainder = tian_total - 25
        return remainder % 10 or 5

def di_shu_cheng_gua(di_total: int) -> int:
    if di_total == 30:
        return 3
    elif di_total < 30:
        return di_total
    else:
        remainder = di_total - 30
        return remainder % 10 or 3

def ba_gua_jia_ze(base: int) -> int:
    result = (base + 30) % 64
    return result if result != 0 else 64

# ====================== 4. 完整邵子神數類別 ======================

class ShaoziShenShu:
    """
    邵子神數完整起盤系統（進階版）

    整合：
    - 起數秘訣完整計算
    - 64個鑰匙表格進階查詢（時辰、運限、流年、特殊事項）
    - 條文資料庫
    """

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.tiaowen_db: Dict[str, str] = {}
        self.load_tiaowen()

    def load_tiaowen(self) -> None:
        json_path = self.data_dir / "shaozi_tiaowen_6144.json"
        if json_path.exists():
            with open(json_path, "r", encoding="utf-8") as f:
                self.tiaowen_db = json.load(f)
        else:
            print("⚠️  條文 JSON 不存在，建議先生成 shaozi_tiaowen_6144.json")

    def cast_plate(self,
                   year_gz: str,
                   month_gz: str,
                   day_gz: str,
                   hour_gz: str,
                   ke: str = "初刻",
                   use_key: bool = True) -> Dict[str, Any]:
        """
        進階起盤（強烈建議使用64鑰匙細調）

        Args:
            year_gz, month_gz, day_gz, hour_gz: 干支
            ke: 指定刻數（初刻、二刻、子初、丑初...），用於64鑰匙時辰查詢
            use_key: 是否啟用64鑰匙進階細調

        Returns:
            包含完整計算過程、條文、64鑰匙詳細資訊的字典
        """
        # 1. 拆解干支
        y_tg, y_dz = year_gz[0], year_gz[1]
        m_tg, m_dz = month_gz[0], month_gz[1]
        d_tg, d_dz = day_gz[0], day_gz[1]
        h_tg, h_dz = hour_gz[0], hour_gz[1]

        # 2. 計算各項總數
        tg_sum = sum([
            calculate_tiangan_number(y_tg),
            calculate_tiangan_number(m_tg),
            calculate_tiangan_number(d_tg),
            calculate_tiangan_number(h_tg)
        ])

        dz_sum = sum([
            calculate_dizhi_number(y_dz),
            calculate_dizhi_number(m_dz),
            calculate_dizhi_number(d_dz),
            calculate_dizhi_number(h_dz)
        ])

        he_luo_num = calculate_he_luo(d_tg, d_dz)

        # 3. 天數成卦 + 地數成卦
        tian_gua = tian_shu_cheng_gua(tg_sum)
        di_gua = di_shu_cheng_gua(dz_sum)

        # 4. 八卦加則 → 基礎數字
        base_number = ba_gua_jia_ze(tian_gua + di_gua)

        # 5. 取得條文
        tiaowen_id = f"{1000 + base_number:04d}"
        tiaowen_text = self.tiaowen_db.get(tiaowen_id, "【條文待補充】")

        result: Dict[str, Any] = {
            "input": {
                "year": year_gz, "month": month_gz,
                "day": day_gz, "hour": hour_gz, "ke": ke
            },
            "base_number": base_number,
            "tiaowen_id": tiaowen_id,
            "tiaowen_text": tiaowen_text,
            "gua": get_peigua(d_tg, d_dz),
            "calculation": {
                "天干總數": tg_sum,
                "地支總數": dz_sum,
                "河洛數": he_luo_num,
                "天數成卦": tian_gua,
                "地數成卦": di_gua,
            }
        }

        # 6. 64鑰匙進階細調（實戰核心）
        if use_key and base_number in SHAOZI_64_KEYS:
            key_data = SHAOZI_64_KEYS[base_number]

            result["key"] = {
                "number": base_number,
                "名稱": key_data.get("名稱", ""),
                "特殊事項": key_data.get("特殊", []),
                "時辰資訊": get_key_info(base_number, ke=ke, category="時辰"),
                "運限資訊": get_key_info(base_number, ke=ke, category="運限"),
            }

            # 額外提供常用特殊事項快速判斷
            special = key_data.get("特殊", [])
            result["key"]["has_克妻"] = "克妻" in special
            result["key"]["has_過房"] = "過房" in special
            result["key"]["has_填房"] = "填房" in special
            result["key"]["has_貴子"] = "貴子" in special
            result["key"]["has_孤"] = "孤" in special

        return result

    def get_key_detail(self, number: int, ke: str = "初刻") -> Dict[str, Any]:
        """取得某數字的完整64鑰匙詳細資訊"""
        if number not in SHAOZI_64_KEYS:
            return {"error": f"第{number}數尚未結構化"}

        key_data = SHAOZI_64_KEYS[number]
        return {
            "number": number,
            "名稱": key_data.get("名稱", ""),
            "特殊事項": key_data.get("特殊", []),
            "時辰資訊": get_key_info(number, ke=ke, category="時辰"),
            "運限資訊": get_key_info(number, ke=ke, category="運限"),
            "完整資料": key_data
        }


# ====================== 5. 獨立測試 ======================

if __name__ == "__main__":
    print("=" * 60)
    print("邵子神數 進階起盤系統測試（含64鑰匙細調）")
    print("=" * 60)

    shaozi = ShaoziShenShu()

    result = shaozi.cast_plate(
        year_gz="甲子",
        month_gz="丙寅",
        day_gz="戊辰",
        hour_gz="庚午",
        ke="初刻"
    )

    print("\n【起盤結果】")
    print(f"基礎數字: {result['base_number']}")
    print(f"條文編號: {result['tiaowen_id']}")
    print(f"卦象: {result['gua']}")

    if "key" in result:
        print(f"\n【64鑰匙細調】")
        print(f"鑰匙名稱: {result['key']['名稱']}")
        print(f"特殊事項: {result['key']['特殊事項']}")
        print(f"時辰資訊: {result['key']['時辰資訊']}")
        print(f"是否有克妻: {result['key']['has_克妻']}")
        print(f"是否有貴子: {result['key']['has_貴子']}")

    print("\n測試完成！")
```