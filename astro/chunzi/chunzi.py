"""
蠢子數纏度 起盤與結構化解讀模組
"""

from __future__ import annotations
import pandas as pd
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
import re


@dataclass
class ChunZiVerse:
    code: str
    category: str
    star: str
    degree: int
    branch: str
    verse: str
    parents: Dict = field(default_factory=dict)
    spouse: Dict = field(default_factory=dict)
    children: Dict = field(default_factory=dict)
    career: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)


class ChunZiShu:
    def __init__(self, csv_path: str = "data/chunzi_verse.csv"):
        self.df = pd.read_csv(csv_path, encoding="utf-8-sig")
        self.code_index = self.df.set_index("code").to_dict("index")

    def get_verse(self, code: str) -> Optional[ChunZiVerse]:
        if code not in self.code_index:
            return None
        row = self.code_index[code]
        v = ChunZiVerse(
            code=code,
            category=row["category"],
            star=row["star"],
            degree=int(row["degree"]) if pd.notna(row["degree"]) else 0,
            branch=row["branch"],
            verse=row["verse"],
        )
        self._parse(v)
        return v

    def _parse(self, v: ChunZiVerse):
        text = v.verse
        # 父母
        if m := re.search(r"父[是命屬]*屬?([鼠牛虎兔龍蛇馬羊猴雞狗豬])", text):
            v.parents["father"] = m.group(1)
        if m := re.search(r"母[是命屬]*屬?([鼠牛虎兔龍蛇馬羊猴雞狗豬])", text):
            v.parents["mother"] = m.group(1)
        if "先去父" in text: v.parents["father_first"] = True
        if "母先" in text:   v.parents["mother_first"] = True

        # 妻宮
        if m := re.search(r"妻宮屬([鼠牛虎兔龍蛇馬羊猴雞狗豬])", text):
            v.spouse["zodiac"] = m.group(1)
        if "側室" in text: v.spouse["concubine"] = True
        if "再娶" in text: v.spouse["remarriage"] = True

        # 子息
        if m := re.search(r"生([一二三四五六])子", text):
            v.children["count"] = int(m.group(1))
        if "石皮" in text or "帶破" in text:
            v.children["stone_skin"] = True

        # 其他
        if any(kw in text for kw in ["折桂", "入泮", "封章"]):
            v.career.append("文業/科舉")
        if "刑冲" in text or "破財" in text:
            v.conflicts.append("刑沖破財")

    def batch_get(self, codes: List[str]) -> List[ChunZiVerse]:
        return [v for c in codes if (v := self.get_verse(c))]


class ChunZiChart:
    """一個完整命例"""
    def __init__(self, gender: str, bazi: str, ke: Optional[int] = None):
        self.gender = gender          # "坤" or "乾"
        self.bazi = bazi              # "丁丑 乙巳 甲子 辛未"
        self.ke = ke
        self.codes: List[str] = []
        self.verses: List[ChunZiVerse] = []
        self.analysis: Dict[str, Any] = {}

    def add_codes(self, codes: List[str], czs: ChunZiShu):
        self.codes = codes
        self.verses = czs.batch_get(codes)
        self._analyze()

    def _analyze(self):
        result = {
            "parents": {},
            "spouse": {},
            "children": {},
            "career": [],
            "conflicts": [],
            "verses": []
        }
        for v in self.verses:
            result["verses"].append({"code": v.code, "text": v.verse})
            result["parents"].update(v.parents)
            result["spouse"].update(v.spouse)
            result["children"].update(v.children)
            result["career"].extend(v.career)
            result["conflicts"].extend(v.conflicts)

        result["career"] = list(set(result["career"]))
        result["conflicts"] = list(set(result["conflicts"]))
        self.analysis = result

    def summary(self):
        print(f"\n【{self.gender}】{self.bazi}（{self.ke}刻）")
        print("代碼：", self.codes)
        print("父母：", self.analysis.get("parents"))
        print("妻宮：", self.analysis.get("spouse"))
        print("子息：", self.analysis.get("children"))
        print("事業：", self.analysis.get("career"))
        print("刑沖：", self.analysis.get("conflicts"))


# ==================== 使用範例 ====================
if __name__ == "__main__":
    czs = ChunZiShu("data/chunzi_verse.csv")

    # === 第一命例 ===
    chart1 = ChunZiChart("坤", "丁丑 乙巳 甲子 辛未", ke=3)
    chart1.add_codes(
        ["室巨9未", "角陰13酉", "柳計6巳", "虛陽7午", "女火5辰", "壁紫3未"],
        czs
    )
    chart1.summary()

    # === 第二命例（目前只能用已存在的代碼） ===
    chart2 = ChunZiChart("坤", "癸丑 壬戌 庚寅 丁丑", ke=6)
    chart2.add_codes(["畢龍6巳"], czs)   # 其他代碼在此版本不存在
    chart2.summary()
