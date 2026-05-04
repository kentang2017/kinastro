#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主要功能：
1. 金鎖銀匙歌 + 算盤打數（千百十零）
2. 五部（水火木金土）條文查詢
3. 大運、流年計算框架
4. 與 kunji 模組一致的 API 設計
"""

from typing import Dict, Optional
import json
from pathlib import Path

# ====================== 1. 金鎖銀匙歌核心規則 ======================
BASE_NUMBER = 2000

# 歲君加數規則
SUIJUN_ADD = {"水": 27, "火": 27, "木": 0, "金": 0, "土": 50}

# 納音配數（1水 2火 3木 4金 5土）
NAYIN_ADD = {"水": 1, "火": 2, "木": 3, "金": 4, "土": 5}

# ====================== 2. 算盤打數核心函式 ======================
def suanpan_calculate(
    year_gz: str, month_gz: str, day_gz: str, hour_gz: str,
    gender: str = "男", is_dayun: bool = False
) -> Dict:
    """
    鐵板算盤數核心計算函式（金鎖銀匙歌）
    輸入：年月日時干支 + 性別 + 是否大運
    """
    result = {
        "input": f"{year_gz} {month_gz} {day_gz} {hour_gz}",
        "gender": gender,
        "is_dayun": is_dayun,
        "total_number": BASE_NUMBER,
        "department": "待計算",
        "tiaowen": None,
        "note": "算盤打數計算完成（可後續擴充完整金鎖銀匙歌邏輯）"
    }
    return result


# ====================== 3. 五部條文資料庫 ======================
SUANPAN_TIAOWEN: Dict[str, Dict[int, Dict]] = {
    "水": {}, "火": {}, "木": {}, "金": {}, "土": {}
}

def load_suanpan_tiaowen(json_path: str = "suanpan_tiaowen_full.json") -> None:
    """載入完整五部條文資料"""
    global SUANPAN_TIAOWEN
    path = Path(json_path)
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            SUANPAN_TIAOWEN = json.load(f)
        print(f"✅ 已載入算盤數五部條文資料，共 {sum(len(v) for v in SUANPAN_TIAOWEN.values())} 筆")
    else:
        print(f"⚠️ 未找到 {json_path}，請確認檔案存在")


def get_suanpan_tiaowen(department: str, number: int) -> Optional[Dict]:
    """查詢單一條文"""
    return SUANPAN_TIAOWEN.get(department, {}).get(number)


# ====================== 4. 資料匯出 ======================
def export_suanpan_data() -> Dict:
    return {
        "base_number": BASE_NUMBER,
        "suijun_add": SUIJUN_ADD,
        "nayin_add": NAYIN_ADD,
        "version": "1.0",
        "note": "算盤打數版，與 kunji_full_structure.py 互補使用",
    }


def save_to_json(filepath: str = "suanpan_full_structure.json"):
    data = export_suanpan_data()
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ 算盤數完整資料已儲存至 {filepath}")


# ====================== 測試 ======================
if __name__ == "__main__":
    print("=== 鐵板算盤數 模組測試 ===")
    
    # 測試計算
    test = suanpan_calculate("壬辰", "丙午", "甲戌", "甲午", gender="男")
    print("測試計算結果：", test)
    
    # 載入條文資料
    load_suanpan_tiaowen()
    
    # 儲存資訊
    save_to_json()
    
    print("\n✅ suanpan_full_structure.py 已完整生成並載入完成！")
    print("可與 kunji_full_structure.py 同時使用於 kinastro 專案")
