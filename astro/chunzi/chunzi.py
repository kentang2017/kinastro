"""
蠢子數纏度 (ChunZiShu Encampment Degree)
"""

import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict, Any
import re

class ChunZiShu:
    def __init__(self, data_path: str = "data/chunzi_verse.csv"):
        self.df = pd.read_csv(data_path, encoding='utf-8-sig')
        # 建立 code 快速索引
        self.code_index = self.df.set_index('code').to_dict('index')
        print(f"[ChunZiShu] 已載入 {len(self.df)} 筆詩詞資料")

    def get_verse(self, code: str) -> Optional[Dict[str, Any]]:
        """根據代碼查單條詩詞（最常用）"""
        code = code.strip()
        if code in self.code_index:
            row = self.code_index[code]
            return {
                "code": code,
                "category": row["category"],
                "star": row["star"],
                "degree": row["degree"],
                "branch": row["branch"],
                "verse": row["verse"],
                "mansion28": row.get("mansion28"),
                "seven_governors": row.get("seven_governors"),
            }
        return None

    def search(self, keyword: str, limit: int = 20) -> List[Dict[str, Any]]:
        """關鍵字搜尋詩詞（支援「未時生人」「先去父」「側室」「石皮」等）"""
        mask = self.df['verse'].str.contains(keyword, na=False, regex=False)
        results = self.df[mask].head(limit)
        return results.to_dict('records')

    def get_verses_by_hour(self, hour_branch: str, ke: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        依時辰 + 刻數找對應詩詞（目前用關鍵字模擬，之後可接考時法）
        例如：get_verses_by_hour('未', 3)
        """
        pattern = f"{hour_branch}時生人"
        if ke:
            # 可擴充更精確的刻數過濾
            pass
        mask = self.df['verse'].str.contains(pattern, na=False)
        return self.df[mask].to_dict('records')

    def batch_lookup(self, codes: List[str]) -> List[Dict[str, Any]]:
        """批量查詢多個代碼（起盤後最常用）"""
        results = []
        for code in codes:
            v = self.get_verse(code)
            if v:
                results.append(v)
            else:
                results.append({"code": code, "verse": "【資料庫中無此代碼】"})
        return results

    def interpret(self, code: str) -> str:
        """簡單結構化解讀（後續可加強 NLP 解析詩詞）"""
        v = self.get_verse(code)
        if not v:
            return f"找不到代碼：{code}"
        return f"""【{code}】
類別：{v['category']}　星曜：{v['star']}　度數：{v['degree']}　地支：{v['branch']}
詩詞：{v['verse']}
"""

# ==================== 使用範例 ====================
if __name__ == "__main__":
    czs = ChunZiShu("data/chunzi_verse.csv")

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