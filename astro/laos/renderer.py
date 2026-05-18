"""Laos Horasat renderer.

提供老撾占星專屬的金色＋深藍宇宙風格渲染：
- 婆羅門占星輪 SVG（🌀）
- Streamlit 分頁展示（老撾日期、特殊年份、ສັງຄົມ、ສີກາດ）
"""

from __future__ import annotations

import math
from typing import Any, Callable, Dict

from .calculator import LaoChart, chart_to_dict
from .data.symbols import BRAHMAN_WHEEL_SYMBOLS

# BRAHMAN_WHEEL_SYMBOLS 中 0~6 分別代表七曜順序鍵值。
_WHEEL_SYMBOL_KEYS: Dict[str, str] = {
    "sun": "0",
    "moon": "1",
    "mercury": "2",
    "venus": "3",
    "mars": "4",
    "jupiter": "5",
    "saturn": "6",
}

_SPECIAL_YEAR_DISPLAY_LIMIT = 6


def _polar(cx: float, cy: float, r: float, angle_deg: float) -> tuple[float, float]:
    """極座標轉平面座標。"""

    rad = math.radians(angle_deg - 90)
    return cx + r * math.cos(rad), cy + r * math.sin(rad)


def _planet_symbol(key: str) -> str:
    """回傳行星符號，優先使用 symbols.py。"""

    if key in ("rahu", "ketu"):
        return "☊" if key == "rahu" else "☋"
    mapped = BRAHMAN_WHEEL_SYMBOLS.get(_WHEEL_SYMBOL_KEYS.get(key, ""), {})
    return mapped.get("unicode", "✶")


def _to_dict(chart: LaoChart | Dict[str, Any]) -> Dict[str, Any]:
    """統一 chart 輸入格式，支援 dataclass 與 dict。"""

    if isinstance(chart, LaoChart):
        return chart_to_dict(chart)
    if isinstance(chart, dict):
        return chart
    raise TypeError("chart 必須是 LaoChart 或 dict")


def build_lao_brahma_wheel_svg(chart: LaoChart | Dict[str, Any], *, size: int = 700) -> str:
    """建立老撾婆羅門占星輪 SVG。"""

    data = _to_dict(chart)
    planets = data.get("planets", [])
    lao_date = data.get("lao_date", {})
    sangkhom = data.get("sangkhom", {})

    cx = cy = size / 2
    r_outer = size * 0.43
    r_inner = size * 0.18
    r_planet = size * 0.34
    r_house_label = size * 0.395

    lao_houses = [
        "ເມສ", "ພຶດສະພາ", "ມິຖຸນ", "ກະກົດ", "ສິງ", "ກັນຍາ",
        "ຕຸລາ", "ພະຈິກ", "ທະນູ", "ມັງກອນ", "ກຸມພາ", "ມີນ",
    ]

    parts = [
        '<div style="width:100%;max-width:820px;margin:0 auto;overflow-x:auto;">',
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" style="width:100%;height:auto;display:block;">',
        "<defs>",
        "<radialGradient id='laoCosmic' cx='50%' cy='50%' r='60%'>",
        "<stop offset='0%' stop-color='#101d44'/>",
        "<stop offset='100%' stop-color='#070d23'/>",
        "</radialGradient>",
        "<linearGradient id='laoGold' x1='0%' y1='0%' x2='100%' y2='100%'>",
        "<stop offset='0%' stop-color='#f5dd93'/>",
        "<stop offset='100%' stop-color='#b8860b'/>",
        "</linearGradient>",
        "</defs>",
        f"<rect x='0' y='0' width='{size}' height='{size}' fill='url(#laoCosmic)' rx='20'/>",
        f"<circle cx='{cx}' cy='{cy}' r='{r_outer + 14}' fill='none' stroke='url(#laoGold)' stroke-width='2.6' opacity='0.95'/>",
        f"<circle cx='{cx}' cy='{cy}' r='{r_outer}' fill='none' stroke='#c79b31' stroke-width='1.6' opacity='0.9'/>",
        f"<circle cx='{cx}' cy='{cy}' r='{r_inner}' fill='#0e1638' stroke='#d4af37' stroke-width='1.8'/>",
    ]

    # 12 宮分割
    for i in range(12):
        angle = i * 30
        x1, y1 = _polar(cx, cy, r_inner, angle)
        x2, y2 = _polar(cx, cy, r_outer, angle)
        lx, ly = _polar(cx, cy, r_house_label, angle + 15)
        parts.append(
            f"<line x1='{x1:.2f}' y1='{y1:.2f}' x2='{x2:.2f}' y2='{y2:.2f}' stroke='#b8902e' stroke-width='1.1' opacity='0.88'/>"
        )
        parts.append(
            f"<text x='{lx:.2f}' y='{ly:.2f}' text-anchor='middle' dominant-baseline='middle' fill='#f2d48a' font-size='12' font-family='Noto Sans Lao, sans-serif'>{lao_houses[i]}</text>"
        )

    # 行星標記
    for p in planets:
        key = str(p.get("key", "")).lower()
        lon = float(p.get("longitude", 0.0))
        symbol = _planet_symbol(key)
        px, py = _polar(cx, cy, r_planet, lon)
        parts.append(
            f"<circle cx='{px:.2f}' cy='{py:.2f}' r='13' fill='#0a1026' stroke='#e4be59' stroke-width='1.2'/>"
        )
        parts.append(
            f"<text x='{px:.2f}' y='{py:.2f}' text-anchor='middle' dominant-baseline='middle' fill='#f4de9a' font-size='16'>{symbol}</text>"
        )

    # 中心資訊
    parts.extend(
        [
            f"<text x='{cx}' y='{cy - 32}' text-anchor='middle' fill='#f4de9a' font-size='24' font-family='Noto Sans Lao, sans-serif'>🌀</text>",
            f"<text x='{cx}' y='{cy - 10}' text-anchor='middle' fill='#f0d080' font-size='15' font-family='Noto Sans Lao, sans-serif'>ໄທຣາສາດລາວ</text>",
            f"<text x='{cx}' y='{cy + 10}' text-anchor='middle' fill='#d9bc76' font-size='12'>{lao_date.get('full_lao_date', '')}</text>",
            f"<text x='{cx}' y='{cy + 30}' text-anchor='middle' fill='#ffdf8d' font-size='13' font-weight='bold'>{sangkhom.get('status', '')}</text>",
        ]
    )

    parts.append("</svg></div>")
    return "\n".join(parts)


def render_lao_horasat(
    chart: LaoChart | Dict[str, Any],
    *,
    lang: str = "zh",
    after_chart_hook: Callable[[], None] | None = None,
) -> None:
    """Streamlit 老撾占星頁面渲染。"""

    import streamlit as st

    _ = lang  # 保留未來多語擴充介面
    data = _to_dict(chart)
    lao_date = data.get("lao_date", {})
    special_year = data.get("special_year", {})
    sangkhom = data.get("sangkhom", {})
    sikarat = data.get("sikarat", {})

    st.markdown(
        """
        <style>
        .lao-cosmic-panel {
            background: linear-gradient(135deg, #09153a 0%, #0e1d4f 55%, #14235a 100%);
            border: 1px solid rgba(232, 193, 84, 0.55);
            border-radius: 14px;
            padding: 14px 16px;
            color: #f5df9d;
            box-shadow: 0 0 24px rgba(10, 20, 60, 0.42);
            margin-bottom: 12px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="lao-cosmic-panel">
          <h3 style="margin:0;color:#f5df9d;">🇱🇦 老撾占星（ໄທຣາສາດລາວ）</h3>
          <p style="margin:6px 0 0 0;color:#d7b96e;">金色古典 × 深藍宇宙 · ປະຕິທິນ · ສັງຄົມ · ສີກາດ · ພຣະລໍ້ບຣາຮມັນ</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(build_lao_brahma_wheel_svg(data), unsafe_allow_html=True)

    if after_chart_hook:
        after_chart_hook()

    tab_date, tab_sangkhom, tab_sikarat, tab_planets = st.tabs(
        ["📅 Laos 日期", "🧿 ສັງຄົມ", "⏰ ສີກາດ", "🪐 星曜"]
    )

    with tab_date:
        st.write(f"**老撾日期**：{lao_date.get('full_lao_date_with_weekday', '—')}")
        st.write(f"**季節**：{lao_date.get('season', '—')}")
        st.write(f"**特殊年份**：{special_year.get('description', '普通年份')}")
        st.json(limited_dict(special_year, _SPECIAL_YEAR_DISPLAY_LIMIT), expanded=False)

    with tab_sangkhom:
        st.write(f"**活動**：{sangkhom.get('activity', '—')}")
        st.write(f"**吉凶**：{sangkhom.get('status', '—')}")
        st.write(f"**建議**：{sangkhom.get('recommendation', '—')}")
        st.caption(sangkhom.get("month_note", ""))

    with tab_sikarat:
        st.write(f"**時段體系**：{sikarat.get('sikarat_type', '—')}")
        st.write(f"**當前時段**：{sikarat.get('period_name', '—')} · {sikarat.get('status', '—')}")
        for hour_text in sikarat.get("best_hours", []):
            st.markdown(f"- {hour_text}")

    with tab_planets:
        rows = []
        for p in data.get("planets", []):
            rows.append(
                {
                    "星曜": f"{p.get('symbol', '')} {p.get('key', '').upper()}",
                    "黃經": f"{float(p.get('longitude', 0.0)):.2f}°",
                    "宮位": p.get("house", "-"),
                    "逆行": "是" if p.get("retrograde") else "否",
                }
            )
        st.dataframe(rows, width="stretch")


def limited_dict(data: Dict[str, Any], max_items: int) -> Dict[str, Any]:
    """避免 UI 一次輸出過大 dict。"""

    items = list(data.items())
    return dict(items[:max_items])


def render_streamlit(
    chart: LaoChart | Dict[str, Any],
    *,
    lang: str = "zh",
    after_chart_hook: Callable[[], None] | None = None,
) -> None:
    """相容命名：供 app.py 直接使用。"""

    render_lao_horasat(chart, lang=lang, after_chart_hook=after_chart_hook)
