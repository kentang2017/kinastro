"""Prompt templates for optional AI annual interpretation."""

from __future__ import annotations

from astro.annual.models import AnnualFlowYear, SolarReturnTimeline


ANNUAL_SR_SYSTEM_PROMPT = """你是一位精通大六壬祿命、紫微斗數、子平八字、七政四餘與西洋太陽回歸的資深命理師。
請根據結構化數據撰寫年度流年分析。
原則：
- 以大六壬為主（約 60%），紫微/八字/七政為輔，西洋 SR 僅作對照（約 10%）
- 不作絕對宿命論斷，使用「傾向」「可能」「宜」「忌」
- 引用具體盤象（三傳、用神、格局、太歲、流年宮、小限宮、七政大運）"""


def build_annual_year_prompt(
    timeline: SolarReturnTimeline,
    year: AnnualFlowYear,
    *,
    language: str = "bilingual",
) -> str:
    birth = timeline.natal_birth_data
    lr = year.liuren_jixiong
    ziwei = year.other_chinese_systems.get("ziwei")
    bazi = year.other_chinese_systems.get("bazi")
    qizheng = year.other_chinese_systems.get("qizheng")
    western = year.western_sr

    sections = [
        "## 命主資料",
        f"- 出生：{birth.year}-{birth.month:02d}-{birth.day:02d} {birth.hour:02d}:{birth.minute:02d} @ {birth.location_name}",
        f"- 本命年支：{timeline.benming_zhi}",
        f"- 虛歲：{year.age}",
        "",
        "## 本年度太陽回歸",
        f"- 精確時刻（當地）：{year.exact_sr_datetime_local}",
        f"- 日柱：{year.sr_day_gz}，時柱：{year.sr_hour_gz}",
        f"- 流年太歲：{year.liunian_zhi}（{year.liunian_gz}）",
        "",
        "## 大六壬課式",
        f"- 三傳：{lr.san_chuan_summary if lr else '—'}",
        f"- 用神：{lr.yong_shen if lr else '—'} / {lr.yong_shen_jiang if lr else '—'}",
        f"- 格局：{', '.join(lr.geju) if lr else '—'}",
        f"- 評分：{lr.score if lr else '—'}（{lr.level.value if lr else '—'}）",
        f"- 摘要：{lr.affair_summary if lr else '—'}",
        "",
        "## 紫微",
        ziwei.summary if ziwei else "—",
        "",
        "## 八字",
        bazi.summary if bazi else "—",
        "",
        "## 七政四餘",
        qizheng.summary if qizheng else "—",
        "",
        "## 西洋太陽回歸",
        western.summary if western else "—",
    ]
    if language == "bilingual":
        sections.append("")
        sections.append("請輸出：1.年度總論 2.大六壬核心斷語 3.分領域指引 4.多體系對照 5.實用建議 6. English Summary")
    return "\n".join(sections)