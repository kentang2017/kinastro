"""
蠢子數纏度 (ChunZiShu) 查詢與結構化解讀模組

"""

from __future__ import annotations
import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
import re

@dataclass
class ChunZiVerse:
    """單條詩詞的結構化物件"""
    code: str
    category: str
    star: str
    degree: int
    branch: str
    verse: str
    mansion28: Optional[str] = None
    seven_governors: Optional[str] = None

    # 結構化解析欄位
    parents: Dict[str, Any] = field(default_factory=dict)
    spouse: Dict[str, Any] = field(default_factory=dict)
    children: Dict[str, Any] = field(default_factory=dict)
    career: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)
    lifespan_hint: Optional[str] = None

class ChunZiShu:
    def __init__(self, csv_path: str = "data/chunzi_verse.csv"):
        self.df = pd.read_csv(csv_path, encoding="utf-8-sig")
        self.code_index = self.df.set_index("code").to_dict("index")
        print(f"[ChunZiShu] 已載入 {len(self.df)} 筆資料")

    # ==================== 基礎查詢 ====================
    def get_verse(self, code: str) -> Optional[ChunZiVerse]:
        """根據代碼取得單條結構化詩詞"""
        code = code.strip()
        if code not in self.code_index:
            return None

        row = self.code_index[code]
        verse = ChunZiVerse(
            code=code,
            category=row["category"],
            star=row["star"],
            degree=int(row["degree"]) if pd.notna(row["degree"]) else 0,
            branch=row["branch"],
            verse=row["verse"],
            mansion28=row.get("mansion28"),
            seven_governors=row.get("seven_governors"),
        )
        self._parse_verse(verse)
        return verse

    def batch_get(self, codes: List[str]) -> List[ChunZiVerse]:
        return [v for c in codes if (v := self.get_verse(c))]

    def search(self, keywords: List[str] | str, limit: int = 30) -> List[ChunZiVerse]:
        """多關鍵字 AND 搜尋"""
        if isinstance(keywords, str):
            keywords = [keywords]

        mask = pd.Series(True, index=self.df.index)
        for kw in keywords:
            mask &= self.df["verse"].str.contains(kw, na=False, regex=False)

        results = []
        for _, row in self.df[mask].head(limit).iterrows():
            if v := self.get_verse(row["code"]):
                results.append(v)
        return results

    # ==================== 結構化解析（核心強化） ====================
    def _parse_verse(self, v: ChunZiVerse) -> None:
        text = v.verse

        # 父母屬相 + 生死順序
        if m := re.search(r"父[是命屬]*屬?([鼠牛虎兔龍蛇馬羊猴雞狗豬])", text):
            v.parents["father"] = m.group(1)
        if m := re.search(r"母[是命屬]*屬?([鼠牛虎兔龍蛇馬羊猴雞狗豬])", text):
            v.parents["mother"] = m.group(1)
        if "先去父" in text or "父先" in text:
            v.parents["father_first"] = True
        if "母先" in text:
            v.parents["mother_first"] = True

        # 妻宮 / 婚姻
        if m := re.search(r"妻宮屬([鼠牛虎兔龍蛇馬羊猴雞狗豬])", text):
            v.spouse["zodiac"] = m.group(1)
        if "側室" in text:
            v.spouse["has_concubine"] = True
        if "再娶" in text or "重婚" in text:
            v.spouse["remarriage"] = True

        # 子息
        if m := re.search(r"生([一二三四五六七八九])子", text):
            v.children["count"] = int(m.group(1))
        if "石皮" in text or "帶破" in text:
            v.children["has_stone_skin"] = True

        # 事業提示
        if any(kw in text for kw in ["折桂", "入泮", "封章", "魁捷", "青雲"]):
            v.career.append("科舉/文業")
        if "手藝" in text:
            v.career.append("手藝四方")

        # 刑沖與壽元提示
        if "刑冲" in text or "破財" in text:
            v.conflicts.append("刑沖破財")
        if "一枕南柯" in text or "命歸" in text:
            v.lifespan_hint = "有壽元記載"

    # ==================== 綜合分析 ====================
    def analyze_codes(self, codes: List[str]) -> Dict[str, Any]:
        """對多個代碼進行綜合分析（適合命例使用）"""
        verses = self.batch_get(codes)
        if not verses:
            return {"error": "找不到有效代碼"}

        result: Dict[str, Any] = {
            "codes": [v.code for v in verses],
            "parents": {},
            "spouse": {},
            "children": {},
            "career": [],
            "conflicts": [],
            "verses": []
        }

        for v in verses:
            result["verses"].append({"code": v.code, "text": v.verse})
            if v.parents:
                result["parents"].update(v.parents)
            if v.spouse:
                result["spouse"].update(v.spouse)
            if v.children:
                result["children"].update(v.children)
            result["career"].extend(v.career)
            result["conflicts"].extend(v.conflicts)

        # 去重
        result["career"] = list(set(result["career"]))
        result["conflicts"] = list(set(result["conflicts"]))
        return result

# ==================== 快速測試 ====================
if __name__ == "__main__":
    czs = ChunZiShu("data/chunzi_verse.csv")

    print("=== 第一命例結構化分析 ===")
    codes1 = ["室巨9未", "角陰13酉", "柳計6巳", "虛陽7午", "女火5辰"]
    print(czs.analyze_codes(codes1))

    print("\n=== 搜尋「未時生人」+「先去父」 ===")
    results = czs.search(["未時生人", "先去父"], limit=5)
    for r in results:
        print(f"{r.code}: {r.verse[:50]}...")
