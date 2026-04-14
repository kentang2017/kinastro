"""
astro/ai_analysis.py — AI 分析模組 (AI Analysis Module)

Provides:
  - CerebrasClient: wrapper around the Cerebras Cloud SDK for chat completions
  - format_chart_for_prompt(): formats any astrology chart into a text prompt
  - load/save system prompts from a JSON file
  - CEREBRAS_MODEL_OPTIONS / descriptions

Similar to the AI integration in kintaiyi (太乙神數).
"""

from __future__ import annotations

import json
import logging
import os
import time
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Cerebras SDK wrapper
# ---------------------------------------------------------------------------

DEFAULT_MODEL = "qwen-3-235b-a22b-instruct-2507"

CEREBRAS_MODEL_OPTIONS = [
    "qwen-3-235b-a22b-instruct-2507",
    "llama-4-scout-17b-16e-instruct",
    "llama3.1-8b",
    "llama-3.3-70b",
    "deepseek-r1-distill-llama-70b",
]

CEREBRAS_MODEL_DESCRIPTIONS = {
    "qwen-3-235b-a22b-instruct-2507": "Cerebras: Fast inference, great for rapid iteration.",
    "llama-4-scout-17b-16e-instruct": "Cerebras: Optimized for guided workflows.",
    "llama3.1-8b": "Cerebras: Light and fast for quick tasks.",
    "llama-3.3-70b": "Cerebras: Most capable for complex reasoning.",
    "deepseek-r1-distill-llama-70b": "DeepSeek distilled on Cerebras.",
}


class RateLimitError(Exception):
    """Raised when the AI API returns a rate-limit (429) error after all retries."""


# Maximum number of application-level retries on top of the SDK's built-in
# retries.  Total wait can be up to ~1+2+4 = 7 seconds with jitter.
_APP_MAX_RETRIES = 3
_APP_RETRY_BASE_DELAY = 1.0  # seconds


class CerebrasClient:
    """Thin wrapper around the Cerebras Cloud SDK with enhanced retry logic."""

    def __init__(self, api_key: str, max_retries: int = 5):
        if not api_key:
            raise ValueError("CerebrasClient requires a non-empty API key.")
        from cerebras.cloud.sdk import Cerebras
        self.client = Cerebras(api_key=api_key, max_retries=max_retries)

    def chat(
        self,
        messages: list[dict[str, str]],
        model: str = DEFAULT_MODEL,
        **kwargs,
    ) -> str:
        """Send a chat completion request and return the assistant message text.

        Includes application-level retry with exponential back-off on top of
        the SDK's built-in retry so that transient 429 bursts are absorbed
        gracefully.
        """
        from cerebras.cloud.sdk import RateLimitError as _SdkRateLimit

        last_exc: Exception | None = None
        for attempt in range(_APP_MAX_RETRIES):
            try:
                response = self.client.chat.completions.create(
                    messages=messages,
                    model=model,
                    **kwargs,
                )
                return response.choices[0].message.content
            except _SdkRateLimit as exc:
                last_exc = exc
                if attempt < _APP_MAX_RETRIES - 1:
                    delay = _APP_RETRY_BASE_DELAY * (2 ** attempt)
                    logger.warning(
                        "Rate limited (attempt %d/%d), retrying in %.1fs …",
                        attempt + 1, _APP_MAX_RETRIES, delay,
                    )
                    time.sleep(delay)

        # All retries exhausted — raise our own RateLimitError so the caller
        # can show a user-friendly message.
        raise RateLimitError(str(last_exc)) from last_exc


# ---------------------------------------------------------------------------
# System prompt management
# ---------------------------------------------------------------------------

_PROMPTS_FILE = os.path.join(
    os.path.dirname(__file__), "data", "system_prompts.json"
)

_DEFAULT_PROMPTS = {
    "prompts": [
        {
            "name": "占星大師",
            "name_en": "Astrology Master",
            "content": (
                "你是一位精通世界各地占星體系的大師，熟悉西洋占星、印度占星（Jyotish）、"
                "七政四餘（中國占星）、紫微斗數、宿曜道、泰國占星、卡巴拉占星、阿拉伯占星、"
                "瑪雅占星、緬甸占星（Mahabote）、古埃及十度區間（Decans）、納迪占星、"
                "蒙古祖爾海（Zurkhai）、希臘占星（Hellenistic）、萬花仙禽（禽星）等。\n\n"
                "請根據提供的排盤數據進行以下操作：\n"
                "1. 解釋盤局的關鍵要素（行星、宮位、相位、特殊格局等）。\n"
                "2. 分析盤局的吉凶和潛在影響。\n"
                "3. 評估命主的運勢和人生趨勢。\n"
                "4. 提供實用的建議或應對策略。\n\n"
                "請以清晰的結構（分段、標題）呈現，語言專業且易懂。"
            ),
        },
        {
            "name": "性格分析",
            "name_en": "Personality Analysis",
            "content": (
                "你是一位占星心理分析師。請根據提供的占星排盤數據，"
                "深入分析命主的性格特質、情感模式、人際關係傾向、"
                "職業適性及心理成長方向。請引用具體的星象配置來支持你的分析。"
            ),
        },
        {
            "name": "流年運勢",
            "name_en": "Annual Forecast",
            "content": (
                "你是一位占星流年運勢分析師。請根據提供的占星排盤數據，"
                "分析命主未來一年的整體運勢趨勢，包括事業、財運、感情、健康等方面。"
                "請指出關鍵的時間節點和需要注意的事項。"
            ),
        },
    ],
    "selected": "占星大師",
}


def load_system_prompts() -> dict:
    """Load system prompts from JSON file, creating defaults if needed."""
    try:
        with open(_PROMPTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "prompts" in data and data["prompts"]:
                return data
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    # Write defaults
    save_system_prompts(_DEFAULT_PROMPTS)
    return _DEFAULT_PROMPTS.copy()


def save_system_prompts(data: dict) -> bool:
    """Persist system prompts to the JSON file."""
    try:
        with open(_PROMPTS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Chart → prompt formatters
# ---------------------------------------------------------------------------

def _safe_getattr(obj: Any, *attrs: str, default: str = "") -> str:
    """Try multiple attribute names and return the first truthy value."""
    for attr in attrs:
        val = getattr(obj, attr, None)
        if val is not None:
            return str(val)
    return default


def _format_planet_list(planets, fields=None) -> str:
    """Generic planet list formatter."""
    if not planets:
        return "(none)"
    lines = []
    for p in planets:
        name = _safe_getattr(p, "name", "symbol")
        sign = _safe_getattr(p, "sign", "rashi", "sign_western")
        deg = _safe_getattr(p, "degree", "sign_degree", "longitude")
        house = _safe_getattr(p, "house", "house_num")
        retro = "R" if getattr(p, "retrograde", False) else ""
        parts = [name]
        if sign:
            parts.append(f"in {sign}")
        if deg:
            parts.append(f"{deg}°")
        if house:
            parts.append(f"H{house}")
        if retro:
            parts.append("(R)")
        lines.append(" ".join(parts))
    return "\n".join(lines)


def _format_aspects(aspects) -> str:
    """Format aspect list."""
    if not aspects:
        return "(none)"
    lines = []
    for a in aspects[:30]:  # cap to avoid overly long prompts
        p1 = _safe_getattr(a, "planet1", "planet1_name", "p1")
        p2 = _safe_getattr(a, "planet2", "planet2_name", "p2")
        asp = _safe_getattr(a, "aspect", "aspect_name", "name")
        orb = _safe_getattr(a, "orb")
        lines.append(f"{p1} {asp} {p2} (orb {orb}°)")
    return "\n".join(lines)


def _format_houses(houses) -> str:
    """Format house cusps."""
    if not houses:
        return "(none)"
    lines = []
    for h in houses:
        num = _safe_getattr(h, "number", "house_num")
        sign = _safe_getattr(h, "sign", "sign_name")
        deg = _safe_getattr(h, "degree", "cusp_degree")
        lines.append(f"House {num}: {sign} {deg}°")
    return "\n".join(lines)


def format_western_chart(chart) -> str:
    """Format a Western chart for the AI prompt."""
    sections = ["【西洋占星排盤 Western Chart】"]
    sections.append(f"ASC Sign: {_safe_getattr(chart, 'asc_sign')}")
    sections.append(f"MC Sign: {_safe_getattr(chart, 'mc_sign')}")
    sections.append("\n--- Planets ---")
    sections.append(_format_planet_list(getattr(chart, 'planets', [])))
    sections.append("\n--- Houses ---")
    sections.append(_format_houses(getattr(chart, 'houses', [])))
    sections.append("\n--- Aspects ---")
    sections.append(_format_aspects(getattr(chart, 'aspects', [])))
    return "\n".join(sections)


def format_vedic_chart(chart) -> str:
    """Format a Vedic (Indian / Jyotish) chart for the AI prompt."""
    sections = ["【印度占星排盤 Vedic Chart】"]
    sections.append(f"Lagna: {_safe_getattr(chart, 'lagna', 'asc_rashi')}")
    sections.append(f"Ayanamsa: {_safe_getattr(chart, 'ayanamsa')}")
    sections.append("\n--- Planets ---")
    sections.append(_format_planet_list(getattr(chart, 'planets', [])))
    sections.append("\n--- Houses ---")
    sections.append(_format_houses(getattr(chart, 'houses', [])))
    sections.append("\n--- Aspects ---")
    sections.append(_format_aspects(getattr(chart, 'aspects', [])))
    return "\n".join(sections)


def format_chinese_chart(chart) -> str:
    """Format a Chinese Seven-Governors (七政四餘) chart for the AI prompt."""
    sections = ["【七政四餘排盤 Chinese Chart】"]
    sections.append(f"命宮: {_safe_getattr(chart, 'ming_gong', 'ming')}")
    sections.append(f"身宮: {_safe_getattr(chart, 'shen_gong', 'shen')}")
    # BaZi
    bazi = getattr(chart, 'bazi', None)
    if bazi:
        sections.append(f"八字: 年={_safe_getattr(bazi, 'year')}, 月={_safe_getattr(bazi, 'month')}, "
                        f"日={_safe_getattr(bazi, 'day')}, 時={_safe_getattr(bazi, 'hour')}")
    sections.append("\n--- Planets ---")
    sections.append(_format_planet_list(getattr(chart, 'planets', [])))
    sections.append("\n--- Houses ---")
    sections.append(_format_houses(getattr(chart, 'houses', [])))
    sections.append("\n--- Aspects ---")
    sections.append(_format_aspects(getattr(chart, 'aspects', [])))
    return "\n".join(sections)


def format_ziwei_chart(chart) -> str:
    """Format a Zi Wei Dou Shu (紫微斗數) chart for the AI prompt."""
    sections = ["【紫微斗數排盤 Zi Wei Dou Shu Chart】"]
    sections.append(f"命宮: {_safe_getattr(chart, 'ming_gong')}")
    sections.append(f"身宮: {_safe_getattr(chart, 'shen_gong')}")
    sections.append(f"命主: {_safe_getattr(chart, 'ming_zhu')}")
    sections.append(f"身主: {_safe_getattr(chart, 'shen_zhu')}")
    # palaces
    palaces = getattr(chart, 'palaces', [])
    if palaces:
        sections.append("\n--- 十二宮 ---")
        for pal in palaces:
            name = _safe_getattr(pal, 'name', 'palace_name')
            branch = _safe_getattr(pal, 'branch', 'earthly_branch')
            stars = _safe_getattr(pal, 'stars', 'star_list')
            sections.append(f"{name}（{branch}）: {stars}")
    return "\n".join(sections)


def format_thai_chart(chart) -> str:
    """Format a Thai astrology chart for the AI prompt."""
    sections = ["【泰國占星排盤 Thai Chart】"]
    sections.append(f"Weekday: {_safe_getattr(chart, 'weekday', 'birth_weekday')}")
    sections.append(f"Lagna: {_safe_getattr(chart, 'lagna')}")
    sections.append("\n--- Planets ---")
    sections.append(_format_planet_list(getattr(chart, 'planets', [])))
    return "\n".join(sections)


def format_kabbalistic_chart(chart) -> str:
    """Format a Kabbalistic chart for the AI prompt."""
    sections = ["【卡巴拉占星排盤 Kabbalistic Chart】"]
    sections.append(f"Life Path: {_safe_getattr(chart, 'life_path')}")
    sections.append(f"Name Number: {_safe_getattr(chart, 'name_number')}")
    sections.append(f"Hebrew Letter: {_safe_getattr(chart, 'hebrew_letter')}")
    sections.append(f"Sephirah: {_safe_getattr(chart, 'sephirah')}")
    sections.append(f"Tree Path: {_safe_getattr(chart, 'tree_path')}")
    sections.append("\n--- Planets ---")
    sections.append(_format_planet_list(getattr(chart, 'planets', [])))
    return "\n".join(sections)


def format_arabic_chart(chart) -> str:
    """Format an Arabic astrology chart for the AI prompt."""
    sections = ["【阿拉伯占星排盤 Arabic Chart】"]
    sections.append(f"Lot of Fortune: {_safe_getattr(chart, 'lot_of_fortune')}")
    sections.append("\n--- Planets ---")
    sections.append(_format_planet_list(getattr(chart, 'planets', [])))
    sections.append("\n--- Arabic Parts ---")
    parts = getattr(chart, 'arabic_parts', [])
    if parts:
        for pt in parts:
            name = _safe_getattr(pt, 'name')
            lon = _safe_getattr(pt, 'longitude', 'degree')
            sign = _safe_getattr(pt, 'sign')
            sections.append(f"{name}: {sign} {lon}°")
    return "\n".join(sections)


def format_maya_chart(chart) -> str:
    """Format a Mayan astrology chart for the AI prompt."""
    sections = ["【瑪雅占星排盤 Mayan Chart】"]
    sections.append(f"Kin: {_safe_getattr(chart, 'kin')}")
    sections.append(f"Tzolkin: {_safe_getattr(chart, 'tzolkin')}")
    sections.append(f"Haab: {_safe_getattr(chart, 'haab')}")
    sections.append(f"Tone: {_safe_getattr(chart, 'tone')}")
    sections.append(f"Glyph: {_safe_getattr(chart, 'glyph', 'day_sign')}")
    sections.append(f"Long Count: {_safe_getattr(chart, 'long_count')}")
    return "\n".join(sections)


def format_mahabote_chart(chart) -> str:
    """Format a Mahabote (Myanmar) chart for the AI prompt."""
    sections = ["【緬甸占星排盤 Mahabote Chart】"]
    sections.append(f"Weekday: {_safe_getattr(chart, 'birth_weekday')}")
    sections.append(f"Animal: {_safe_getattr(chart, 'birth_animal_en', 'birth_animal_cn')}")
    houses = getattr(chart, 'houses', [])
    if houses:
        sections.append("\n--- Houses ---")
        for h in houses:
            name = _safe_getattr(h, 'name', 'house_name')
            wday = _safe_getattr(h, 'weekday_en', 'weekday_cn')
            animal = _safe_getattr(h, 'animal_en', 'animal_cn')
            sections.append(f"{name}: {wday} ({animal})")
    return "\n".join(sections)


def format_decan_chart(chart) -> str:
    """Format an Egyptian Decans chart for the AI prompt."""
    sections = ["【古埃及十度區間排盤 Egyptian Decans Chart】"]
    sections.append(f"Sun Decan: {_safe_getattr(chart, 'sun_decan')}")
    sections.append(f"Moon Decan: {_safe_getattr(chart, 'moon_decan')}")
    sections.append(f"ASC Decan: {_safe_getattr(chart, 'asc_decan')}")
    sections.append("\n--- Planets ---")
    sections.append(_format_planet_list(getattr(chart, 'planets', [])))
    return "\n".join(sections)


def format_nadi_chart(chart) -> str:
    """Format a Nadi Jyotish chart for the AI prompt."""
    sections = ["【納迪占星排盤 Nadi Chart】"]
    sections.append(f"Nadi Type: {_safe_getattr(chart, 'nadi_type')}")
    sections.append(f"Nakshatra: {_safe_getattr(chart, 'birth_nakshatra', 'nakshatra')}")
    sections.append("\n--- Planets ---")
    sections.append(_format_planet_list(getattr(chart, 'planets', [])))
    return "\n".join(sections)


def format_zurkhai_chart(chart) -> str:
    """Format a Mongolian Zurkhai chart for the AI prompt."""
    sections = ["【蒙古祖爾海排盤 Zurkhai Chart】"]
    sections.append(f"Animal: {_safe_getattr(chart, 'animal', 'birth_animal')}")
    sections.append(f"Element: {_safe_getattr(chart, 'element', 'birth_element')}")
    sections.append(f"Mewa: {_safe_getattr(chart, 'mewa')}")
    sections.append(f"Parkha: {_safe_getattr(chart, 'parkha')}")
    sections.append("\n--- Planets ---")
    sections.append(_format_planet_list(getattr(chart, 'planets', [])))
    return "\n".join(sections)


def format_hellenistic_chart(chart) -> str:
    """Format a Hellenistic chart for the AI prompt."""
    sections = ["【希臘占星排盤 Hellenistic Chart】"]
    sections.append(f"ASC: {_safe_getattr(chart, 'asc_sign')}")
    sections.append(f"MC: {_safe_getattr(chart, 'mc_sign')}")
    sections.append(f"Sect: {_safe_getattr(chart, 'sect')}")
    sections.append(f"Lot of Fortune: {_safe_getattr(chart, 'lot_of_fortune')}")
    sections.append("\n--- Planets ---")
    sections.append(_format_planet_list(getattr(chart, 'planets', [])))
    sections.append("\n--- Aspects ---")
    sections.append(_format_aspects(getattr(chart, 'aspects', [])))
    return "\n".join(sections)


def format_sukkayodo_chart(chart) -> str:
    """Format a Sukkayodo chart for the AI prompt."""
    sections = ["【宿曜道排盤 Sukkayodo Chart】"]
    sections.append(f"Birth Mansion: {_safe_getattr(chart, 'birth_mansion', 'mansion')}")
    sections.append("\n--- Planets ---")
    sections.append(_format_planet_list(getattr(chart, 'planets', [])))
    return "\n".join(sections)


def format_chinstar_chart(chart_data: dict) -> str:
    """Format a 萬花仙禽 (Chinstar) chart for the AI prompt."""
    sections = ["【萬花仙禽排盤 Chinstar Chart】"]
    if isinstance(chart_data, dict):
        for k, v in chart_data.items():
            sections.append(f"{k}: {v}")
    else:
        sections.append(format_generic_chart(chart_data, "萬花仙禽"))
    return "\n".join(sections)


def format_generic_chart(chart, system_name: str = "Unknown") -> str:
    """Fallback formatter for any chart object — dumps all public attributes."""
    sections = [f"【{system_name}】"]
    if isinstance(chart, dict):
        for k, v in chart.items():
            sections.append(f"{k}: {v}")
    else:
        for attr in sorted(dir(chart)):
            if attr.startswith("_"):
                continue
            val = getattr(chart, attr, None)
            if callable(val):
                continue
            sections.append(f"{attr}: {val}")
    return "\n".join(sections)


# Mapping from system key to formatter function
SYSTEM_FORMATTERS = {
    "tab_chinese": format_chinese_chart,
    "tab_ziwei": format_ziwei_chart,
    "tab_western": format_western_chart,
    "tab_indian": format_vedic_chart,
    "tab_sukkayodo": format_sukkayodo_chart,
    "tab_thai": format_thai_chart,
    "tab_kabbalistic": format_kabbalistic_chart,
    "tab_arabic": format_arabic_chart,
    "tab_maya": format_maya_chart,
    "tab_mahabote": format_mahabote_chart,
    "tab_decans": format_decan_chart,
    "tab_nadi": format_nadi_chart,
    "tab_zurkhai": format_zurkhai_chart,
    "tab_hellenistic": format_hellenistic_chart,
    "tab_chinstar": format_chinstar_chart,
}


def format_chart_for_prompt(system_key: str, chart) -> str:
    """Format a chart object into a text prompt for AI analysis.

    Parameters
    ----------
    system_key : str
        One of the _SYSTEM_KEYS (e.g. ``"tab_western"``).
    chart : object
        The chart object returned by the compute function.

    Returns
    -------
    str
        Human-readable chart data for the AI prompt.
    """
    formatter = SYSTEM_FORMATTERS.get(system_key)
    if formatter:
        return formatter(chart)
    return format_generic_chart(chart, system_key)
