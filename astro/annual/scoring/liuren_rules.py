"""Declarative Liu Ren annual scoring rules."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LiurenRule:
    rule_id: str
    description: str
    score_delta: float
    tag: str


LIUREN_SCORING_RULES: tuple[LiurenRule, ...] = (
    LiurenRule("LR-SC-01", "初傳吉將", 8.0, "開年順遂"),
    LiurenRule("LR-SC-02", "初傳凶將", -10.0, "年初阻滯"),
    LiurenRule("LR-SC-03", "中末傳吉將", 5.0, "事態轉吉"),
    LiurenRule("LR-SC-04", "中末傳凶將", -6.0, "事態轉凶"),
    LiurenRule("LR-SC-05", "三傳皆吉", 15.0, "連環吉利"),
    LiurenRule("LR-SC-06", "三傳皆凶", -20.0, "連環不利"),
    LiurenRule("LR-SC-07", "傳中空亡", -8.0, "事多虛幻"),
    LiurenRule("LR-YS-01", "用神吉將", 12.0, "用神得力"),
    LiurenRule("LR-YS-02", "用神凶將", -10.0, "用神受制"),
    LiurenRule("LR-GJ-01", "上格", 12.0, "格局清貴"),
    LiurenRule("LR-GJ-02", "下格", -12.0, "格局不利"),
    LiurenRule("LR-GJ-03", "中格", 4.0, "格局平穩"),
    LiurenRule("LR-TS-01", "流年吉語", 4.0, "太歲助身"),
    LiurenRule("LR-TS-02", "流年凶語", -6.0, "太歲不利"),
    LiurenRule("LR-TS-03", "流年衝本命", -12.0, "動盪之年"),
    LiurenRule("LR-PG-01", "重點宮吉將", 8.0, "領域順遂"),
    LiurenRule("LR-PG-02", "重點宮凶將", -8.0, "領域波動"),
    LiurenRule("LR-LM-01", "論命吉格", 6.0, "祿命吉象"),
    LiurenRule("LR-LM-02", "論命凶格", -8.0, "祿命凶象"),
)

GOOD_GEJU_KEYWORDS = ("龍", "元首", "重審", "連珠", "間傳", "知一", "斫輪", "勝光")
BAD_GEJU_KEYWORDS = ("伏吟", "反吟", "涉害", "無依", "退連", "昴星", "別責")
GOOD_FLOW_WORDS = ("吉", "進益", "喜", "和順", "有助", "吉利", "通達")
BAD_FLOW_WORDS = ("凶", "災", "不利", "動盪", "衝", "疾病", "破財", "口舌")