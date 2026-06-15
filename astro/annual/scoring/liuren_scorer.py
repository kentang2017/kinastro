"""Rule-based Liu Ren annual fortune scoring."""

from __future__ import annotations

from typing import Any

from astro.annual.models import LiurenJixiong, PalaceAffair, SanChuanReading
from astro.annual.scoring.levels import clamp_score, score_to_level
from astro.annual.scoring.liuren_rules import (
    BAD_FLOW_WORDS,
    BAD_GEJU_KEYWORDS,
    GOOD_FLOW_WORDS,
    GOOD_GEJU_KEYWORDS,
)
from astro.sanshi.lunming import JIANG_FULLNAME, JIANG_JIXI, TWELVE_PALACES, YUEJIANG_NAME

DIZHI = list("子丑寅卯辰巳午未申酉戌亥")
RI_GONG_MAP = {
    "甲": "寅", "乙": "辰", "丙": "巳", "丁": "未",
    "戊": "巳", "己": "未", "庚": "申", "辛": "戌",
    "壬": "亥", "癸": "丑",
}
KEY_PALACES = [
    "命宮", "兄弟宮", "夫妻宮", "子女宮",
    "財帛宮", "疾厄宮", "官祿宮", "相貌宮",
]
LUNMING_GOOD_WORDS = ("吉", "福", "喜", "進", "旺", "貴", "成", "順")
LUNMING_BAD_WORDS = ("凶", "災", "破", "病", "夭", "害", "剋", "阻")


def _jiang_jixiong(jiang: str) -> str:
    return JIANG_JIXI.get(jiang, "中")


def _parse_san_chuan(chart: dict[str, Any]) -> list[SanChuanReading]:
    san_chuan = chart.get("三傳", {})
    readings: list[SanChuanReading] = []
    for name in ("初傳", "中傳", "末傳"):
        vals = san_chuan.get(name, [])
        zhi = vals[0] if len(vals) > 0 else ""
        jiang = vals[1] if len(vals) > 1 else ""
        liuqin = vals[2] if len(vals) > 2 else ""
        kong = bool(len(vals) > 3 and vals[3] == "空")
        jixiong = _jiang_jixiong(jiang)
        note_parts = []
        if kong:
            note_parts.append("旬空")
        if jixiong == "吉":
            note_parts.append("吉將")
        elif jixiong == "凶":
            note_parts.append("凶將")
        readings.append(
            SanChuanReading(
                name=name,
                zhi=zhi,
                jiang=jiang,
                jiang_fullname=JIANG_FULLNAME.get(jiang, jiang),
                liuqin=liuqin,
                is_kong=kong,
                jixiong=jixiong if jixiong in {"吉", "凶"} else "中",
                note="、".join(note_parts),
            )
        )
    return readings


def _yong_shen(chart: dict[str, Any]) -> tuple[str, str, str]:
    day_gz = chart.get("_day_gz", chart.get("日期", "")[:2])
    ri_gan = day_gz[0] if day_gz else ""
    ri_gong = RI_GONG_MAP.get(ri_gan, "")
    di_to_tian = chart.get("地轉天盤", {})
    di_to_jiang = chart.get("地轉天將", {})
    yong = di_to_tian.get(ri_gong, "")
    jiang = di_to_jiang.get(ri_gong, "")
    return yong, jiang, ri_gong


def _palace_affairs(
    chart: dict[str, Any],
    benming_zhi: str,
) -> list[PalaceAffair]:
    if benming_zhi not in DIZHI:
        return []
    di_to_tian = chart.get("地轉天盤", {})
    di_to_jiang = chart.get("地轉天將", {})
    day_gz = chart.get("_day_gz", chart.get("日期", "")[:2])
    ri_gan = day_gz[0] if day_gz else ""
    start = DIZHI.index(benming_zhi)
    affairs: list[PalaceAffair] = []
    for idx, palace in enumerate(TWELVE_PALACES):
        branch = DIZHI[(start + idx) % 12]
        tian = di_to_tian.get(branch, "")
        jiang = di_to_jiang.get(branch, "")
        score = 50.0
        keywords: list[str] = []
        jx = _jiang_jixiong(jiang)
        if jx == "吉":
            score += 8
            keywords.append("吉將")
        elif jx == "凶":
            score -= 8
            keywords.append("凶將")
        if palace in KEY_PALACES and jx == "吉":
            score += 4
        summary = f"{palace}在{branch}，天盤{tian}，臨{JIANG_FULLNAME.get(jiang, jiang)}"
        affairs.append(
            PalaceAffair(
                palace=palace,
                branch=branch,
                tian_jiang=jiang,
                liuqin="",
                score=clamp_score(score),
                summary=summary,
                keywords=keywords,
            )
        )
    return affairs


def _extract_lunming_bonus(lunming: dict[str, Any]) -> tuple[float, list[str], list[str]]:
    """Scan 論命報告中的十二宮 / 二十四格 / 格局等文字，補充評分。"""
    bonus = 0.0
    opportunities: list[str] = []
    risks: list[str] = []
    sections = (
        lunming.get("十二宮"),
        lunming.get("二十四格"),
        lunming.get("格局論斷"),
        lunming.get("身命總則"),
    )
    for section in sections:
        if not section:
            continue
        texts: list[str] = []
        if isinstance(section, dict):
            for value in section.values():
                if isinstance(value, str):
                    texts.append(value)
                elif isinstance(value, list):
                    texts.extend(str(item) for item in value)
                elif isinstance(value, dict):
                    for nested in value.values():
                        if isinstance(nested, str):
                            texts.append(nested)
                        elif isinstance(nested, list):
                            texts.extend(str(item) for item in nested)
        elif isinstance(section, list):
            texts.extend(str(item) for item in section)
        elif isinstance(section, str):
            texts.append(section)

        for text in texts:
            if any(word in text for word in LUNMING_GOOD_WORDS):
                bonus += 3
                opportunities.append(text[:80])
            if any(word in text for word in LUNMING_BAD_WORDS):
                bonus -= 4
                risks.append(text[:80])
    return bonus, opportunities[:3], risks[:3]


def score_liuren_annual(
    chart: dict[str, Any],
    lunming: dict[str, Any],
    benming_zhi: str,
    liunian_zhi: str,
) -> LiurenJixiong:
    base = 50.0
    san_chuan = _parse_san_chuan(chart)
    for idx, reading in enumerate(san_chuan):
        weight = 1.0 if idx == 0 else 0.7
        if reading.jixiong == "吉":
            base += 8 * weight
        elif reading.jixiong == "凶":
            base -= (10 if idx == 0 else 6) * weight
        if reading.is_kong:
            base -= 8 * weight

    if san_chuan and all(r.jixiong == "吉" for r in san_chuan):
        base += 15
    if san_chuan and all(r.jixiong == "凶" for r in san_chuan):
        base -= 20

    yong, yong_jiang, ri_gong = _yong_shen(chart)
    yong_jixiong = _jiang_jixiong(yong_jiang)
    if yong_jixiong == "吉":
        base += 12
    elif yong_jixiong == "凶":
        base -= 10

    geju = list(chart.get("格局", []))
    geju_level = "無格"
    for pattern in geju:
        if any(key in pattern for key in GOOD_GEJU_KEYWORDS):
            base += 12
            geju_level = "上格"
        if any(key in pattern for key in BAD_GEJU_KEYWORDS):
            base -= 12
            geju_level = "下格"
    if geju and geju_level == "無格":
        geju_level = "中格"
        base += 4

    di_to_jiang = chart.get("地轉天將", {})
    liunian_jiang = di_to_jiang.get(liunian_zhi, "")
    taisui_parts: list[str] = []
    opportunities: list[str] = []
    risks: list[str] = []

    flow = lunming.get("流年壽夭", {})
    flow_comments = flow.get("流年禍福", []) if isinstance(flow, dict) else []
    for comment in flow_comments:
        taisui_parts.append(str(comment))
        if any(word in comment for word in GOOD_FLOW_WORDS):
            base += 4
            opportunities.append(str(comment))
        if any(word in comment for word in BAD_FLOW_WORDS):
            base -= 6
            risks.append(str(comment))

    if liunian_zhi and benming_zhi:
        chong_map = {
            "子": "午", "午": "子", "丑": "未", "未": "丑",
            "寅": "申", "申": "寅", "卯": "酉", "酉": "卯",
            "辰": "戌", "戌": "辰", "巳": "亥", "亥": "巳",
        }
        if chong_map.get(liunian_zhi) == benming_zhi:
            base -= 12
            risks.append(f"流年{liunian_zhi}衝本命{benming_zhi}")

    palace_affairs = _palace_affairs(chart, benming_zhi)
    for affair in palace_affairs:
        if affair.palace in KEY_PALACES:
            base += (affair.score - 50) * 0.08

    lunming_bonus, lm_opps, lm_risks = _extract_lunming_bonus(lunming)
    base += lunming_bonus
    opportunities.extend(lm_opps)
    risks.extend(lm_risks)

    yue_jiang = ""
    for zhi, name in YUEJIANG_NAME.items():
        tian_pan = chart.get("天地盤", {})
        if isinstance(tian_pan, dict) and tian_pan.get(zhi):
            yue_jiang = name
            break

    score = clamp_score(base)
    key_palaces = {
        affair.palace: affair.summary
        for affair in palace_affairs
        if affair.palace in KEY_PALACES
    }
    san_summary = " → ".join(
        f"{r.name}{r.zhi}({r.jiang_fullname or r.jiang})" for r in san_chuan
    )
    affair_summary = (
        f"三傳：{san_summary}。"
        f"用神{yong}臨{JIANG_FULLNAME.get(yong_jiang, yong_jiang)}。"
        f"流年太歲{liunian_zhi}。"
    )

    return LiurenJixiong(
        score=score,
        level=score_to_level(score),
        san_chuan=san_chuan,
        san_chuan_summary=san_summary,
        yong_shen=yong,
        yong_shen_palace=ri_gong,
        yong_shen_jiang=yong_jiang,
        yong_shen_jixiong=yong_jixiong if yong_jixiong in {"吉", "凶"} else "中",
        geju=geju,
        geju_level=geju_level,
        liunian_zhi=liunian_zhi,
        liunian_jiang=liunian_jiang,
        taisui_impact="；".join(taisui_parts[:5]),
        yue_jiang=yue_jiang,
        palace_affairs=palace_affairs,
        key_palaces=key_palaces,
        affair_summary=affair_summary,
        opportunities=opportunities[:5],
        risks=risks[:5],
        lunming_excerpt={
            "流年壽夭": flow,
            "格局": geju,
            "十二宮": lunming.get("十二宮", {}),
            "二十四格": lunming.get("二十四格", {}),
        },
    )