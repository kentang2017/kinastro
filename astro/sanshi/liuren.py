"""
astro/sanshi/liuren.py — 大六壬排盤模組 (Da Liu Ren Divination Module)

大六壬為古代三式之一，以日干支及月將為基礎，
排列天地盤、四課、三傳，推斷吉凶。

此模組封裝 kinliuren 庫，提供 compute / render 介面。
"""

from __future__ import annotations

import sxtwl
import streamlit as st

from astro.i18n import t, auto_cn

# ============================================================
# 常量
# ============================================================

TIANGAN = list("甲乙丙丁戊己庚辛壬癸")
DIZHI = list("子丑寅卯辰巳午未申酉戌亥")

# 24 節氣名（sxtwl 的索引順序）
JIEQI_NAMES = [
    "小寒", "大寒", "立春", "雨水", "驚蟄", "春分",
    "清明", "穀雨", "立夏", "小滿", "芒種", "夏至",
    "小暑", "大暑", "立秋", "處暑", "白露", "秋分",
    "寒露", "霜降", "立冬", "小雪", "大雪", "冬至",
]

# 月份中文名（正月 ~ 十二月）
CHINESE_MONTHS = list("正二三四五六七八九十") + ["十一", "十二"]


def _get_jieqi(year: int, month: int, day: int) -> str:
    """根據公曆日期推算當前所在節氣。"""
    # 取得當年所有節氣日期
    jieqi_list = []
    for m in range(1, 13):
        for jq_type in (0, 1):  # 節, 氣
            jq_idx = (m - 1) * 2 + jq_type
            if jq_idx >= 24:
                break
            jd = sxtwl.fromSolar(year, m, 1)
            # Use sxtwl approach: iterate to find jieqi dates
    # Simplified approach: use month-based mapping
    # The jieqi of a given month is roughly predictable
    month_jieqi = {
        1: "小寒", 2: "立春", 3: "驚蟄", 4: "清明",
        5: "立夏", 6: "芒種", 7: "小暑", 8: "立秋",
        9: "白露", 10: "寒露", 11: "立冬", 12: "大雪",
    }
    # More precise: use sxtwl to get exact jieqi
    try:
        d = sxtwl.fromSolar(year, month, day)
        # Check current jieqi
        # Walk backwards from current day to find the most recent jieqi
        for offset in range(45):
            check = sxtwl.fromSolar(year, month, day)
            # sxtwl JD approach
            jd_val = check.getJD() - offset
            check_day = sxtwl.fromJD(jd_val)
            if check_day.hasJieQi():
                jq_idx = check_day.getJieQi()
                if 0 <= jq_idx < 24:
                    return JIEQI_NAMES[jq_idx]
    except Exception:
        pass
    return month_jieqi.get(month, "小寒")


def _get_gangzhi(year: int, month: int, day: int, hour: int) -> dict:
    """取得年月日時干支。"""
    d = sxtwl.fromSolar(year, month, day)
    gz_day = d.getDayGZ()

    day_tg = gz_day.tg
    day_dz = gz_day.dz
    day_gz = TIANGAN[day_tg] + DIZHI[day_dz]

    # 時干支
    hour_zhi_idx = ((hour + 1) // 2) % 12
    hour_tg = (day_tg * 2 + hour_zhi_idx) % 10
    hour_gz = TIANGAN[hour_tg] + DIZHI[hour_zhi_idx]

    # 農曆月
    lunar_month = d.getLunarMonth()

    return {
        "day_gz": day_gz,
        "hour_gz": hour_gz,
        "lunar_month": lunar_month,
    }


def compute_liuren_chart(
    year: int, month: int, day: int,
    hour: int, minute: int,
    timezone: float = 8.0,
    **kwargs,
) -> dict:
    """計算大六壬排盤。

    Returns
    -------
    dict
        包含三傳、四課、天地盤、格局等完整排盤資訊。
    """
    from kinliuren.kinliuren import Liuren

    gz = _get_gangzhi(year, month, day, hour)
    jieqi = _get_jieqi(year, month, day)
    lunar_month_str = CHINESE_MONTHS[gz["lunar_month"] - 1] if 1 <= gz["lunar_month"] <= 12 else "正"

    lr = Liuren(jieqi, lunar_month_str, gz["day_gz"], gz["hour_gz"])
    result = lr.result(0)
    result["_jieqi"] = jieqi
    result["_lunar_month"] = lunar_month_str
    result["_day_gz"] = gz["day_gz"]
    result["_hour_gz"] = gz["hour_gz"]
    return result


def render_liuren_chart(chart: dict, after_chart_hook=None):
    """在 Streamlit 中渲染大六壬排盤結果。"""
    st.markdown(f"### 🔮 {auto_cn('大六壬排盤')}")

    # ── 基本資訊 ──
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(auto_cn("節氣"), chart.get("_jieqi", ""))
    with col2:
        st.metric(auto_cn("農曆月"), chart.get("_lunar_month", ""))
    with col3:
        st.metric(auto_cn("日干支"), chart.get("_day_gz", ""))
    with col4:
        st.metric(auto_cn("時干支"), chart.get("_hour_gz", ""))

    st.divider()

    # ── 格局 ──
    geju = chart.get("格局", [])
    if geju:
        st.markdown(f"**{auto_cn('格局')}**：{'、'.join(geju) if isinstance(geju, list) else geju}")

    # ── 日馬 ──
    dayma = chart.get("日馬", "")
    if dayma:
        st.markdown(f"**{auto_cn('日馬')}**：{dayma}")

    st.divider()

    # ── 三傳 ──
    st.markdown(f"#### {auto_cn('三傳')}")
    san_chuan = chart.get("三傳", {})
    if san_chuan:
        sc_cols = st.columns(3)
        for i, (name, vals) in enumerate(san_chuan.items()):
            with sc_cols[i % 3]:
                if isinstance(vals, list) and len(vals) >= 3:
                    st.markdown(
                        f"**{auto_cn(name)}**\n\n"
                        f"- {auto_cn('地支')}：{vals[0]}\n"
                        f"- {auto_cn('天將')}：{vals[1]}\n"
                        f"- {auto_cn('六親')}：{vals[2]}\n"
                        + (f"- {auto_cn('旬空')}：{vals[3]}" if len(vals) > 3 and vals[3] else "")
                    )

    st.divider()

    # ── 四課 ──
    st.markdown(f"#### {auto_cn('四課')}")
    si_ke = chart.get("四課", {})
    if si_ke:
        sk_cols = st.columns(4)
        for i, (name, val) in enumerate(si_ke.items()):
            with sk_cols[i % 4]:
                if isinstance(val, list) and len(val) >= 1:
                    st.markdown(f"**{auto_cn(name)}**\n\n{val[0]}")
                    if len(val) > 1:
                        st.caption(val[1])
                else:
                    st.markdown(f"**{auto_cn(name)}**：{val}")

    st.divider()

    # ── 天地盤 ──
    st.markdown(f"#### {auto_cn('天地盤')}")
    tiandipal = chart.get("天地盤", {})
    if tiandipal:
        tp = tiandipal.get("天盤", [])
        dp = tiandipal.get("地盤", [])
        tj = tiandipal.get("天將", [])
        if tp and dp:
            import pandas as pd
            data = {"地盤": dp, "天盤": tp}
            if tj:
                data["天將"] = tj
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, hide_index=True)

    # ── 地轉天盤 / 地轉天將 ──
    for key in ("地轉天盤", "地轉天將"):
        mapping = chart.get(key, {})
        if mapping:
            with st.expander(auto_cn(key), expanded=False):
                import pandas as pd
                df = pd.DataFrame(
                    [{"地支": k, "對應": v} for k, v in mapping.items()]
                )
                st.dataframe(df, use_container_width=True, hide_index=True)

    if after_chart_hook:
        after_chart_hook()


# ============================================================
# 論命分析便利介面
# ============================================================

def compute_lunming(
    chart: dict,
    benming_zhi: str,
    liunian_zhi: str | None = None,
) -> dict:
    """對已排好的大六壬盤進行論命分析。

    Parameters
    ----------
    chart : dict
        ``compute_liuren_chart()`` 的回傳值。
    benming_zhi : str
        本命地支（如 ``'子'``）。
    liunian_zhi : str, optional
        流年地支，用於流年禍福分析。

    Returns
    -------
    dict
        完整結構化論命報告。
    """
    from astro.sanshi.lunming import LunMingAnalyzer

    analyzer = LunMingAnalyzer(chart, benming_zhi)
    report = analyzer.analyze_all()
    # 若有指定流年，重新分析流年部分
    if liunian_zhi:
        report["流年壽夭"] = analyzer.analyze_flow_year_month(liunian_zhi)
    return report


def render_lunming_report(report: dict) -> None:
    """在 Streamlit 中渲染論命分析報告。"""
    st.markdown(f"### 📜 {auto_cn('大六壬論命分析')}")

    # ── 身命總則 ──
    shenming = report.get("身命總則", {})
    if shenming:
        st.markdown(f"#### {auto_cn('身命總則')}")
        for section_name, section_data in shenming.items():
            if isinstance(section_data, dict):
                with st.expander(auto_cn(section_name), expanded=True):
                    for k, v in section_data.items():
                        if k == "論斷" and isinstance(v, list):
                            for comment in v:
                                st.markdown(f"- {comment}")
                        else:
                            st.markdown(f"**{auto_cn(k)}**：{v}")
            elif isinstance(section_data, list):
                with st.expander(auto_cn(section_name), expanded=False):
                    for item in section_data:
                        if isinstance(item, dict):
                            st.markdown(f"**{item.get('傳名', '')}**")
                            for k2, v2 in item.items():
                                if k2 == "傳名":
                                    continue
                                if k2 == "論斷" and isinstance(v2, list):
                                    for c in v2:
                                        st.markdown(f"  - {c}")
                                else:
                                    st.markdown(f"  - **{auto_cn(k2)}**：{v2}")
                        else:
                            st.markdown(f"- {item}")
            elif isinstance(section_data, str):
                st.info(section_data)

    st.divider()

    # ── 五節總決 ──
    five = report.get("五節總決", {})
    if five:
        st.markdown(f"#### {auto_cn('五節總決')}")
        for sec_name, sec_items in five.items():
            with st.expander(auto_cn(sec_name), expanded=False):
                if isinstance(sec_items, list):
                    for item in sec_items:
                        st.markdown(f"- {item}")
                else:
                    st.markdown(str(sec_items))

    st.divider()

    # ── 十二宮論 ──
    palaces = report.get("十二宮論", {})
    if palaces:
        st.markdown(f"#### {auto_cn('十二宮論')}")
        cols = st.columns(3)
        for i, (pname, pdata) in enumerate(palaces.items()):
            with cols[i % 3]:
                with st.expander(auto_cn(pname), expanded=False):
                    if isinstance(pdata, dict):
                        for k, v in pdata.items():
                            if k == "論斷" and isinstance(v, list):
                                for c in v:
                                    st.markdown(f"- {c}")
                            else:
                                st.markdown(f"**{auto_cn(k)}**：{v}")

    st.divider()

    # ── 二十四格 & 十六局 ──
    ge24 = report.get("二十四格", [])
    ju16 = report.get("十六局", [])
    if ge24 or ju16:
        st.markdown(f"#### {auto_cn('格局判斷')}")
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"**{auto_cn('二十四格')}**")
            if ge24:
                for g in ge24:
                    st.markdown(f"- {g}")
            else:
                st.caption(auto_cn("未入任何格"))
        with col_b:
            st.markdown(f"**{auto_cn('十六局')}**")
            if ju16:
                for j in ju16:
                    st.markdown(f"- {j}")
            else:
                st.caption(auto_cn("未入任何局"))

    st.divider()

    # ── 女命專論 ──
    female = report.get("女命專論", {})
    if female:
        with st.expander(auto_cn("女命專論"), expanded=False):
            for k, v in female.items():
                if isinstance(v, list):
                    for c in v:
                        st.markdown(f"- {c}")
                else:
                    st.markdown(f"**{auto_cn(k)}**：{v}")

    # ── 流年壽夭 ──
    flow = report.get("流年壽夭", {})
    if flow:
        st.markdown(f"#### {auto_cn('流年壽夭')}")
        for sec_name, sec_items in flow.items():
            with st.expander(auto_cn(sec_name), expanded=False):
                if isinstance(sec_items, list):
                    for item in sec_items:
                        st.markdown(f"- {item}")
                else:
                    st.markdown(str(sec_items))

