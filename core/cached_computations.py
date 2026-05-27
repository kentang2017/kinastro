"""Cached computation wrappers for KinAstro.

All ``@st.cache_data`` / ``@st.cache_resource`` wrappers live here so
they can be shared across the thin ``app.py`` and system-handler modules
without circular imports.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import streamlit as st

# ── Astro compute imports ────────────────────────────────────────────────────
from astro.qizheng.calculator import compute_chart
from astro.qizheng.shensha import compute_shensha
from astro.qizheng.qizheng_dasha import compute_dasha
from astro.qizheng.qizheng_transit import compute_transit, compute_transit_now
from astro.qizheng.zhangguo import compute_zhangguo
from astro.western.western import compute_western_chart
from astro.western.western_transit import compute_western_transits
from astro.western.western_return import compute_solar_return
from astro.western.western_synastry import compute_synastry
from astro.western.fixed_stars import compute_fixed_star_positions
from astro.western.asteroids import compute_asteroids
from astro.western.advanced_bodies import calculate_parans, calculate_heliacal
from astro.vedic.indian import compute_vedic_chart
from astro.vedic.vedic_dasha import compute_vimshottari, compute_yogini
from astro.vedic.ashtakavarga import compute_ashtakavarga
from astro.vedic.vedic_yogas import compute_yogas
from astro.vedic.bphs_engine import compute_bphs
from astro.vedic.varga import compute_varga_chart
from astro.thai import compute_thai_chart
from astro.ziwei import compute_ziwei_chart
from astro.cetian_ziwei import compute_cetian_ziwei_chart
from astro.jewish_mazzalot import compute_mazzalot_chart, build_mazzalot_star_of_david_svg

# ── Key helpers ──────────────────────────────────────────────────────────────

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
    year, month, day, hour, minute, latitude, longitude, timezone = birth_sig
    options = dict(options_sig)
    common_kwargs = dict(
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        latitude=latitude,
        longitude=longitude,
        timezone=timezone,
        location_name=options.get("location_name", ""),
    )
    if system_name == "tab_chinese":
        return compute_chart(**common_kwargs, gender=options.get("gender", "male"))
    if system_name == "tab_western":
        return compute_western_chart(**common_kwargs, sidereal=bool(options.get("sidereal", False)))
    if system_name == "tab_indian":
        return compute_vedic_chart(**common_kwargs)
    if system_name == "tab_thai":
        return compute_thai_chart(**common_kwargs)
    if system_name == "tab_ziwei":
        return compute_ziwei_chart(
            **common_kwargs,
            gender=options.get("gender", "male"),
            vietnam_mode=bool(options.get("vietnam_mode", False)),
        )
    if system_name == "tab_cetian_ziwei":
        return compute_cetian_ziwei_chart(**common_kwargs, gender=options.get("gender", "male"))
    if system_name == "tab_mazzalot":
        return compute_mazzalot_chart(
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            timezone=timezone,
            lat=latitude,
            lon=longitude,
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
    return compute_transit_now(timezone=timezone)


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
    _ = chart_key
    return compute_shensha(
        year=year,
        solar_month=solar_month,
        julian_day=julian_day,
        hour_branch=hour_branch,
        timezone=timezone,
        ming_gong_branch=ming_gong_branch,
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
    _ = chart_key
    return compute_dasha(
        birth_year=birth_year,
        ming_gong_branch=ming_gong_branch,
        gender=gender,
        houses=houses,
        current_year=current_year,
    )


@st.cache_data(ttl=3600, show_spinner=False)
def compute_transit_cached(*, year: int, month: int, day: int, hour: int, minute: int, timezone: float):
    return compute_transit(
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        timezone=timezone,
    )


@st.cache_data(ttl=3600, show_spinner=False)
def compute_zhangguo_cached(chart_key: tuple[Any, ...], planets, houses, gender: str):
    _ = chart_key
    return compute_zhangguo(planets=planets, houses=houses, gender=gender)


@st.cache_data(ttl=3600, show_spinner=False)
def compute_western_transits_cached(
    birth_sig: tuple[Any, ...],
    sidereal: bool,
    location_name: str,
    t_year: int,
    t_month: int,
    t_day: int,
    t_hour: int,
    t_minute: int,
):
    _, _, _, _, _, _, _, timezone = birth_sig
    natal = compute_system_cached("tab_western", birth_sig, _options_sig({"sidereal": sidereal, "location_name": location_name}))
    return compute_western_transits(natal, t_year, t_month, t_day, t_hour, t_minute, timezone)


@st.cache_data(ttl=3600, show_spinner=False)
def compute_solar_return_cached(
    sun_longitude: float,
    return_year: int,
    latitude: float,
    longitude: float,
    timezone: float,
    location_name: str,
):
    return compute_solar_return(sun_longitude, return_year, latitude, longitude, timezone, location_name)


@st.cache_data(ttl=3600, show_spinner=False)
def compute_synastry_cached(
    natal_sig: tuple[Any, ...],
    sidereal: bool,
    location_name: str,
    b_year: int,
    b_month: int,
    b_day: int,
    b_hour: int,
    b_minute: int,
    b_tz: float,
    b_lat: float,
    b_lon: float,
    b_location_name: str,
):
    natal = compute_system_cached("tab_western", natal_sig, _options_sig({"sidereal": sidereal, "location_name": location_name}))
    w_b = compute_western_chart(
        year=b_year,
        month=b_month,
        day=b_day,
        hour=b_hour,
        minute=b_minute,
        timezone=b_tz,
        latitude=b_lat,
        longitude=b_lon,
        location_name=b_location_name,
        sidereal=sidereal,
    )
    return compute_synastry(natal, w_b, "Person A", "Person B")


@st.cache_data(ttl=3600, show_spinner=False)
def compute_vimshottari_cached(moon_longitude: float, julian_day: float):
    return compute_vimshottari(moon_longitude, julian_day)


@st.cache_data(ttl=3600, show_spinner=False)
def compute_yogini_cached(moon_longitude: float, julian_day: float):
    return compute_yogini(moon_longitude, julian_day)


@st.cache_data(ttl=3600, show_spinner=False)
def compute_ashtakavarga_cached(p_lons_items: tuple[tuple[str, float], ...], asc_lon: float):
    return compute_ashtakavarga(dict(p_lons_items), asc_lon)


@st.cache_data(ttl=3600, show_spinner=False)
def compute_yogas_cached(p_lons_items: tuple[tuple[str, float], ...], asc_lon: float):
    return compute_yogas(dict(p_lons_items), asc_lon)


@st.cache_data(ttl=3600, show_spinner=False)
def compute_bphs_cached(birth_sig: tuple[Any, ...], location_name: str):
    v_chart = compute_system_cached("tab_indian", birth_sig, _options_sig({"location_name": location_name}))
    return compute_bphs(v_chart.planets, v_chart.houses, v_chart.ascendant)


@st.cache_data(ttl=3600, show_spinner=False)
def compute_varga_cached(varga_key: str, birth_sig: tuple[Any, ...], location_name: str):
    v_chart = compute_system_cached("tab_indian", birth_sig, _options_sig({"location_name": location_name}))
    return compute_varga_chart(varga_key, v_chart.planets, v_chart.ascendant)


@st.cache_data(ttl=3600, show_spinner=False)
def compute_asteroids_cached(julian_day: float, heliocentric: bool, groups_tuple: tuple[str, ...]):
    return compute_asteroids(julian_day, heliocentric=heliocentric, include_groups=list(groups_tuple))


@st.cache_data(ttl=3600, show_spinner=False)
def compute_fixed_stars_cached(julian_day: float, limit):
    return compute_fixed_star_positions(julian_day, limit=limit)


@st.cache_data(ttl=3600, show_spinner=False)
def compute_parans_cached(julian_day: float, latitude: float, longitude: float, limit):
    stars = compute_fixed_stars_cached(julian_day, limit)
    return calculate_parans(julian_day, latitude, longitude, stars)


@st.cache_data(ttl=3600, show_spinner=False)
def compute_heliacal_cached(julian_day: float, latitude: float, longitude: float, altitude: float, limit):
    stars = compute_fixed_stars_cached(julian_day, limit)
    return calculate_heliacal(julian_day, latitude, longitude, altitude, stars)


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
    year, month, day, hour, minute, latitude, longitude, timezone = birth_sig
    chart = compute_mazzalot_chart(
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        timezone=timezone,
        lat=latitude,
        lon=longitude,
    )
    return build_mazzalot_star_of_david_svg(
        chart,
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        tz=timezone,
        location=location_name,
    )


# ── Overview dashboard ───────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def cached_overview_snapshot(params_payload: dict[str, Any], gender: str) -> dict[str, dict[str, str]]:
    """Compute lightweight dashboard metrics for popular systems."""
    out: dict[str, dict[str, str]] = {}

    try:
        west = compute_western_chart(**params_payload)
        sun = next((p for p in getattr(west, "planets", []) if "Sun" in getattr(p, "name", "")), None)
        sun_sign = getattr(sun, "sign_chinese", "") or getattr(sun, "sign", "") or "-"
        out["tab_western"] = {
            "main": f"☉ {sun_sign}",
            "sub": f"P:{len(getattr(west, 'planets', []))} · A:{len(getattr(west, 'aspects', []))}",
        }
    except Exception:
        pass

    try:
        ziwei = compute_ziwei_chart(**params_payload, gender=gender)
        out["tab_ziwei"] = {
            "main": f"{getattr(ziwei, 'ming_zhu', '-')}",
            "sub": f"宮:{len(getattr(ziwei, 'palaces', []))} · 局:{getattr(ziwei, 'wu_xing_ju', '-')}",
        }
    except Exception:
        pass

    try:
        chinese = compute_chart(**params_payload, gender=gender)
        out["tab_chinese"] = {
            "main": f"{getattr(chinese, 'solar_month', '-')}",
            "sub": f"P:{len(getattr(chinese, 'planets', []))} · H:{len(getattr(chinese, 'houses', []))}",
        }
    except Exception:
        pass

    try:
        vedic = compute_vedic_chart(**params_payload)
        moon = next((p for p in getattr(vedic, "planets", []) if "Chandra" in getattr(p, "name", "")), None)
        nak = getattr(moon, "nakshatra", "-")
        out["tab_indian"] = {
            "main": f"☾ {nak}",
            "sub": f"P:{len(getattr(vedic, 'planets', []))} · H:{len(getattr(vedic, 'houses', []))}",
        }
    except Exception:
        pass

    return out


def build_overview_items(
    params_payload: dict[str, Any],
    gender: str,
    get_system_fn,
    t_fn,
) -> list[dict[str, str]]:
    """Build rendered overview item cards in fixed priority order."""
    snapshot = cached_overview_snapshot(params_payload, gender)
    ordered = ["tab_western", "tab_ziwei", "tab_chinese", "tab_indian"]
    items: list[dict[str, str]] = []
    for sys_id in ordered:
        meta = get_system_fn(sys_id)
        metric = snapshot.get(sys_id)
        if not meta or not metric:
            continue
        items.append(
            {
                "system_id": sys_id,
                "icon": meta.icon,
                "title": t_fn(meta.tab_key),
                "metric_main": metric.get("main", "-"),
                "metric_sub": metric.get("sub", "-"),
                "accent": meta.accent_color,
            }
        )
    return items
