# -*- coding: utf-8 -*-
"""
astro/kaiyuan/renderer.py — 開元占經 Streamlit 渲染模組

視覺風格：
  - 仿古宣紙質感（米白底色）
  - 書法字體（Noto Serif SC）
  - 傳統星占排版

主要函式：
    render_streamlit()
"""

from __future__ import annotations

import json
import pathlib
from typing import Any, Dict, List, Optional

import streamlit as st

from astro.i18n import auto_cn

# ─────────────────────────────────────────────────────────────────────────────
# 色彩常數
# ─────────────────────────────────────────────────────────────────────────────
_PAPER_BG = "#fdf8f0"
_SEAL_RED = "#8b1a1a"
_INK_DARK = "#1a1a2e"
_SUBTITLE = "#6b5e4e"
_BORDER = "#c4a882"
_GOLD = "#b8860b"

_DATA_DIR = pathlib.Path(__file__).parent

# ─────────────────────────────────────────────────────────────────────────────
# 資料載入
# ─────────────────────────────────────────────────────────────────────────────

def _load_json(filename: str) -> Any:
    path = _DATA_DIR / filename
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _load_five_planet_data() -> Dict[str, Dict[str, Any]]:
    """載入五星入宿占文，返回 {planet_name: {mansion: text}}"""
    file_map = {
        "歲星（木）": "wood_star.json",
        "熒惑（火）": "fire_star.json",
        "太白（金）": "gold_star.json",
        "填星（土）": "earth_star.json",
        "辰星（水）": "water_star.json",
    }
    result: Dict[str, Dict[str, Any]] = {}
    for label, fname in file_map.items():
        raw = _load_json(fname)
        # Each file has one top-level key (the planet canonical name)
        if isinstance(raw, dict):
            top_val = next(iter(raw.values())) if raw else {}
            result[label] = top_val if isinstance(top_val, dict) else {}
    return result


def _load_moon_28_mansion() -> Dict[str, Any]:
    raw = _load_json("moon_28_mansion.json")
    if isinstance(raw, dict):
        return next(iter(raw.values())) if raw else {}
    return {}


def _load_moon_five_stars() -> Dict[str, Any]:
    raw = _load_json("moon_in_five_stars.json")
    if isinstance(raw, dict):
        return next(iter(raw.values())) if raw else {}
    return {}


def _load_moon_attack_28() -> Dict[str, Any]:
    raw = _load_json("kaiyuan_moon_attack.json")
    if isinstance(raw, dict):
        return next(iter(raw.values())) if raw else {}
    return {}


def _load_sun_eclipse_month() -> Dict[str, Any]:
    raw = _load_json("kaiyuan_sun_elipse_month.json")
    if isinstance(raw, dict):
        return next(iter(raw.values())) if raw else {}
    return {}


def _load_sun_eclipse_gz() -> Dict[str, Any]:
    raw = _load_json("kaiyuan_sun_elipse_gz.json")
    if isinstance(raw, dict):
        return next(iter(raw.values())) if raw else {}
    return {}


def _load_five_star_general() -> Dict[str, Any]:
    raw = _load_json("kaiyuan_five_star_rep.json")
    if isinstance(raw, dict):
        return next(iter(raw.values())) if raw else {}
    return {}


def _load_five_sounds() -> Dict[str, Any]:
    return _load_json("five_sounds.json")


def _load_jiazi_five_sounds() -> Dict[str, Any]:
    return _load_json("jiazi_five_sounds.json")


# ─────────────────────────────────────────────────────────────────────────────
# 通用渲染輔助
# ─────────────────────────────────────────────────────────────────────────────

def _section_header(title: str) -> None:
    st.markdown(
        f"<h3 style='color:{_SEAL_RED};font-family:Noto Serif SC,serif;"
        f"letter-spacing:3px;border-bottom:2px solid {_BORDER};padding-bottom:6px;'>"
        f"{title}</h3>",
        unsafe_allow_html=True,
    )


def _omen_card(source: str, text: Any) -> None:
    """渲染一條占文卡片（source = 典籍名稱, text = 占文內容）"""
    if isinstance(text, list):
        text_html = "".join(
            f"<p style='margin:4px 0;'>{t_}</p>" for t_ in text
        )
    elif isinstance(text, dict):
        text_html = "".join(
            f"<p style='margin:4px 0;'><b>{k}：</b>{v}</p>"
            for k, v in text.items()
        )
    else:
        text_html = f"<p style='margin:4px 0;'>{text}</p>"

    st.markdown(
        f"<div style='background:{_PAPER_BG};border-left:3px solid {_SEAL_RED};"
        f"padding:10px 14px;border-radius:4px;margin-bottom:8px;'>"
        f"<b style='color:{_GOLD};font-family:Noto Serif SC,serif;font-size:14px;'>"
        f"【{source}】</b>"
        f"<div style='font-family:Noto Serif SC,serif;font-size:14px;color:{_INK_DARK};"
        f"margin-top:4px;'>{text_html}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )


def _render_dict_omens(data: Dict[str, Any]) -> None:
    """遞歸渲染占文字典（跳過空值）"""
    if not data:
        st.info(auto_cn("暫無資料"))
        return
    for source, text in data.items():
        if source == "歷史應驗":
            with st.expander(auto_cn("📜 歷史應驗")):
                if isinstance(text, list):
                    for item in text:
                        st.markdown(f"• {item}")
                else:
                    st.markdown(str(text))
        else:
            _omen_card(source, text)


# ─────────────────────────────────────────────────────────────────────────────
# 子頁面渲染
# ─────────────────────────────────────────────────────────────────────────────

def _render_five_planets_tab() -> None:
    """五星入宿占文查詢"""
    _section_header("🪐 五星入二十八宿占")
    st.caption(auto_cn("選擇行星與宿名，查閱《開元占經》原文占辭"))

    planet_data = _load_five_planet_data()
    planet_names = list(planet_data.keys())

    col1, col2 = st.columns(2)
    with col1:
        selected_planet = st.selectbox(
            auto_cn("行星"),
            planet_names,
            key="kaiyuan_planet_select",
        )
    with col2:
        mansions = list(planet_data.get(selected_planet, {}).keys())
        selected_mansion = st.selectbox(
            auto_cn("宿名"),
            mansions if mansions else ["（無資料）"],
            key="kaiyuan_mansion_select",
        )

    if st.button(auto_cn("查詢占文"), key="kaiyuan_planet_btn"):
        omen = planet_data.get(selected_planet, {}).get(selected_mansion)
        if omen:
            st.markdown(
                f"<h4 style='color:{_SEAL_RED};font-family:Noto Serif SC,serif;'>"
                f"{selected_planet} 入 {selected_mansion} 宿</h4>",
                unsafe_allow_html=True,
            )
            if isinstance(omen, dict):
                _render_dict_omens(omen)
            else:
                st.markdown(
                    f"<div style='background:{_PAPER_BG};padding:12px;border-radius:4px;"
                    f"font-family:Noto Serif SC,serif;font-size:15px;color:{_INK_DARK};'>"
                    f"{omen}</div>",
                    unsafe_allow_html=True,
                )
        else:
            st.warning(auto_cn("暫無此條目資料"))


def _render_moon_28_tab() -> None:
    """月犯二十八宿占（簡表）"""
    _section_header("🌙 月犯二十八宿占")
    st.caption(auto_cn("月亮經過二十八宿時的傳統占驗"))

    data = _load_moon_28_mansion()
    mansions = list(data.keys())
    if not mansions:
        st.info(auto_cn("暫無資料"))
        return

    selected = st.selectbox(
        auto_cn("宿名"),
        mansions,
        key="kaiyuan_moon28_select",
    )
    if st.button(auto_cn("查詢"), key="kaiyuan_moon28_btn"):
        omen = data.get(selected)
        if omen:
            st.markdown(
                f"<h4 style='color:{_SEAL_RED};font-family:Noto Serif SC,serif;'>"
                f"月犯 {selected} 宿</h4>",
                unsafe_allow_html=True,
            )
            if isinstance(omen, dict):
                _render_dict_omens(omen)
            else:
                st.markdown(str(omen))
        else:
            st.warning(auto_cn("暫無此條目資料"))


def _render_moon_attack_tab() -> None:
    """月犯二十八宿詳細占（kaiyuan_moon_attack）"""
    _section_header("🌙 月犯二十八宿詳占")
    st.caption(auto_cn("《開元占經》月犯二十八宿詳細占辭，含四方分組"))

    data = _load_moon_attack_28()
    if not data:
        st.info(auto_cn("暫無資料"))
        return

    # data is {region: {mansion: {source: text}}}
    for region, mansions in data.items():
        with st.expander(auto_cn(f"📌 {region}"), expanded=False):
            if not isinstance(mansions, dict):
                continue
            mansion_list = list(mansions.keys())
            sel = st.selectbox(
                auto_cn("宿名"),
                mansion_list,
                key=f"kaiyuan_attack_{region}",
            )
            omen = mansions.get(sel, {})
            if isinstance(omen, dict):
                _render_dict_omens(omen)
            else:
                st.markdown(str(omen))


def _render_moon_five_stars_tab() -> None:
    """月犯五星占"""
    _section_header("🌙 月犯五星占")
    st.caption(auto_cn("月亮與五大行星相犯的傳統占驗"))

    data = _load_moon_five_stars()
    if not data:
        st.info(auto_cn("暫無資料"))
        return

    # Show general section first
    if "總論" in data:
        with st.expander(auto_cn("📖 總論"), expanded=True):
            _render_dict_omens(data["總論"])

    planets = [k for k in data.keys() if k != "總論"]
    planet_map = {
        "歲星": "歲星（木）", "熒惑": "熒惑（火）", "太白": "太白（金）",
        "填星": "填星（土）", "辰星": "辰星（水）",
    }
    for p in planets:
        label = planet_map.get(p, p)
        with st.expander(auto_cn(f"🪐 月犯 {label}"), expanded=False):
            omen = data[p]
            if isinstance(omen, dict):
                _render_dict_omens(omen)
            else:
                st.markdown(str(omen))


def _render_sun_eclipse_tab() -> None:
    """日食占"""
    _section_header("☀️ 日食占")
    st.caption(auto_cn("《開元占經》日食逐月及干支占辭"))

    sub_tab1, sub_tab2 = st.tabs([
        auto_cn("按月份"),
        auto_cn("按干支"),
    ])

    with sub_tab1:
        month_data = _load_sun_eclipse_month()
        months = list(month_data.keys())
        if months:
            sel_month = st.selectbox(auto_cn("月份"), months, key="kaiyuan_sun_month_sel")
            if st.button(auto_cn("查詢"), key="kaiyuan_sun_month_btn"):
                omen = month_data.get(sel_month, {})
                st.markdown(
                    f"<h4 style='color:{_SEAL_RED};font-family:Noto Serif SC,serif;'>"
                    f"{sel_month} 日食</h4>",
                    unsafe_allow_html=True,
                )
                if isinstance(omen, dict):
                    _render_dict_omens(omen)
                else:
                    st.markdown(str(omen))
        else:
            st.info(auto_cn("暫無資料"))

    with sub_tab2:
        gz_data = _load_sun_eclipse_gz()
        # First entry may be general notes
        gz_keys = list(gz_data.keys())
        general_key = "甘氏总论" if "甘氏总论" in gz_data else None
        if general_key:
            with st.expander(auto_cn("📖 甘氏總論"), expanded=False):
                _render_dict_omens(gz_data[general_key])
            gz_keys = [k for k in gz_keys if k != general_key]

        if gz_keys:
            sel_gz = st.selectbox(auto_cn("干支"), gz_keys, key="kaiyuan_sun_gz_sel")
            if st.button(auto_cn("查詢"), key="kaiyuan_sun_gz_btn"):
                omen = gz_data.get(sel_gz, {})
                st.markdown(
                    f"<h4 style='color:{_SEAL_RED};font-family:Noto Serif SC,serif;'>"
                    f"{sel_gz} 日食</h4>",
                    unsafe_allow_html=True,
                )
                if isinstance(omen, dict):
                    _render_dict_omens(omen)
                else:
                    st.markdown(str(omen))
        else:
            st.info(auto_cn("暫無資料"))


def _render_five_sounds_tab() -> None:
    """五音法"""
    _section_header("🎵 五音法")
    st.caption(auto_cn("《開元占經》五音占風法與六十甲子納音"))

    sub1, sub2 = st.tabs([auto_cn("地十二辰五音法"), auto_cn("六十甲子五音")])

    with sub1:
        sounds_data = _load_five_sounds()
        # sections: 地十二辰五音法 / 李先生註 / 五音相動風占
        for section_name, section_data in sounds_data.items():
            with st.expander(auto_cn(f"📌 {section_name}"), expanded=(section_name == "地十二辰五音法")):
                if isinstance(section_data, dict):
                    for key, val in section_data.items():
                        if isinstance(val, dict):
                            st.markdown(
                                f"<b style='color:{_SEAL_RED};font-family:Noto Serif SC,serif;'>{key}</b>",
                                unsafe_allow_html=True,
                            )
                            cols = st.columns(3)
                            for i, (attr, v) in enumerate(val.items()):
                                with cols[i % 3]:
                                    if isinstance(v, list):
                                        st.markdown(f"**{attr}**：{'、'.join(str(x) for x in v)}")
                                    else:
                                        st.markdown(f"**{attr}**：{v}")
                        else:
                            st.markdown(f"**{key}**：{val}")
                else:
                    st.markdown(str(section_data))

    with sub2:
        jiazi_data = _load_jiazi_five_sounds()
        # 納音 and 總則
        nayin = jiazi_data.get("納音", {})
        zongze = jiazi_data.get("總則", {})

        if nayin:
            st.markdown(auto_cn("### 六十甲子納音分類"))
            for sound_type, gz_list in nayin.items():
                st.markdown(
                    f"<span style='color:{_SEAL_RED};font-family:Noto Serif SC,serif;"
                    f"font-weight:bold;'>{sound_type}</span>：{'　'.join(gz_list) if isinstance(gz_list, list) else gz_list}",
                    unsafe_allow_html=True,
                )
            st.markdown("---")

        if zongze:
            st.markdown(auto_cn("### 總則"))
            if isinstance(zongze, dict):
                for title, content in zongze.items():
                    with st.expander(auto_cn(f"📖 {title}"), expanded=False):
                        if isinstance(content, dict):
                            for src, text in content.items():
                                _omen_card(src, text)
                        else:
                            st.markdown(str(content))
            else:
                st.markdown(str(zongze))


def _render_five_star_general_tab() -> None:
    """五星總論"""
    _section_header("🌌 五星總論")
    st.caption(auto_cn("《開元占經》五星總論，集各家占辭"))

    data = _load_five_star_general()
    if not data:
        st.info(auto_cn("暫無資料"))
        return

    for section, content in data.items():
        with st.expander(auto_cn(f"📌 {section}"), expanded=False):
            if isinstance(content, dict):
                for src, text in content.items():
                    if isinstance(text, dict):
                        st.markdown(
                            f"<b style='color:{_GOLD};font-family:Noto Serif SC,serif;'>"
                            f"【{src}】</b>",
                            unsafe_allow_html=True,
                        )
                        for sub_src, sub_text in text.items():
                            _omen_card(sub_src, sub_text)
                    else:
                        _omen_card(src, text)
            else:
                st.markdown(str(content))


# ─────────────────────────────────────────────────────────────────────────────
# 主入口
# ─────────────────────────────────────────────────────────────────────────────

def render_streamlit() -> None:
    """開元占經 Streamlit 主渲染函式（不需出生資料，為查詢工具）"""
    # 標題
    st.markdown(
        f"<h2 style='color:{_SEAL_RED};font-family:Noto Serif SC,serif;"
        f"letter-spacing:4px;text-align:center;'>📜 開元占經 📜</h2>",
        unsafe_allow_html=True,
    )
    st.caption(auto_cn("唐·瞿曇悉達 撰 · 五星入宿 · 月占 · 日食占 · 五音法"))
    st.markdown("---")

    tabs = st.tabs([
        auto_cn("🪐 五星入宿"),
        auto_cn("🌙 月犯五星"),
        auto_cn("🌙 月犯廿八宿"),
        auto_cn("🌙 月犯廿八宿詳"),
        auto_cn("☀️ 日食占"),
        auto_cn("🎵 五音法"),
        auto_cn("🌌 五星總論"),
    ])

    with tabs[0]:
        _render_five_planets_tab()
    with tabs[1]:
        _render_moon_five_stars_tab()
    with tabs[2]:
        _render_moon_28_tab()
    with tabs[3]:
        _render_moon_attack_tab()
    with tabs[4]:
        _render_sun_eclipse_tab()
    with tabs[5]:
        _render_five_sounds_tab()
    with tabs[6]:
        _render_five_star_general_tab()
