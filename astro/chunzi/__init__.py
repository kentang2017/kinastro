# -*- coding: utf-8 -*-
"""
astro/chunzi/__init__.py — 蠢子數模組公開介面

蠢子數（ChunZiShu）是以 28 宿 + 七政四餘 + 度數為核心的傳統詩詞命理系統，
特別擅長女命婚姻、子息、父母、事業的交叉驗證。

資料來源：data/chunzi_verse.csv（4574 筆詩詞）
"""

from .chunzi import (
    BRANCHES,
    BRANCH_ZODIAC,
    MANSIONS_28,
    ZODIAC_BRANCH,
    ChunZiShu,
)

__all__ = [
    "ChunZiShu",
    "MANSIONS_28",
    "BRANCHES",
    "BRANCH_ZODIAC",
    "ZODIAC_BRANCH",
]
