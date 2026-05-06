"""
堅占星 (Kin Astro) — FastAPI Backend
Separates compute-heavy astrology calculations from the Streamlit frontend
for better stability, performance, and reusability.

Run with:
    uvicorn api_server:app --reload

All endpoints accept birth parameters and return JSON-serializable chart data.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import logging
from datetime import date, datetime
from functools import lru_cache
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Astro compute imports (no render functions — they depend on Streamlit UI)
# ---------------------------------------------------------------------------
from astro.qizheng.calculator import compute_chart
from astro.western.western import compute_western_chart
from astro.vedic.indian import compute_vedic_chart
from astro.thai import compute_thai_chart
from astro.kabbalistic import compute_kabbalistic_chart
from astro.arabic.arabic import compute_arabic_chart
from astro.maya import compute_maya_chart
from astro.ziwei import compute_ziwei_chart
from astro.mahabote import compute_mahabote_chart
from astro.egyptian.decans import compute_decan_chart
from astro.vedic.nadi import compute_nadi_chart
from astro.zurkhai import compute_zurkhai_chart
from astro.western.hellenistic import compute_hellenistic_chart
from astro.damo import compute_damo_chart
from astro.sanshi.liuren import compute_liuren_chart
from astro.sanshi.taiyi import compute_taiyi_chart
from astro.bazi import compute_bazi
from astro.horary.calculator import compute_western_horary, compute_vedic_prashna

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logger = logging.getLogger("kinastro.api")

# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------
app = FastAPI(
    title="堅占星 Kin Astro API",
    description=(
        "Multi-system astrology chart computation backend. "
        "Supports Chinese (七政四餘), Zi Wei Dou Shu (紫微斗數), Western, "
        "Vedic (Jyotish), Thai, Kabbalistic, Arabic, Mayan, Mahabote, "
        "Egyptian Decans, Nadi, Zurkhai, Hellenistic, "
        "Da Liu Ren (大六壬) and Taiyi (太乙命法) systems."
    ),
    version="1.0.0",
)

# =========================================================================
#  Pydantic request / response models
# =========================================================================


class BirthParams(BaseModel):
    """Common birth parameters shared by all astrology systems."""

    year: int = Field(..., ge=1, le=3000, description="Birth year")
    month: int = Field(..., ge=1, le=12, description="Birth month")
    day: int = Field(..., ge=1, le=31, description="Birth day")
    hour: int = Field(..., ge=0, le=23, description="Birth hour (0-23)")
    minute: int = Field(..., ge=0, le=59, description="Birth minute (0-59)")
    timezone: float = Field(
        ..., ge=-12.0, le=14.0, description="UTC offset (e.g. 8.0 for UTC+8)"
    )
    latitude: float = Field(
        ..., ge=-90.0, le=90.0, description="Birth latitude"
    )
    longitude: float = Field(
        ..., ge=-180.0, le=180.0, description="Birth longitude"
    )
    location_name: str = Field(
        default="", description="Human-readable location name"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "year": 1990,
                    "month": 6,
                    "day": 15,
                    "hour": 14,
                    "minute": 30,
                    "timezone": 8.0,
                    "latitude": 25.033,
                    "longitude": 121.565,
                    "location_name": "Taipei",
                }
            ]
        }
    }


class ChineseParams(BirthParams):
    """Chinese system additionally requires gender."""

    gender: str = Field(
        default="male",
        pattern=r"^(male|female)$",
        description="Gender: 'male' or 'female'",
    )


class WesternParams(BirthParams):
    """Western system supports an optional sidereal flag."""

    sidereal: bool = Field(
        default=False,
        description="Use sidereal zodiac (Lahiri ayanamsa) instead of tropical",
    )


class HellenisticParams(BirthParams):
    """Hellenistic system additionally needs birth_year and current_year."""

    current_year: Optional[int] = Field(
        default=None,
        description="Current year for profections (defaults to now)",
    )


class ComputeAllParams(BirthParams):
    """Parameters for the /api/compute endpoint that runs all systems."""

    gender: str = Field(
        default="male",
        pattern=r"^(male|female)$",
        description="Gender for Chinese chart",
    )
    sidereal: bool = Field(
        default=False,
        description="Use sidereal zodiac for the Western chart",
    )
    current_year: Optional[int] = Field(
        default=None,
        description="Current year for Hellenistic profections",
    )



class TaiyiParams(BirthParams):
    """Taiyi Life Method additionally requires gender."""

    gender: str = Field(
        default="male",
        pattern=r"^(male|female)$",
        description="Gender: 'male' or 'female'",
    )


class ChartResponse(BaseModel):
    """Generic envelope for a single chart result."""

    system: str
    ok: bool = True
    data: dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


class ComputeAllResponse(BaseModel):
    """Response from the /api/compute endpoint (all systems)."""

    ok: bool = True
    charts: dict[str, ChartResponse] = Field(default_factory=dict)


# =========================================================================
#  Serialisation helpers
# =========================================================================

def _make_serializable(obj: Any) -> Any:
    """Recursively convert an object tree to JSON-safe primitives."""
    if obj is None or isinstance(obj, (bool, int, float, str)):
        return obj
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, bytes):
        return obj.decode("utf-8", errors="replace")
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return {k: _make_serializable(v) for k, v in dataclasses.asdict(obj).items()}
    if isinstance(obj, dict):
        return {str(k): _make_serializable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_make_serializable(item) for item in obj]
    # Fallback: convert to string
    return str(obj)


def _chart_to_dict(chart_obj: Any) -> dict[str, Any]:
    """Convert a chart dataclass (or plain dict) to a JSON-safe dict."""
    if dataclasses.is_dataclass(chart_obj) and not isinstance(chart_obj, type):
        raw = dataclasses.asdict(chart_obj)
    elif isinstance(chart_obj, dict):
        raw = chart_obj
    else:
        raw = {"repr": str(chart_obj)}
    return _make_serializable(raw)


# =========================================================================
#  Cached computation layer
# =========================================================================

def _cache_key(params: BirthParams, **extra: Any) -> str:
    """Build a deterministic hash key from request parameters."""
    key_data = params.model_dump()
    key_data.update(extra)
    raw = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()


# lru_cache requires hashable arguments, so we use the hash key string.

@lru_cache(maxsize=256)
def _cached_chinese(key: str, year: int, month: int, day: int, hour: int,
                    minute: int, timezone: float, latitude: float,
                    longitude: float, location_name: str, gender: str) -> dict:
    chart = compute_chart(
        year=year, month=month, day=day, hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name, gender=gender,
    )
    return _chart_to_dict(chart)


@lru_cache(maxsize=256)
def _cached_western(key: str, year: int, month: int, day: int, hour: int,
                    minute: int, timezone: float, latitude: float,
                    longitude: float, location_name: str,
                    sidereal: bool) -> dict:
    chart = compute_western_chart(
        year=year, month=month, day=day, hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name, sidereal=sidereal,
    )
    return _chart_to_dict(chart)


@lru_cache(maxsize=256)
def _cached_vedic(key: str, year: int, month: int, day: int, hour: int,
                  minute: int, timezone: float, latitude: float,
                  longitude: float, location_name: str) -> dict:
    chart = compute_vedic_chart(
        year=year, month=month, day=day, hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name,
    )
    return _chart_to_dict(chart)


@lru_cache(maxsize=256)
def _cached_thai(key: str, year: int, month: int, day: int, hour: int,
                 minute: int, timezone: float, latitude: float,
                 longitude: float, location_name: str) -> dict:
    chart = compute_thai_chart(
        year=year, month=month, day=day, hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name,
    )
    return _chart_to_dict(chart)


@lru_cache(maxsize=256)
def _cached_kabbalistic(key: str, year: int, month: int, day: int, hour: int,
                        minute: int, timezone: float, latitude: float,
                        longitude: float, location_name: str) -> dict:
    chart = compute_kabbalistic_chart(
        year=year, month=month, day=day, hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name,
    )
    return _chart_to_dict(chart)


@lru_cache(maxsize=256)
def _cached_arabic(key: str, year: int, month: int, day: int, hour: int,
                   minute: int, timezone: float, latitude: float,
                   longitude: float, location_name: str) -> dict:
    chart = compute_arabic_chart(
        year=year, month=month, day=day, hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name,
    )
    return _chart_to_dict(chart)


@lru_cache(maxsize=256)
def _cached_maya(key: str, year: int, month: int, day: int, hour: int,
                 minute: int, timezone: float, latitude: float,
                 longitude: float, location_name: str) -> dict:
    chart = compute_maya_chart(
        year=year, month=month, day=day, hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name,
    )
    return _chart_to_dict(chart)


@lru_cache(maxsize=256)
def _cached_ziwei(key: str, year: int, month: int, day: int, hour: int,
                  minute: int, timezone: float, latitude: float,
                  longitude: float, location_name: str) -> dict:
    chart = compute_ziwei_chart(
        year=year, month=month, day=day, hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name,
    )
    return _chart_to_dict(chart)


@lru_cache(maxsize=256)
def _cached_mahabote(key: str, year: int, month: int, day: int, hour: int,
                     minute: int, timezone: float, latitude: float,
                     longitude: float, location_name: str) -> dict:
    chart = compute_mahabote_chart(
        year=year, month=month, day=day, hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name,
    )
    return _chart_to_dict(chart)


@lru_cache(maxsize=256)
def _cached_decans(key: str, year: int, month: int, day: int, hour: int,
                   minute: int, timezone: float, latitude: float,
                   longitude: float, location_name: str) -> dict:
    chart = compute_decan_chart(
        year=year, month=month, day=day, hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name,
    )
    return _chart_to_dict(chart)


@lru_cache(maxsize=256)
def _cached_nadi(key: str, year: int, month: int, day: int, hour: int,
                 minute: int, timezone: float, latitude: float,
                 longitude: float, location_name: str) -> dict:
    chart = compute_nadi_chart(
        year=year, month=month, day=day, hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name,
    )
    return _chart_to_dict(chart)


@lru_cache(maxsize=256)
def _cached_zurkhai(key: str, year: int, month: int, day: int, hour: int,
                    minute: int, timezone: float, latitude: float,
                    longitude: float, location_name: str) -> dict:
    chart = compute_zurkhai_chart(
        year=year, month=month, day=day, hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name,
    )
    return _chart_to_dict(chart)


@lru_cache(maxsize=256)
def _cached_damo(key: str, year: int, month: int, day: int, hour: int,
                 minute: int, timezone: float, latitude: float,
                 longitude: float, location_name: str,
                 gender: str) -> dict:
    chart = compute_damo_chart(
        year=year, month=month, day=day, hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name, gender=gender,
    )
    return _chart_to_dict(chart)


@lru_cache(maxsize=256)
def _cached_liuren(key: str, year: int, month: int, day: int, hour: int,
                   minute: int, timezone: float, latitude: float,
                   longitude: float, location_name: str) -> dict:
    chart = compute_liuren_chart(
        year=year, month=month, day=day, hour=hour, minute=minute,
        timezone=timezone,
    )
    return _chart_to_dict(chart)


@lru_cache(maxsize=256)
def _cached_taiyi(key: str, year: int, month: int, day: int, hour: int,
                  minute: int, timezone: float, latitude: float,
                  longitude: float, location_name: str,
                  gender: str) -> dict:
    chart = compute_taiyi_chart(
        year=year, month=month, day=day, hour=hour, minute=minute,
        gender=gender,
    )
    return _chart_to_dict(chart)


@lru_cache(maxsize=256)
def _cached_bazi(key: str, year: int, month: int, day: int, hour: int,
                 minute: int, timezone: float, latitude: float,
                 longitude: float, location_name: str,
                 gender: str, reference_date_iso: str) -> dict:
    ref_date = date.fromisoformat(reference_date_iso)
    chart = compute_bazi(
        year=year, month=month, day=day, hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name, gender=gender,
        reference_date=ref_date,
    )
    return _chart_to_dict(chart)


# Hellenistic depends on a WesternChart object, so handle specially.
def _compute_hellenistic(params: BirthParams,
                         current_year: Optional[int]) -> dict:
    """Compute Hellenistic chart (requires a Western chart first)."""
    w_chart = compute_western_chart(
        year=params.year, month=params.month, day=params.day,
        hour=params.hour, minute=params.minute, timezone=params.timezone,
        latitude=params.latitude, longitude=params.longitude,
        location_name=params.location_name,
    )
    cy = current_year if current_year is not None else datetime.now().year
    h_chart = compute_hellenistic_chart(
        w_chart, birth_year=params.year, current_year=cy,
    )
    return _chart_to_dict(h_chart)


# ---------------------------------------------------------------------------
#  Internal helpers for calling cached functions with BirthParams
# ---------------------------------------------------------------------------

def _base_kwargs(p: BirthParams) -> dict:
    """Extract the 9 common kwargs from a BirthParams model."""
    return dict(
        year=p.year, month=p.month, day=p.day,
        hour=p.hour, minute=p.minute, timezone=p.timezone,
        latitude=p.latitude, longitude=p.longitude,
        location_name=p.location_name,
    )


# =========================================================================
#  Individual system endpoints
# =========================================================================


@app.post("/api/chinese", response_model=ChartResponse, tags=["Systems"])
async def chinese_chart(params: ChineseParams) -> ChartResponse:
    """Compute a Chinese 七政四餘 chart."""
    try:
        key = _cache_key(params, gender=params.gender)
        data = _cached_chinese(key, **_base_kwargs(params), gender=params.gender)
        return ChartResponse(system="chinese", data=data)
    except Exception as exc:
        logger.exception("Chinese chart computation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/western", response_model=ChartResponse, tags=["Systems"])
async def western_chart(params: WesternParams) -> ChartResponse:
    """Compute a Western astrology chart (tropical or sidereal)."""
    try:
        key = _cache_key(params, sidereal=params.sidereal)
        data = _cached_western(
            key, **_base_kwargs(params), sidereal=params.sidereal,
        )
        return ChartResponse(system="western", data=data)
    except Exception as exc:
        logger.exception("Western chart computation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/vedic", response_model=ChartResponse, tags=["Systems"])
async def vedic_chart(params: BirthParams) -> ChartResponse:
    """Compute a Vedic (Jyotish) chart."""
    try:
        key = _cache_key(params)
        data = _cached_vedic(key, **_base_kwargs(params))
        return ChartResponse(system="vedic", data=data)
    except Exception as exc:
        logger.exception("Vedic chart computation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/thai", response_model=ChartResponse, tags=["Systems"])
async def thai_chart(params: BirthParams) -> ChartResponse:
    """Compute a Thai astrology chart."""
    try:
        key = _cache_key(params)
        data = _cached_thai(key, **_base_kwargs(params))
        return ChartResponse(system="thai", data=data)
    except Exception as exc:
        logger.exception("Thai chart computation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/kabbalistic", response_model=ChartResponse, tags=["Systems"])
async def kabbalistic_chart(params: BirthParams) -> ChartResponse:
    """Compute a Kabbalistic astrology chart."""
    try:
        key = _cache_key(params)
        data = _cached_kabbalistic(key, **_base_kwargs(params))
        return ChartResponse(system="kabbalistic", data=data)
    except Exception as exc:
        logger.exception("Kabbalistic chart computation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/arabic", response_model=ChartResponse, tags=["Systems"])
async def arabic_chart(params: BirthParams) -> ChartResponse:
    """Compute an Arabic/Islamic astrology chart."""
    try:
        key = _cache_key(params)
        data = _cached_arabic(key, **_base_kwargs(params))
        return ChartResponse(system="arabic", data=data)
    except Exception as exc:
        logger.exception("Arabic chart computation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/maya", response_model=ChartResponse, tags=["Systems"])
async def maya_chart(params: BirthParams) -> ChartResponse:
    """Compute a Mayan astrology chart."""
    try:
        key = _cache_key(params)
        data = _cached_maya(key, **_base_kwargs(params))
        return ChartResponse(system="maya", data=data)
    except Exception as exc:
        logger.exception("Mayan chart computation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/ziwei", response_model=ChartResponse, tags=["Systems"])
async def ziwei_chart(params: BirthParams) -> ChartResponse:
    """Compute a Zi Wei Dou Shu (紫微斗數) chart."""
    try:
        key = _cache_key(params)
        data = _cached_ziwei(key, **_base_kwargs(params))
        return ChartResponse(system="ziwei", data=data)
    except Exception as exc:
        logger.exception("Zi Wei chart computation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/mahabote", response_model=ChartResponse, tags=["Systems"])
async def mahabote_chart(params: BirthParams) -> ChartResponse:
    """Compute a Myanmar Mahabote chart."""
    try:
        key = _cache_key(params)
        data = _cached_mahabote(key, **_base_kwargs(params))
        return ChartResponse(system="mahabote", data=data)
    except Exception as exc:
        logger.exception("Mahabote chart computation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/decans", response_model=ChartResponse, tags=["Systems"])
async def decans_chart(params: BirthParams) -> ChartResponse:
    """Compute an Egyptian Decans chart."""
    try:
        key = _cache_key(params)
        data = _cached_decans(key, **_base_kwargs(params))
        return ChartResponse(system="decans", data=data)
    except Exception as exc:
        logger.exception("Decans chart computation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/nadi", response_model=ChartResponse, tags=["Systems"])
async def nadi_chart(params: BirthParams) -> ChartResponse:
    """Compute a Nadi Jyotish chart."""
    try:
        key = _cache_key(params)
        data = _cached_nadi(key, **_base_kwargs(params))
        return ChartResponse(system="nadi", data=data)
    except Exception as exc:
        logger.exception("Nadi chart computation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/zurkhai", response_model=ChartResponse, tags=["Systems"])
async def zurkhai_chart(params: BirthParams) -> ChartResponse:
    """Compute a Mongolian Zurkhai chart."""
    try:
        key = _cache_key(params)
        data = _cached_zurkhai(key, **_base_kwargs(params))
        return ChartResponse(system="zurkhai", data=data)
    except Exception as exc:
        logger.exception("Zurkhai chart computation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/damo", response_model=ChartResponse, tags=["Systems"])
async def damo_chart(params: ChineseParams) -> ChartResponse:
    """Compute a Damo One Palm Scripture chart (達摩一掌經)."""
    try:
        key = _cache_key(params, gender=params.gender)
        kwargs = _base_kwargs(params)
        kwargs["gender"] = params.gender
        data = _cached_damo(key, **kwargs)
        return ChartResponse(system="damo", data=data)
    except Exception as exc:
        logger.exception("Damo One Palm chart computation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/hellenistic", response_model=ChartResponse, tags=["Systems"])
async def hellenistic_chart(params: HellenisticParams) -> ChartResponse:
    """Compute a Hellenistic Greek astrology chart (derived from Western)."""
    try:
        data = _compute_hellenistic(params, params.current_year)
        return ChartResponse(system="hellenistic", data=data)
    except Exception as exc:
        logger.exception("Hellenistic chart computation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/liuren", response_model=ChartResponse, tags=["Systems"])
async def liuren_chart(params: BirthParams) -> ChartResponse:
    """Compute a Da Liu Ren chart (大六壬)."""
    try:
        key = _cache_key(params)
        data = _cached_liuren(key, **_base_kwargs(params))
        return ChartResponse(system="liuren", data=data)
    except Exception as exc:
        logger.exception("Da Liu Ren chart computation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/taiyi", response_model=ChartResponse, tags=["Systems"])
async def taiyi_chart(params: TaiyiParams) -> ChartResponse:
    """Compute a Taiyi Life Method chart (太乙命法)."""
    try:
        key = _cache_key(params, gender=params.gender)
        kwargs = _base_kwargs(params)
        kwargs["gender"] = params.gender
        data = _cached_taiyi(key, **kwargs)
        return ChartResponse(system="taiyi", data=data)
    except Exception as exc:
        logger.exception("Taiyi Life Method chart computation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/bazi", response_model=ChartResponse, tags=["Systems"])
async def bazi_chart(params: ChineseParams) -> ChartResponse:
    """Compute a traditional Ziping Bazi (子平八字) chart.

    Strictly follows classical Ziping method (子平正宗) as described in:
    - 淵海子平 (Yuanhai Ziping)
    - 子平真詮 (Ziping Zhenquan)
    - 三命通會 (Sanming Tonghui)
    - 滴天髓 (Ditianshui)

    Returns the full BaziChart including four pillars, ten gods, day master
    strength, pattern (格局), use god (用神), great fortune cycles (大運),
    current year fortune (流年), and shen sha (神煞).
    """
    try:
        today_iso = date.today().isoformat()
        key = _cache_key(params, gender=params.gender, reference_date=today_iso)
        kwargs = _base_kwargs(params)
        kwargs["gender"] = params.gender
        kwargs["reference_date_iso"] = today_iso
        data = _cached_bazi(key, **kwargs)
        return ChartResponse(system="bazi", data=data)
    except Exception as exc:
        logger.exception("Ziping Bazi chart computation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


class HoraryParams(BirthParams):
    """Parameters for Traditional Horary Astrology chart."""

    question_text: str = Field(
        default="",
        description="The horary question being asked",
    )
    question_type: str = Field(
        default="general",
        description=(
            "Question type: 'marriage', 'career', 'wealth', 'lost_item', "
            "'illness', 'travel', 'missing_person', 'property', 'general'"
        ),
    )
    tradition: str = Field(
        default="western",
        description="Tradition: 'western' (Lilly/Bonatti) or 'vedic' (Prashna Marga)",
    )
    prashna_number: Optional[int] = Field(
        default=None,
        ge=1, le=108,
        description="Optional 1-108 querent number for Vedic Prashna tradition",
    )


@app.post("/api/horary", response_model=ChartResponse, tags=["Systems"])
async def horary_chart(params: HoraryParams) -> ChartResponse:
    """Compute a Traditional Horary chart.

    Supports both Western (Lilly/Bonatti) and Vedic (Prashna Marga) traditions.
    The ``tradition`` field selects the system; ``question_type`` and
    ``question_text`` are used for the judgment.

    Western tradition applies strict Lilly/Bonatti rules including:
    - Essential and Accidental Dignities
    - Applying/separating aspects, Reception
    - Void of Course Moon (with Lilly's exception signs)
    - Translation and Collection of Light
    - Strictures Against Judgment

    Vedic Prashna follows Prasna Marga with Arudha Lagna computation.
    """
    try:
        kw = _base_kwargs(params)
        if params.tradition == "vedic":
            chart = compute_vedic_prashna(
                question_text=params.question_text,
                question_type=params.question_type,
                prashna_number=params.prashna_number,
                **kw,
            )
        else:
            chart = compute_western_horary(
                question_text=params.question_text,
                question_type=params.question_type,
                **kw,
            )
        return ChartResponse(system=f"horary_{params.tradition}", data=_chart_to_dict(chart))
    except Exception as exc:
        logger.exception("Horary chart computation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc




# =========================================================================
#  Aggregate endpoint — compute ALL systems in one call
# =========================================================================

# Map of system name → (cached_fn, extra_params_builder)
_SYSTEMS_BASIC: list[tuple[str, Any]] = [
    ("vedic", _cached_vedic),
    ("thai", _cached_thai),
    ("kabbalistic", _cached_kabbalistic),
    ("arabic", _cached_arabic),
    ("maya", _cached_maya),
    ("ziwei", _cached_ziwei),
    ("mahabote", _cached_mahabote),
    ("decans", _cached_decans),
    ("nadi", _cached_nadi),
    ("zurkhai", _cached_zurkhai),
    ("liuren", _cached_liuren),
]

# Damo requires gender parameter and is handled separately in compute_all
# endpoint rather than being included in _SYSTEMS_BASIC.


@app.post("/api/compute", response_model=ComputeAllResponse, tags=["Aggregate"])
async def compute_all(params: ComputeAllParams) -> ComputeAllResponse:
    """Compute charts for **all** astrology systems in a single request.

    Individual system failures are captured in the per-system ``error``
    field; the overall response still returns HTTP 200 so that partial
    results are available.
    """
    charts: dict[str, ChartResponse] = {}
    kw = _base_kwargs(params)

    # --- Chinese (needs gender) ---
    try:
        key = _cache_key(params, gender=params.gender)
        data = _cached_chinese(key, **kw, gender=params.gender)
        charts["chinese"] = ChartResponse(system="chinese", data=data)
    except Exception as exc:
        logger.exception("Chinese chart failed in /api/compute")
        charts["chinese"] = ChartResponse(
            system="chinese", ok=False, error=str(exc),
        )

    # --- Western (needs sidereal) ---
    try:
        key = _cache_key(params, sidereal=params.sidereal)
        data = _cached_western(key, **kw, sidereal=params.sidereal)
        charts["western"] = ChartResponse(system="western", data=data)
    except Exception as exc:
        logger.exception("Western chart failed in /api/compute")
        charts["western"] = ChartResponse(
            system="western", ok=False, error=str(exc),
        )

    # --- Basic systems (common params only) ---
    for name, fn in _SYSTEMS_BASIC:
        try:
            key = _cache_key(params)
            data = fn(key, **kw)
            charts[name] = ChartResponse(system=name, data=data)
        except Exception as exc:
            logger.exception("%s chart failed in /api/compute", name)
            charts[name] = ChartResponse(
                system=name, ok=False, error=str(exc),
            )

    # --- Hellenistic (derived from Western) ---
    try:
        data = _compute_hellenistic(params, params.current_year)
        charts["hellenistic"] = ChartResponse(system="hellenistic", data=data)
    except Exception as exc:
        logger.exception("Hellenistic chart failed in /api/compute")
        charts["hellenistic"] = ChartResponse(
            system="hellenistic", ok=False, error=str(exc),
        )

    # --- Damo (needs gender) ---
    try:
        key = _cache_key(params, gender=params.gender)
        data = _cached_damo(key, **kw, gender=params.gender)
        charts["damo"] = ChartResponse(system="damo", data=data)
    except Exception as exc:
        logger.exception("Damo chart failed in /api/compute")
        charts["damo"] = ChartResponse(
            system="damo", ok=False, error=str(exc),
        )

    return ComputeAllResponse(charts=charts)


# =========================================================================
#  Health / info endpoints
# =========================================================================


@app.get("/api/health", tags=["Meta"])
async def health() -> dict[str, str]:
    """Simple liveness check."""
    return {"status": "ok"}


@app.get("/api/systems", tags=["Meta"])
async def list_systems() -> dict[str, list[str]]:
    """List all supported astrology systems."""
    return {
        "systems": [
            "chinese",
            "western",
            "vedic",
            "thai",
            "kabbalistic",
            "arabic",
            "maya",
            "ziwei",
            "mahabote",
            "decans",
            "nadi",
            "zurkhai",
            "hellenistic",
            "damo",
            "liuren",
            "taiyi",
            "bazi",
            "horary_western",
            "horary_vedic",
        ]
    }
