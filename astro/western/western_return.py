"""
astro/western_return.py — 返照盤 (Solar & Lunar Return)

Finds the exact moment Sun/Moon returns to natal position,
then casts a full chart.
"""
import streamlit as st

from .solar_return_core import (
    LunarReturnCoreResult,
    SolarReturnCoreResult,
    compute_lunar_return_core,
    compute_solar_return_core,
    jd_to_datetime_str,
)

# Backward-compatible aliases
SolarReturnResult = SolarReturnCoreResult
LunarReturnResult = LunarReturnCoreResult


@st.cache_data(ttl=3600, show_spinner=False)
def compute_solar_return(
    natal_sun_lon,
    target_year,
    latitude,
    longitude,
    timezone=0.0,
    location_name="",
):
    """Find when Sun returns to natal longitude in target_year."""
    return compute_solar_return_core(
        natal_sun_lon,
        target_year,
        latitude,
        longitude,
        timezone=timezone,
        location_name=location_name,
    )


@st.cache_data(ttl=3600, show_spinner=False)
def compute_lunar_return(
    natal_moon_lon,
    after_jd,
    latitude,
    longitude,
    timezone=0.0,
    location_name="",
):
    """Find next Moon return to natal longitude after given JD."""
    return compute_lunar_return_core(
        natal_moon_lon,
        after_jd,
        latitude,
        longitude,
        timezone=timezone,
        location_name=location_name,
    )


__all__ = [
    "SolarReturnResult",
    "LunarReturnResult",
    "compute_solar_return",
    "compute_lunar_return",
    "jd_to_datetime_str",
]