"""Cached computation wrappers for KinAstro.

All ``@st.cache_data`` / ``@st.cache_resource`` wrappers live here so
they can be shared across the thin ``app.py`` and system-handler modules
without circular imports.

Lazy import policy
------------------
The astro compute modules are *only* imported on first call to the
matching wrapper. This is critical: importing this module was the
biggest cold-start cost in the whole project (≈1.1s out of 1.5s
total) because it eagerly pulled in 44 astro submodules. Each
wrapper now does ``from astro.<x> import <fn> as _fn`` inside its
body so the cost is paid only when the user actually visits the
matching tab. ``app.py`` and the 5 system handlers import only a few
named wrappers, so the wrappers themselves are cheap.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import streamlit as st


# ── Key helpers (module-level: tiny, no astro deps) ──────────────────────────

_BIRTH_KEY_FIELDS = ("year", "month", "day", "hour", "minute", "latitude", "longitude", "timezone")


def _birth_sig(params: dict[str, Any]) -> tuple[Any, ...]:
    return tuple(params[k] for k in _BIRTH_KEY_FIELDS)


def _to_hashable(value: Any):
    if isinstance(value, dict):
        return tuple(sorted((k, _to_hashable(v)) for k, v in value.items()))
    if isinstance(value, (list, tuple, set)):
        return tuple(_to_hashable(v) for v in value)
    return value


def _options_sig(options: dict[str, Any] | None = None) -> tuple[tuple[str, Any], ...]:
    if not options:
        return tuple()
    return tuple(sorted((key, _to_hashable(val)) for key, val in options.items()))


def _system_cache_key(system_name: str, params: dict[str, Any], options: dict[str, Any] | None = None) -> tuple[Any, ...]:
    return (system_name, _birth_sig(params), _options_sig(options))


# ── Resource caches ──────────────────────────────────────────────────────────

@st.cache_resource(show_spinner=False)
def get_swe():
    import swisseph as swe
    return swe


@st.cache_resource(show_spinner=False)
def get_ptolemy_calculator():
    from astro.western.ptolemy_dignities import PtolemyDignityCalculator
    return PtolemyDignityCalculator()


@st.cache_resource(show_spinner=False)
def get_wanhua_tool():
    from astro.chinstar.chinstar import WanHuaXianQin
    return WanHuaXianQin()


# ── Data caches ──────────────────────────────────────────────────────────────

@st.cache_data(ttl=3600, show_spinner=False)
def compute_taixuan_natal_cached(year: int, month: int, day: int, hour: int):
    from astro.chinese.taixuan import TaiXuanCalculator
    return TaiXuanCalculator(year=year, month=month, day=day, hour=hour, mode="natal").calculate()


@st.cache_data(ttl=3600, show_spinner=False)
def compute_system_cached(system_name: str, birth_sig: tuple[Any, ...], options_sig: tuple[tuple[str, Any], ...]):
    from astro.qizheng.calculator import compute_chart as _compute_chart
    from astro.western.western import compute_western_chart as _compute_western_chart
    from astro.vedic.indian import compute_vedic_chart as _compute_vedic_chart
    from astro.thai import compute_thai_chart as _compute_thai_chart
    from astro.ziwei import compute_ziwei_chart as _compute_ziwei_chart
    from astro.cetian_ziwei import compute_cetian_ziwei_chart as _compute_cetian_ziwei_chart
    from astro.jewish_mazzalot import compute_mazzalot_chart as _compute_mazzalot_chart
    year, month, day, hour, minute, latitude, longitude, timezone = birth_sig
    options = dict(options_sig)
    common_kwargs = dict(
        year=year, month=month, day=day, hour=hour, minute=minute,
        latitude=latitude, longitude=longitude, timezone=timezone,
        location_name=options.get("location_name", ""),
    )
    if system_name == "tab_chinese":
        return _compute_chart(**common_kwargs, gender=options.get("gender", "male"))
    if system_name == "tab_western":
        return _compute_western_chart(**common_kwargs, sidereal=bool(options.get("sidereal", False)))
    if system_name == "tab_indian":
        return _compute_vedic_chart(**common_kwargs)
    if system_name == "tab_thai":
        return _compute_thai_chart(**common_kwargs)
    if system_name == "tab_ziwei":
        return _compute_ziwei_chart(
            **common_kwargs,
            gender=options.get("gender", "male"),
            vietnam_mode=bool(options.get("vietnam_mode", False)),
        )
    if system_name == "tab_cetian_ziwei":
        return _compute_cetian_ziwei_chart(**common_kwargs, gender=options.get("gender", "male"))
    if system_name == "tab_mazzalot":
        return _compute_mazzalot_chart(
            year=year, month=month, day=day, hour=hour, minute=minute,
            timezone=timezone, lat=latitude, lon=longitude,
        )
    raise ValueError(f"Unsupported cached system: {system_name}")


def get_or_compute_chart(system_name: str, params: dict[str, Any], options: dict[str, Any] | None = None):
    """Get a cached chart, computing it if not already cached."""
    store = st.session_state.setdefault("_chart_cache_by_system", {})
    key = _system_cache_key(system_name, params, options)
    if key not in store:
        store[key] = compute_system_cached(system_name, _birth_sig(params), _options_sig(options))
    return store[key]


def invalidate_chart_cache_if_birth_changed(params: dict[str, Any]) -> None:
    """Clear session-state chart caches when birth data changes."""
    new_sig = _birth_sig(params)
    old_sig = st.session_state.get("_last_birth_sig")
    if old_sig != new_sig:
        st.session_state["_chart_cache_by_system"] = {}
        st.session_state["_render_cache_by_system"] = {}
        st.session_state["_last_birth_sig"] = new_sig


@st.cache_data(ttl=3600, show_spinner=False)
def compute_transit_now_cached(timezone: float):
    from astro.qizheng.qizheng_transit import compute_transit_now as _fn
    return _fn(timezone=timezone)


@st.cache_data(ttl=3600, show_spinner=False)
def compute_shensha_cached(
    chart_key: tuple[Any, ...],
    *,
    year: int,
    solar_month: int,
    julian_day: float,
    hour_branch: str,
    timezone: float,
    ming_gong_branch: str,
):
    from astro.qizheng.shensha import compute_shensha as _fn
    _ = chart_key
    return _fn(
        year=year, solar_month=solar_month, julian_day=julian_day,
        hour_branch=hour_branch, timezone=timezone, ming_gong_branch=ming_gong_branch,
    )


@st.cache_data(ttl=3600, show_spinner=False)
def compute_dasha_cached(
    chart_key: tuple[Any, ...],
    *,
    birth_year: int,
    ming_gong_branch: str,
    gender: str,
    houses,
    current_year: int,
):
    from astro.qizheng.qizheng_dasha import compute_dasha as _fn
    _ = chart_key
    return _fn(
        birth_year=birth_year, ming_gong_branch=ming_gong_branch,
        gender=gender, houses=houses, current_year=current_year,
    )


@st.cache_data(ttl=3600, show_spinner=False)
def compute_transit_cached(*, year: int, month: int, day: int, hour: int, minute: int, timezone: float):
    from astro.qizheng.qizheng_transit import compute_transit as _fn
    return _fn(year=year, month=month, day=day, hour=hour, minute=minute, timezone=timezone)


@st.cache_data(ttl=3600, show_spinner=False)
def compute_zhangguo_cached(chart_key: tuple[Any, ...], planets, houses, gender: str):
    from astro.qizheng.zhangguo import compute_zhangguo as _fn
    _ = chart_key
    return _fn(planets=planets, houses=houses, gender=gender)


@st.cache_data(ttl=3600, show_spinner=False)
def compute_western_transits_cached(
    birth_sig: tuple[Any, ...],
    sidereal: bool,
    location_name: str,
    t_year: int, t_month: int, t_day: int, t_hour: int, t_minute: int,
):
    from astro.western.western_transit import compute_western_transits as _fn
    _, _, _, _, _, _, _, timezone = birth_sig
    natal = compute_system_cached("tab_western", birth_sig, _options_sig({"sidereal": sidereal, "location_name": location_name}))
    return _fn(natal, t_year, t_month, t_day, t_hour, t_minute, timezone)


@st.cache_data(ttl=3600, show_spinner=False)
def compute_solar_return_cached(
    sun_longitude: float,
    return_year: int,
    latitude: float,
    longitude: float,
    timezone: float,
    location_name: str,
):
    from astro.western.western_return import compute_solar_return as _fn
    return _fn(sun_longitude, return_year, latitude, longitude, timezone, location_name)


@st.cache_data(ttl=3600, show_spinner=False)
def compute_synastry_cached(
    natal_sig: tuple[Any, ...],
    sidereal: bool,
    location_name: str,
    b_year: int, b_month: int, b_day: int, b_hour: int, b_minute: int,
    b_tz: float, b_lat: float, b_lon: float, b_location_name: str,
):
    from astro.western.western import compute_western_chart as _wc
    from astro.western.western_synastry import compute_synastry as _fn
    natal = compute_system_cached("tab_western", natal_sig, _options_sig({"sidereal": sidereal, "location_name": location_name}))
    w_b = _wc(
        year=b_year, month=b_month, day=b_day, hour=b_hour, minute=b_minute,
        timezone=b_tz, latitude=b_lat, longitude=b_lon,
        location_name=b_location_name, sidereal=sidereal,
    )
    return _fn(natal, w_b, "Person A", "Person B")


@st.cache_data(ttl=3600, show_spinner=False)
def compute_love_synastry_cached(
    natal_sig: tuple[Any, ...],
    sidereal: bool,
    location_name: str,
    name_a: str,
    b_year: int, b_month: int, b_day: int, b_hour: int, b_minute: int,
    b_tz: float, b_lat: float, b_lon: float, b_location_name: str,
    name_b: str,
):
    from astro.western.western import compute_western_chart as _wc
    from astro.western.western_love_synastry import compute_love_synastry as _fn
    natal = compute_system_cached("tab_western", natal_sig, _options_sig({"sidereal": sidereal, "location_name": location_name}))
    w_b = _wc(
        year=b_year, month=b_month, day=b_day, hour=b_hour, minute=b_minute,
        timezone=b_tz, latitude=b_lat, longitude=b_lon,
        location_name=b_location_name, sidereal=sidereal,
    )
    return _fn(natal, w_b, name_a, name_b)


@st.cache_data(ttl=3600, show_spinner=False)
def compute_vimshottari_cached(moon_longitude: float, julian_day: float):
    from astro.vedic.vedic_dasha import compute_vimshottari as _fn
    return _fn(moon_longitude, julian_day)


@st.cache_data(ttl=3600, show_spinner=False)
def compute_yogini_cached(moon_longitude: float, julian_day: float):
    from astro.vedic.vedic_dasha import compute_yogini as _fn
    return _fn(moon_longitude, julian_day)


@st.cache_data(ttl=3600, show_spinner=False)
def compute_ashtakavarga_cached(p_lons_items: tuple[tuple[str, float], ...], asc_lon: float):
    from astro.vedic.ashtakavarga import compute_ashtakavarga as _fn
    return _fn(dict(p_lons_items), asc_lon)


@st.cache_data(ttl=3600, show_spinner=False)
def compute_yogas_cached(p_lons_items: tuple[tuple[str, float], ...], asc_lon: float):
    from astro.vedic.vedic_yogas import compute_yogas as _fn
    return _fn(dict(p_lons_items), asc_lon)


@st.cache_data(ttl=3600, show_spinner=False)
def compute_bphs_cached(birth_sig: tuple[Any, ...], location_name: str):
    from astro.vedic.bphs_engine import compute_bphs as _fn
    v_chart = compute_system_cached("tab_indian", birth_sig, _options_sig({"location_name": location_name}))
    return _fn(v_chart.planets, v_chart.houses, v_chart.ascendant)


@st.cache_data(ttl=3600, show_spinner=False)
def compute_varga_cached(varga_key: str, birth_sig: tuple[Any, ...], location_name: str):
    from astro.vedic.varga import compute_varga_chart as _fn
    v_chart = compute_system_cached("tab_indian", birth_sig, _options_sig({"location_name": location_name}))
    return _fn(varga_key, v_chart.planets, v_chart.ascendant)


@st.cache_data(ttl=3600, show_spinner=False)
def compute_asteroids_cached(julian_day: float, heliocentric: bool, groups_tuple: tuple[str, ...]):
    from astro.western.asteroids import compute_asteroids as _fn
    return _fn(julian_day, heliocentric=heliocentric, include_groups=list(groups_tuple))


@st.cache_data(ttl=3600, show_spinner=False)
def compute_fixed_stars_cached(julian_day: float, limit):
    from astro.western.fixed_stars import compute_fixed_star_positions as _fn
    return _fn(julian_day, limit=limit)


@st.cache_data(ttl=3600, show_spinner=False)
def compute_parans_cached(julian_day: float, latitude: float, longitude: float, limit):
    from astro.western.advanced_bodies import calculate_parans as _fn
    stars = compute_fixed_stars_cached(julian_day, limit)
    return _fn(julian_day, latitude, longitude, stars)


@st.cache_data(ttl=3600, show_spinner=False)
def compute_heliacal_cached(julian_day: float, latitude: float, longitude: float, altitude: float, limit):
    from astro.western.advanced_bodies import calculate_heliacal as _fn
    stars = compute_fixed_stars_cached(julian_day, limit)
    return _fn(julian_day, latitude, longitude, altitude, stars)


@st.cache_data(ttl=3600, show_spinner=False)
def build_tieban_svg_cached(birth_sig: tuple[Any, ...], gender: str, language: str) -> str:
    from astro.tieban import TieBanShenShu, TieBanBirthData, render_tieban_chart_svg
    year, month, day, hour, minute, _, _, _ = birth_sig
    tbss = TieBanShenShu()
    ganzhi = tbss.calculate_ganzhi(datetime(year, month, day, hour, minute))
    birth_data = TieBanBirthData(
        birth_dt=datetime(year, month, day, hour, minute),
        year_gz=ganzhi["year"],
        month_gz=ganzhi["month"],
        day_gz=ganzhi["day"],
        hour_gz=ganzhi["hour"],
        gender=gender,
    )
    tb_result = tbss.calculate(birth_data)
    return render_tieban_chart_svg(tb_result, language=language)


@st.cache_data(ttl=3600, show_spinner=False)
def compute_tieban_result_cached(birth_sig: tuple[Any, ...], gender: str):
    from astro.tieban import TieBanShenShu, TieBanBirthData
    year, month, day, hour, minute, _, _, _ = birth_sig
    tbss = TieBanShenShu()
    ganzhi = tbss.calculate_ganzhi(datetime(year, month, day, hour, minute))
    birth_data = TieBanBirthData(
        birth_dt=datetime(year, month, day, hour, minute),
        year_gz=ganzhi["year"],
        month_gz=ganzhi["month"],
        day_gz=ganzhi["day"],
        hour_gz=ganzhi["hour"],
        gender=gender,
    )
    return tbss.calculate(birth_data)


@st.cache_data(ttl=3600, show_spinner=False)
def build_mazzalot_svg_cached(
    birth_sig: tuple[Any, ...],
    location_name: str,
):
    from astro.jewish_mazzalot import compute_mazzalot_chart, build_mazzalot_star_of_david_svg
    year, month, day, hour, minute, latitude, longitude, timezone = birth_sig
    chart = compute_mazzalot_chart(
        year=year, month=month, day=day, hour=hour, minute=minute,
        timezone=timezone, lat=latitude, lon=longitude,
    )
    return build_mazzalot_star_of_david_svg(
        chart,
        year=year, month=month, day=day, hour=hour,
    )
