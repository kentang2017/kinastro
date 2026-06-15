"""Ziwei annual flow-year palace resolution (流年宮 / 小限宮 / 大限)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

TIANGAN_INDEX = {stem: idx for idx, stem in enumerate("甲乙丙丁戊己庚辛壬癸")}


@dataclass
class ZiweiFlowPalaces:
    virtual_age: int
    liunian_gz: str
    liunian_branch: str
    liunian_palace_name: str
    liunian_palace_branch: str
    liunian_stars: list[str]
    liunian_aux_stars: list[str]
    liunian_sihua: dict[str, str]
    xiaoxian_palace_name: str
    xiaoxian_palace_branch: str
    xiaoxian_stars: list[str]
    xiaoxian_aux_stars: list[str]
    daxian_palace_name: str
    daxian_range: str
    direction: str


def _palace_by_branch(chart: Any, branch: int) -> Any | None:
    for palace in getattr(chart, "palaces", []):
        if getattr(palace, "branch", None) == branch:
            return palace
    return None


def _palace_by_branch_name(chart: Any, branch_name: str) -> Any | None:
    for palace in getattr(chart, "palaces", []):
        if getattr(palace, "branch_name", "") == branch_name:
            return palace
    return None


def _is_forward_xiaoxian(chart: Any) -> bool:
    """陽男陰女順行，陰男陽女逆行。"""
    gender = getattr(chart, "gender", "男")
    yin_yang = getattr(chart, "yin_yang", "陽")
    return (yin_yang == "陽" and gender == "男") or (yin_yang == "陰" and gender == "女")


def resolve_xiaoxian_palace(chart: Any, virtual_age: int) -> Any | None:
    if virtual_age < 1:
        return None
    ming_branch = getattr(chart, "ming_gong_branch", 0)
    offset = virtual_age - 1
    if _is_forward_xiaoxian(chart):
        branch = (ming_branch + offset) % 12
    else:
        branch = (ming_branch - offset) % 12
    return _palace_by_branch(chart, branch)


def resolve_liunian_palace(chart: Any, liunian_branch: str) -> Any | None:
    """流年宮：太歲地支臨宮。"""
    return _palace_by_branch_name(chart, liunian_branch)


def resolve_daxian_palace(chart: Any, virtual_age: int) -> Any | None:
    for palace in getattr(chart, "palaces", []):
        start = getattr(palace, "da_xian_start", 0)
        if start <= virtual_age <= start + 9:
            return palace
    return None


def _liunian_sihua(liunian_gz: str, chart: Any) -> dict[str, str]:
    from astro.ziwei import SIHUA_TABLE

    if len(liunian_gz) < 1 or liunian_gz[0] not in TIANGAN_INDEX:
        return {}
    stem_idx = TIANGAN_INDEX[liunian_gz[0]]
    lu, quan, ke, ji = SIHUA_TABLE[stem_idx]
    result = {"化祿": lu, "化權": quan, "化科": ke, "化忌": ji}
    for palace in getattr(chart, "palaces", []):
        stars = list(getattr(palace, "stars", [])) + list(getattr(palace, "aux_stars", []))
        for star in stars:
            if star == ji:
                result["化忌落宮"] = getattr(palace, "name", "")
            if star == lu:
                result["化祿落宮"] = getattr(palace, "name", "")
    return result


def resolve_ziwei_flow_palaces(
    chart: Any,
    virtual_age: int,
    liunian_gz: str,
    liunian_branch: str,
) -> ZiweiFlowPalaces:
    liunian_palace = resolve_liunian_palace(chart, liunian_branch)
    xiaoxian_palace = resolve_xiaoxian_palace(chart, virtual_age)
    daxian_palace = resolve_daxian_palace(chart, virtual_age)
    return ZiweiFlowPalaces(
        virtual_age=virtual_age,
        liunian_gz=liunian_gz,
        liunian_branch=liunian_branch,
        liunian_palace_name=getattr(liunian_palace, "name", "") if liunian_palace else "",
        liunian_palace_branch=getattr(liunian_palace, "branch_name", "") if liunian_palace else "",
        liunian_stars=list(getattr(liunian_palace, "stars", [])) if liunian_palace else [],
        liunian_aux_stars=list(getattr(liunian_palace, "aux_stars", [])) if liunian_palace else [],
        liunian_sihua=_liunian_sihua(liunian_gz, chart),
        xiaoxian_palace_name=getattr(xiaoxian_palace, "name", "") if xiaoxian_palace else "",
        xiaoxian_palace_branch=getattr(xiaoxian_palace, "branch_name", "") if xiaoxian_palace else "",
        xiaoxian_stars=list(getattr(xiaoxian_palace, "stars", [])) if xiaoxian_palace else [],
        xiaoxian_aux_stars=list(getattr(xiaoxian_palace, "aux_stars", [])) if xiaoxian_palace else [],
        daxian_palace_name=getattr(daxian_palace, "name", "") if daxian_palace else "",
        daxian_range=getattr(daxian_palace, "da_xian", "") if daxian_palace else "",
        direction="順行" if _is_forward_xiaoxian(chart) else "逆行",
    )