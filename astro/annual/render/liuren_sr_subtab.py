"""Liuren solar-return annual sub-tab: lazy chart per virtual age (1–120)."""

from __future__ import annotations

from datetime import datetime

import streamlit as st

from astro.annual.natal_context import virtual_age
from astro.annual.timeline import compute_sr_liuren_for_virtual_age
from astro.models import BirthData
from astro.sanshi.liuren import render_liuren_chart, render_lunming_report
from core.cached_computations import _birth_sig, compute_sr_liuren_age_cached
from ui.helpers import t

MAX_VIRTUAL_AGE = 120


def _sr_year_for_age(birth_year: int, age: int) -> int:
    return birth_year + age - 1


def render_liuren_sr_annual_subtab(birth: BirthData, benming_zhi: str) -> None:
    """Render on-demand solar-return Liu Ren charts for virtual ages 1–120."""
    st.caption(
        "依出生地計算每年太陽回歸精確時刻，以該時刻起大六壬課式與祿命論年。"
        "僅在您選定虛歲並按「排盤」後才計算該年，不會一次跑完 120 年。"
    )

    ages = list(range(1, MAX_VIRTUAL_AGE + 1))
    current_age = min(max(virtual_age(birth.year, datetime.now().year), 1), MAX_VIRTUAL_AGE)
    default_index = current_age - 1

    col_age, col_btn = st.columns([4, 1])
    with col_age:
        selected_age = st.selectbox(
            "虛歲",
            options=ages,
            index=default_index,
            format_func=lambda age: (
                f"虛歲 {age} 歲（SR {_sr_year_for_age(birth.year, age)} 年）"
            ),
            key="liuren_sr_age_select",
        )
    with col_btn:
        st.write("")
        st.write("")
        run_chart = st.button("排盤", type="primary", key="liuren_sr_compute_btn")

    sr_year = _sr_year_for_age(birth.year, selected_age)
    birth_sig = _birth_sig(birth.to_compute_kwargs())
    cache_slot = f"liuren_sr::{birth_sig}::{selected_age}"

    if run_chart:
        with st.spinner(t("spinner_liuren_sr_annual")):
            flow_year = compute_sr_liuren_age_cached(birth_sig, selected_age, benming_zhi)
            st.session_state["liuren_sr_active_slot"] = cache_slot
            st.session_state[cache_slot] = flow_year

    active_slot = st.session_state.get("liuren_sr_active_slot")
    flow_year = st.session_state.get(cache_slot) if active_slot == cache_slot else None

    if flow_year is None:
        st.info(f"請選擇虛歲（1–{MAX_VIRTUAL_AGE}），再按「排盤」以顯示該年太陽回歸六壬盤。")
        return

    st.markdown(
        f"**虛歲 {selected_age} 歲｜SR {sr_year} 年｜太陽回歸：** "
        f"`{flow_year.exact_sr_datetime_local.strftime('%Y-%m-%d %H:%M:%S')}`"
    )
    if flow_year.sr_day_gz or flow_year.sr_hour_gz:
        st.caption(
            f"日干支 {flow_year.sr_day_gz or '—'}　"
            f"時干支 {flow_year.sr_hour_gz or '—'}　"
            f"流年 {flow_year.liunian_gz or '—'}"
        )

    if flow_year.liuren_chart:
        render_liuren_chart(
            flow_year.liuren_chart,
            benming_zhi=benming_zhi,
        )
    if flow_year.liuren_lunming:
        render_lunming_report(flow_year.liuren_lunming)