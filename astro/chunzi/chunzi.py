# -*- coding: utf-8 -*-
"""
蠢子數纏度 (ChunZiShu / Encampment Degree)

基於 28 宿 + 七政四餘 + 度數的傳統詩詞式命理系統。
特別適用於女命婚姻、子息、父母、事業的交叉驗證。

資料來源：chunzi_verse.csv（4574 筆詩詞）
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

# 預設資料檔路徑（相對於本檔案）
_DEFAULT_DATA = Path(__file__).parent / "data" / "chunzi_verse.csv"

# 二十八宿完整列表（用於驗證）
MANSIONS_28 = [
    "角", "亢", "氐", "房", "心", "尾", "箕",   # 東方蒼龍
    "斗", "牛", "女", "虛", "危", "室", "壁",   # 北方玄武
    "奎", "婁", "胃", "昂", "畢", "嘴", "參",   # 西方白虎
    "井", "鬼", "柳", "星", "張", "翼", "軫",   # 南方朱雀
]

# 十二地支（用於解析時辰、父母屬相等）
BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 地支對應屬相
BRANCH_ZODIAC = {
    "子": "鼠", "丑": "牛", "寅": "虎", "卯": "兔",
    "辰": "龍", "巳": "蛇", "午": "馬", "未": "羊",
    "申": "猴", "酉": "雞", "戌": "狗", "亥": "豬",
}

# 屬相對應地支（反向查詢）
ZODIAC_BRANCH = {v: k for k, v in BRANCH_ZODIAC.items()}


class ChunZiShu:
    """蠢子數纏度查詢主類別。

    提供依代碼、28宿、關鍵字、多標籤等多種查詢方式，
    並支援詩詞結構化解析（父母屬相、妻宮、子息、壽元等）。

    Args:
        data_path: CSV 資料檔路徑，預設使用模組內建路徑。

    Example:
        >>> czs = ChunZiShu()
        >>> czs.get_verse("室巨9未")
        {'code': '室巨9未', 'verse': '...', ...}
    """

    def __init__(self, data_path: Optional[Path] = None) -> None:
        path = Path(data_path) if data_path else _DEFAULT_DATA
        if not path.exists():
            raise FileNotFoundError(f"[ChunZiShu] 找不到資料檔：{path}")
        self.df: pd.DataFrame = pd.read_csv(path, encoding="utf-8-sig")
        # 建立 code 快速索引（O(1) 查詢）
        # 部分代碼在資料庫中有多筆（不同詩詞），以第一筆為主索引
        _dedup = self.df.drop_duplicates(subset="code", keep="first")
        self.code_index: Dict[str, Dict] = _dedup.set_index("code").to_dict("index")

    # ------------------------------------------------------------------
    # 基礎查詢
    # ------------------------------------------------------------------

    def get_verse(self, code: str) -> Optional[Dict[str, Any]]:
        """根據代碼查單條詩詞（最常用入口）。

        Args:
            code: 詩詞代碼，例如 "室巨9未"、"角陰13酉"。

        Returns:
            包含全部欄位的字典，找不到時回傳 None。
        """
        code = code.strip()
        if code not in self.code_index:
            return None
        row = self.code_index[code]
        return {
            "code": code,
            "category": row.get("category"),
            "star": row.get("star"),
            "degree": row.get("degree"),
            "branch": row.get("branch"),
            "verse": row.get("verse"),
            "mansion28": row.get("mansion28"),
            "seven_governors": row.get("seven_governors"),
        }

    def search(self, keyword: str, limit: int = 20) -> List[Dict[str, Any]]:
        """單關鍵字全文搜尋詩詞。

        Args:
            keyword: 搜尋關鍵字，例如 "未時生人"、"先去父"、"側室"。
            limit: 最多回傳筆數，預設 20。

        Returns:
            符合條件的詩詞列表（每筆為完整欄位字典）。
        """
        mask = self.df["verse"].str.contains(keyword, na=False, regex=False)
        return self.df[mask].head(limit).to_dict("records")

    def get_verses_by_mansion(self, mansion: str) -> List[Dict[str, Any]]:
        """依 28 宿名稱查詢所有詩詞。

        Args:
            mansion: 28 宿名稱，例如 "室"、"角"、"柳"。

        Returns:
            屬於該宿的詩詞列表。若宿名無效則回傳空列表。
        """
        mansion = mansion.strip()
        # 同時搜尋 category 欄（主宿）與 mansion28 欄（交叉參照）
        mask = (
            self.df["category"].str.strip() == mansion
        ) | (
            self.df["mansion28"].str.strip() == mansion
        )
        results = self.df[mask].to_dict("records")
        return results

    def search_by_tags(self, tags: List[str], limit: int = 50) -> List[Dict[str, Any]]:
        """多關鍵字 AND 搜尋（所有標籤都必須出現在詩詞中）。

        Args:
            tags: 關鍵字列表，例如 ["未時生人", "先去父"]。
            limit: 最多回傳筆數，預設 50。

        Returns:
            同時包含所有關鍵字的詩詞列表。

        Example:
            >>> czs.search_by_tags(["未時生人", "先去父"])
        """
        if not tags:
            return []
        # 逐步縮小範圍：AND 邏輯
        mask = pd.Series([True] * len(self.df), index=self.df.index)
        for tag in tags:
            mask &= self.df["verse"].str.contains(tag, na=False, regex=False)
        return self.df[mask].head(limit).to_dict("records")

    def get_verses_by_hour(
        self, hour_branch: str, ke: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """依時辰（+ 刻數）查對應詩詞。

        目前以關鍵字「X時生人」匹配；刻數過濾預留 Hook，
        可由「考時法」（ChunZiInterpreter.determine_ke）擴充。

        Args:
            hour_branch: 時辰地支，例如 "未"、"子"、"寅"。
            ke: 刻數（1-10），目前為未來「考時法」預留，尚未實作精確過濾。

        Returns:
            符合時辰的詩詞列表。
        """
        pattern = f"{hour_branch}時生人"
        mask = self.df["verse"].str.contains(pattern, na=False)
        return self.df[mask].to_dict("records")

    def batch_lookup(self, codes: List[str]) -> List[Dict[str, Any]]:
        """批量查詢多個代碼（起盤後最常用）。

        Args:
            codes: 代碼列表，例如 ["室巨9未", "角陰13酉"]。

        Returns:
            每個代碼對應的結果列表；找不到的代碼會有明確提示。
        """
        results = []
        for code in codes:
            v = self.get_verse(code)
            if v:
                results.append(v)
            else:
                results.append({"code": code, "verse": f"【資料庫中無此代碼：{code}】"})
        return results

    def interpret(self, code: str) -> str:
        """格式化輸出單條詩詞（純文字顯示）。

        Args:
            code: 詩詞代碼。

        Returns:
            格式化後的文字輸出，找不到代碼時給出清楚提示。
        """
        v = self.get_verse(code)
        if not v:
            return (
                f"⚠️  找不到代碼：「{code}」\n"
                f"請確認格式，例如：室巨9未、角陰13酉、柳計6巳"
            )
        return (
            f"【{code}】\n"
            f"類別：{v['category']}　"
            f"星曜：{v['star']}　"
            f"度數：{v['degree']}　"
            f"地支：{v['branch']}\n"
            f"詩詞：{v['verse']}\n"
        )

    def explain(self, code: str) -> Dict[str, Any]:
        """嘗試從詩詞中結構化提取命理關鍵資訊。

        解析父母屬相、妻宮（或夫星）、子息數、出生時辰、
        壽元、刑沖克害等關鍵資訊。解析採正則表示式，
        無法確定的欄位以 None 回傳，不強行猜測。

        Args:
            code: 詩詞代碼，例如 "室巨9未"。

        Returns:
            結構化字典，包含以下欄位：
            - code (str)
            - verse (str)
            - father_zodiac (str|None)：父親屬相
            - mother_zodiac (str|None)：母親屬相
            - spouse_zodiac (str|None)：配偶屬相
            - children_count (int|None)：子息數
            - birth_hour (str|None)：出生時辰（地支）
            - birth_ke (int|None)：出生刻數
            - longevity (int|None)：壽元（歲）
            - flags (List[str])：特殊命理標記（克夫、刑沖等）

        Example:
            >>> czs.explain("室巨9未")
            {'code': '室巨9未', 'father_zodiac': '龍', ...}
        """
        v = self.get_verse(code)
        if not v:
            return {
                "code": code,
                "error": f"找不到代碼：「{code}」",
            }

        verse = v["verse"]
        result: Dict[str, Any] = {
            "code": code,
            "verse": verse,
            "father_zodiac": None,
            "mother_zodiac": None,
            "spouse_zodiac": None,
            "children_count": None,
            "birth_hour": None,
            "birth_ke": None,
            "longevity": None,
            "flags": [],
        }

        # ------ 父母屬相 ------
        # 父親：匹配「父是屬X」「父命屬X」「父親屬X」，X 後可接任意文字
        _zodiac_cls = r"[鼠牛虎兔龍蛇馬羊猴雞狗豬]"
        father_pat = rf"父(?:是屬|命屬|親屬|屬)({_zodiac_cls})"
        m = re.search(father_pat, verse)
        if m:
            result["father_zodiac"] = m.group(1)

        # 母親：匹配「母屬Y」「慈母屬Y」「母命屬Y」「母親屬Y」
        mother_pat = rf"(?:慈|親)?母(?:命屬|親屬|屬)({_zodiac_cls})"
        m = re.search(mother_pat, verse)
        if m:
            result["mother_zodiac"] = m.group(1)

        # ------ 配偶屬相 ------
        # 匹配：妻宮屬X / 夫星屬X / 妻星屬X / 配偶屬X
        spouse_pat = r"(?:妻宮|夫星|妻星|配偶)屬([鼠牛虎兔龍蛇馬羊猴雞狗豬])"
        m = re.search(spouse_pat, verse)
        if m:
            result["spouse_zodiac"] = m.group(1)

        # ------ 子息數 ------
        # 匹配：生X子 / 弄璋X / 結X果（果=子）
        child_patterns = [
            r"生([一二三四五六七八九十百兩\d]+)[個]?子",
            r"弄璋([一二三四五六七八九十\d]+)",
            r"結([一二三四五六七八九十\d]+)果",
            r"滿樹花開結([一二三四五六七八九十\d]+)果",
        ]
        chinese_num = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
                       "六": 6, "七": 7, "八": 8, "九": 9, "十": 10, "兩": 2}
        for pat in child_patterns:
            m = re.search(pat, verse)
            if m:
                raw = m.group(1)
                result["children_count"] = chinese_num.get(raw, int(raw) if raw.isdigit() else None)
                break

        # ------ 出生時辰 ------
        # 匹配：X時生人 / X時生見 / X時方生
        hour_pat = r"([子丑寅卯辰巳午未申酉戌亥])時(?:生人|生見|方生|出生)"
        m = re.search(hour_pat, verse)
        if m:
            result["birth_hour"] = m.group(1)

        # ------ 刻數 ------
        # 匹配：X刻生 / X刻交
        ke_pat = r"([一二三四五六七八九十\d]+)刻(?:生|交|中生)"
        m = re.search(ke_pat, verse)
        if m:
            raw = m.group(1)
            result["birth_ke"] = chinese_num.get(raw, int(raw) if raw.isdigit() else None)

        # ------ 壽元 ------
        # 匹配：壽享X歲 / X歲辭人世 / 壽X歲 / 壽X齡
        longevity_patterns = [
            r"壽享([七八九\d十百]+)歲",
            r"([七八九\d十百]+)歲(?:辭人世|齡|歲終)",
            r"壽至([七八九\d十百]+)",
        ]
        for pat in longevity_patterns:
            m = re.search(pat, verse)
            if m:
                raw = m.group(1)
                # 處理「七十八」→ 78
                longevity = _parse_chinese_number(raw)
                if longevity:
                    result["longevity"] = longevity
                break

        # ------ 特殊命理標記 ------
        flag_keywords = {
            "克夫": "克夫",
            "剋夫": "克夫",
            "克妻": "克妻",
            "剋妻": "克妻",
            "刑沖": "刑沖",
            "刑冲": "刑沖",
            "先去父": "先去父",
            "先剋去": "先去父",  # 「父是屬X先剋去」即先去父
            "先克去": "先去父",
            "先去母": "先去母",
            "父早亡": "父早亡",
            "母早亡": "母早亡",
            "側室": "側室",
            "繼室": "繼室",
            "再嫁": "再嫁",
            "再娶": "再娶",
            "石皮": "石皮（離異）",
            "破財": "破財",
            "官非": "官非",
            "孤剋": "孤剋",
            "無子": "無子",
        }
        flags = []
        for kw, label in flag_keywords.items():
            if kw in verse and label not in flags:
                flags.append(label)
        result["flags"] = flags

        return result


# ------------------------------------------------------------------
# 輔助函式
# ------------------------------------------------------------------

def _parse_chinese_number(text: str) -> Optional[int]:
    """將中文數字字串轉換為整數（簡易版，支援十百位）。

    Args:
        text: 中文數字，例如 "七十八"、"八十四"。

    Returns:
        對應整數，無法解析時回傳 None。
    """
    units = {"十": 10, "百": 100}
    digits = {
        "零": 0, "一": 1, "二": 2, "三": 3, "四": 4,
        "五": 5, "六": 6, "七": 7, "八": 8, "九": 9,
    }
    if text.isdigit():
        return int(text)
    # 簡易解析：X十Y 或 百X 格式
    m = re.match(r"([一二三四五六七八九]?)十([一二三四五六七八九]?)", text)
    if m:
        tens = digits.get(m.group(1), 1) if m.group(1) else 1
        ones = digits.get(m.group(2), 0) if m.group(2) else 0
        return tens * 10 + ones
    if text in digits:
        return digits[text]
    return None


# ==================== 使用範例 ====================
if __name__ == "__main__":
    czs = ChunZiShu()

    print("\n=== 第一命例：丁丑 乙巳 甲子 辛未（未時三刻）===")
    codes1 = ["室巨9未", "角陰13酉", "柳計6巳", "虛陽7午", "女火5辰"]
    for v in czs.batch_lookup(codes1):
        print(czs.interpret(v["code"]))

    print("\n=== 第二命例：癸丑 壬戌 庚寅 丁丑 ===")
    print("已知存在：畢龍6巳")
    print(czs.interpret("畢龍6巳"))

    print("\n=== 搜尋關鍵字範例 ===")
    results = czs.search("未時生人", limit=5)
    for r in results:
        print(f"{r['code']}: {r['verse'][:60]}...")

    print("\n=== 依 28 宿查詢（室宿）===")
    mansion_results = czs.get_verses_by_mansion("室")
    print(f"室宿詩詞共 {len(mansion_results)} 筆")

    print("\n=== 多標籤 AND 搜尋 ===")
    tag_results = czs.search_by_tags(["未時生人", "先去父"])
    print(f"同時含「未時生人」+「先去父」：{len(tag_results)} 筆")

    print("\n=== 結構化解析 ===")
    info = czs.explain("室巨9未")
    print(info)