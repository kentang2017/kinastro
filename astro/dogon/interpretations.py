"""Interpretation helpers for Dogon Sirius Cosmology."""

from __future__ import annotations

from .calculator import DogonZoneResult, SiguiCycleInfo


def build_dogon_personal_influence(
    sirius_declination: float,
    zone_result: DogonZoneResult,
    sigui: SiguiCycleInfo,
    latitude: float,
    longitude: float,
) -> tuple[str, str]:
    nearing_en = "approaching" if sigui.years_until_next <= 8 else "between"

    zone_zh = zone_result.meaning_zh
    zone_en = zone_result.meaning_en

    lat_msg_zh = "高緯度地區可見性變化較大，建議重視節律而非單點判讀。" if abs(latitude) > 66 else "可見性條件穩定，可結合年度觀測節點。"
    lat_msg_en = "At polar/high latitudes, visibility varies strongly; prioritize ritual rhythm over single-point readings." if abs(latitude) > 66 else "Visibility is relatively stable; combine with yearly observation markers."

    influence_zh = f"""你的 Sirius 赤緯為 {sirius_declination:.2f}°，落於「{zone_result.label}」：{zone_zh}。
目前位於 Sigui 50 年週期的 {nearing_year_phrase(sigui, zh=True)}，與下一次 Sigui 尚有 {sigui.years_until_next:.2f} 年。
此配置傾向在個人生命中強化『儀式記憶—祖先敘事—社群責任』三者連動。{lat_msg_zh}"""

    influence_en = (
        f"Your Sirius declination is {sirius_declination:.2f}°, mapped to '{zone_result.label}': {zone_en}. "
        f"You are {nearing_en} the 50-year Sigui pulse ({sigui.years_until_next:.2f} years to next Sigui). "
        "This pattern emphasizes ritual memory, ancestral narrative, and communal responsibility. "
        f"{lat_msg_en}"
    )

    return influence_zh, influence_en


def nearing_year_phrase(sigui: SiguiCycleInfo, zh: bool = True) -> str:
    if zh:
        return f"第 {sigui.years_since_previous:.2f} 年（上一輪 {sigui.previous_year}）"
    return f"year {sigui.years_since_previous:.2f} since {sigui.previous_year}"
