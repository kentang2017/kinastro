"""
astro/sanshi/taiyi.py — 太乙神數（命法）排盤模組
(Taiyi Shen Shu — Life Destiny Divination Module)

太乙神數為古代三式之一，主要用於推算天時國運及個人命運。
本模組主要顯示「太乙命法」部分，以出生年月日時計算命宮、身宮、
十二宮排列、陽九百六行限、出身卦及五柱卦象等。

此模組封裝 kintaiyi 庫，提供 compute / render 介面。
"""

from __future__ import annotations

import streamlit as st

from astro.i18n import auto_cn


def compute_taiyi_chart(
    year: int, month: int, day: int,
    hour: int, minute: int,
    gender: str = "male",
    timezone: float = 8.0,
    **kwargs,
) -> dict:
    """計算太乙神數命法排盤。

    Parameters
    ----------
    gender : str
        "male" / "男" 或 "female" / "女"

    Returns
    -------
    dict
        太乙命法完整排盤結果，包含 ``_chart_svg`` 鍵儲存生成的 SVG 圖表字串。
    """
    from kintaiyi.kintaiyi import Taiyi

    sex = "男" if gender in ("male", "男") else "女"
    t = Taiyi(year, month, day, hour, minute)
    result = t.taiyi_life(sex)
    try:
        result["_chart_svg"] = t.gen_life_gong(sex)
    except Exception:
        result["_chart_svg"] = None

    # ── 十二宮文字描述 ──
    try:
        life1 = t.gongs_discription(sex)
        life2 = t.twostar_disc(sex)
        result["_lifedisc"] = t.convert_gongs_text(life1, life2)
    except Exception:
        result["_lifedisc"] = None

    # ── 十六諸神落宮描述 ──
    try:
        result["_lifedisc2"] = t.stars_descriptions_text(3, 0)
    except Exception:
        result["_lifedisc2"] = None

    # ── 十六宮評分等級 ──
    try:
        result["_lifedisc3"] = t.sixteen_gong_grades(3, 0)
    except Exception:
        result["_lifedisc3"] = None

    # ── 陽九行限 / 百六行限 文字描述 ──
    try:
        result["_yangjiu_xx"] = t.yangjiu_xingxian(sex)
    except Exception:
        result["_yangjiu_xx"] = None

    try:
        result["_bailiu_xx"] = t.bailiu_xingxian(sex)
    except Exception:
        result["_bailiu_xx"] = None

    return result


def _render_svg(svg: str) -> None:
    """以 HTML 組件方式渲染太乙排盤 SVG 圖。"""
    import streamlit.components.v1 as components

    # Strip the XML declaration if present so the SVG embeds cleanly in HTML.
    if svg.startswith("<?xml"):
        svg = svg[svg.index("?>") + 2:].lstrip()

    html = (
        '<div style="display:flex;justify-content:center;align-items:center;">'
        + svg
        + "</div>"
    )
    components.html(html, height=480)


def _format_nested(d: dict, parent_key: str = "") -> str:
    """將巢狀字典格式化為可讀的 Markdown 文字。"""
    items: list[str] = []
    for k, v in d.items():
        full_key = f"{parent_key}{k}" if parent_key else k
        if isinstance(v, dict):
            items.append(_format_nested(v, full_key + ":").rstrip())
        elif isinstance(v, list):
            items.append(f"**{full_key}**：{', '.join(map(str, v))}")
        else:
            items.append(f"**{full_key}**：{v}")
    return "\n\n".join(items) + "\n\n"


def render_taiyi_chart(chart: dict, after_chart_hook=None):
    """在 Streamlit 中渲染太乙命法排盤結果。"""
    st.markdown(f"### 🌟 {auto_cn('太乙命法排盤')}")

    # ── SVG 排盤圖 ──
    svg = chart.get("_chart_svg")
    if svg:
        _render_svg(svg)
        st.divider()

    # ── 十二宮分析 ──
    lifedisc = chart.get("_lifedisc")
    if lifedisc:
        with st.expander(auto_cn("【十二宮分析】"), expanded=True):
            st.markdown(lifedisc)

    # ── 太乙十六神落宮 ──
    lifedisc2 = chart.get("_lifedisc2")
    if lifedisc2:
        with st.expander(auto_cn("【太乙十六神落宮】"), expanded=False):
            st.markdown(lifedisc2)

    # ── 太乙十六神上中下等 ──
    lifedisc3 = chart.get("_lifedisc3")
    if lifedisc3:
        with st.expander(auto_cn("【太乙十六神上中下等】"), expanded=False):
            st.markdown(lifedisc3)

    st.divider()

    # ── 基本資訊 ──
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(auto_cn("性別"), chart.get("性別", ""))
        st.metric(auto_cn("紀元"), chart.get("紀元", ""))
    with col2:
        st.metric(auto_cn("出生日期"), chart.get("出生日期", ""))
        st.metric(auto_cn("太歲"), chart.get("太歲", ""))
    with col3:
        gz = chart.get("出生干支", [])
        st.metric(auto_cn("出生干支"), " ".join(gz) if isinstance(gz, list) else str(gz))
        lunar = chart.get("農曆", {})
        if isinstance(lunar, dict):
            st.metric(auto_cn("農曆"), f"{lunar.get('年', '')}年{lunar.get('月', '')}月{lunar.get('日', '')}日")

    st.divider()

    # ── 命局 ──
    mingju = chart.get("命局", {})
    if isinstance(mingju, dict):
        st.markdown(f"#### {auto_cn('命局')}")
        mj_cols = st.columns(3)
        with mj_cols[0]:
            st.markdown(f"**{auto_cn('局式')}**：{mingju.get('文', '')}")
        with mj_cols[1]:
            st.markdown(f"**{auto_cn('局數')}**：{mingju.get('數', '')}")
        with mj_cols[2]:
            st.markdown(f"**{auto_cn('理天/理地')}**：{mingju.get('年', '')}")

    st.divider()

    # ── 命宮身宮 ──
    st.markdown(f"#### {auto_cn('安命宮 · 安身宮')}")
    mg_cols = st.columns(4)
    with mg_cols[0]:
        st.metric(auto_cn("安命宮"), chart.get("安命宮", ""))
    with mg_cols[1]:
        st.metric(auto_cn("安身宮"), chart.get("安身宮", ""))
    with mg_cols[2]:
        st.metric(auto_cn("飛祿"), chart.get("飛祿", ""))
    with mg_cols[3]:
        st.metric(auto_cn("飛馬"), chart.get("飛馬", ""))

    st.divider()

    # ── 卦象 ──
    st.markdown(f"#### {auto_cn('卦象')}")
    gua_keys = [
        ("出身卦", "出身卦"), ("年卦", "年卦"), ("月卦", "月卦"),
        ("日卦", "日卦"), ("時卦", "時卦"), ("分卦", "分卦"),
    ]
    gua_cols = st.columns(6)
    for i, (key, label) in enumerate(gua_keys):
        with gua_cols[i]:
            val = chart.get(key, "")
            st.metric(auto_cn(label), str(val))

    st.divider()

    # ── 太乙諸神 ──
    st.markdown(f"#### {auto_cn('太乙諸神')}")
    shen_keys = [
        ("太乙", "太乙"), ("天乙", "天乙"), ("地乙", "地乙"),
        ("四神", "四神"), ("直符", "直符"), ("始擊", "始擊"),
    ]
    shen_cols = st.columns(6)
    for i, (key, label) in enumerate(shen_keys):
        with shen_cols[i]:
            val = chart.get(key, "")
            st.metric(auto_cn(label), str(val))

    # ── 文昌 ──
    wenchang = chart.get("文昌", [])
    if isinstance(wenchang, list) and len(wenchang) >= 2:
        st.markdown(f"**{auto_cn('文昌')}**：{wenchang[0]}　{wenchang[1]}")

    st.divider()

    # ── 主客算 ──
    st.markdown(f"#### {auto_cn('主客算')}")
    calc_cols = st.columns(3)
    for ci, key in enumerate(["主算", "客算", "定算"]):
        with calc_cols[ci]:
            val = chart.get(key, [])
            if isinstance(val, list) and len(val) >= 2:
                st.markdown(f"**{auto_cn(key)}**：{val[0]}")
                if val[1]:
                    descs = val[1] if isinstance(val[1], list) else [val[1]]
                    for d in descs:
                        if d:
                            st.caption(str(d))
            else:
                st.markdown(f"**{auto_cn(key)}**：{val}")

    gen_cols = st.columns(6)
    for ci, key in enumerate(["主將", "主參", "客將", "客參", "合神", "計神"]):
        with gen_cols[ci]:
            st.metric(auto_cn(key), str(chart.get(key, "")))

    st.divider()

    # ── 基運 ──
    st.markdown(f"#### {auto_cn('君臣民基')}")
    base_cols = st.columns(3)
    for ci, key in enumerate(["君基", "臣基", "民基"]):
        with base_cols[ci]:
            st.metric(auto_cn(key), str(chart.get(key, "")))

    # ── 天盤 ──
    tianpan = chart.get("天盤", {})
    if tianpan:
        with st.expander(auto_cn("天盤"), expanded=False):
            import pandas as pd
            df = pd.DataFrame(
                [{"地支": k, "天盤": v} for k, v in tianpan.items()]
            )
            st.dataframe(df, width="stretch", hide_index=True)

    # ── 陽九百六行限 ──
    for key in ("陽九行限", "百六行限"):
        data = chart.get(key, {})
        if data:
            with st.expander(auto_cn(key), expanded=False):
                import pandas as pd
                df = pd.DataFrame(
                    [{"年齡段": k, "地支": v} for k, v in data.items()]
                )
                st.dataframe(df, width="stretch", hide_index=True)

    # ── 陽九行限描述 ──
    yangjiu_xx = chart.get("_yangjiu_xx")
    if yangjiu_xx:
        with st.expander(auto_cn("【陽九行限】"), expanded=False):
            st.markdown(_format_nested(yangjiu_xx))

    # ── 百六行限描述 ──
    bailiu_xx = chart.get("_bailiu_xx")
    if bailiu_xx:
        with st.expander(auto_cn("【百六行限】"), expanded=False):
            st.markdown(_format_nested(bailiu_xx))

    # ── 其他指標 ──
    extra_keys = ["定目", "五福", "帝符", "太尊", "飛鳥", "三風", "五風", "八風", "大游", "小游", "黑符"]
    extra_data = {k: chart.get(k) for k in extra_keys if chart.get(k) is not None}
    if extra_data:
        with st.expander(auto_cn("其他指標"), expanded=False):
            e_cols = st.columns(4)
            for i, (k, v) in enumerate(extra_data.items()):
                with e_cols[i % 4]:
                    st.metric(auto_cn(k), str(v))

    if after_chart_hook:
        after_chart_hook()
