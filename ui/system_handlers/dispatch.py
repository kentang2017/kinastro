"""System dispatch table for KinAstro.

Maps system IDs to their render functions.
"""
from __future__ import annotations

from typing import Callable


def _get_dispatch() -> dict[str, Callable]:
    from ui.system_handlers import chinese_systems, western_systems, vedic_systems
    from ui.system_handlers import asian_systems, mideast_systems, ancient_systems
    from ui.system_handlers import sanshi_systems

    return {
        "tab_chinese": chinese_systems.render_tab_chinese,
        "tab_cetian_ziwei": chinese_systems.render_tab_cetian_ziwei,
        "tab_tieban": chinese_systems.render_tab_tieban,
        "tab_shaozi": chinese_systems.render_tab_shaozi,
        "tab_huangji": chinese_systems.render_tab_huangji,
        "tab_taixuan": chinese_systems.render_tab_taixuan,
        "tab_wuyunliuqi": chinese_systems.render_tab_wuyunliuqi,
        "tab_damo": chinese_systems.render_tab_damo,
        "tab_diqiyijue": chinese_systems.render_tab_diqiyijue,
        "tab_twelve_ci": chinese_systems.render_tab_twelve_ci,
        "tab_chinstar": chinese_systems.render_tab_chinstar,
        "tab_liuren": chinese_systems.render_tab_liuren,
        "tab_fendjing": chinese_systems.render_tab_fendjing,
        "tab_bazi": chinese_systems.render_tab_bazi,
        "tab_chunzi": chinese_systems.render_tab_chunzi,
        "tab_kaiyuan": chinese_systems.render_tab_kaiyuan,
        "tab_beiji": chinese_systems.render_tab_beiji,
        "tab_nanji": chinese_systems.render_tab_nanji,
        "tab_western": western_systems.render_tab_western,
        "tab_sabian": western_systems.render_tab_sabian,
        "tab_hellenistic": western_systems.render_tab_hellenistic,
        "tab_babylonian": western_systems.render_tab_babylonian,
        "tab_acg": western_systems.render_tab_acg,
        "tab_uranian": western_systems.render_tab_uranian,
        "tab_cosmobiology": western_systems.render_tab_cosmobiology,
        "tab_harmonic": western_systems.render_tab_harmonic,
        "tab_primary_directions": western_systems.render_tab_primary_directions,
        "tab_rectification": western_systems.render_tab_rectification,
        "tab_trutine_of_hermes": western_systems.render_tab_trutine_of_hermes,
        "tab_esoteric": western_systems.render_tab_esoteric,
        "tab_human_design": western_systems.render_tab_human_design,
        "tab_electional": western_systems.render_tab_electional,
        "tab_mundane": western_systems.render_tab_mundane,
        "tab_fludd_rota": western_systems.render_tab_fludd_rota,
        "tab_alchemical_astrology": western_systems.render_tab_alchemical_astrology,
        "tab_history": western_systems.render_tab_history,
        "tab_wiki": western_systems.render_tab_wiki,
        "tab_indian": vedic_systems.render_tab_indian,
        "tab_vastu": vedic_systems.render_tab_vastu,
        "tab_lal_kitab": vedic_systems.render_tab_lal_kitab,
        "tab_sukkayodo": vedic_systems.render_tab_sukkayodo,
        "tab_kp": vedic_systems.render_tab_kp,
        "tab_nadi": vedic_systems.render_tab_nadi,
        "tab_jaimini": vedic_systems.render_tab_jaimini,
        "tab_thai": asian_systems.render_tab_thai,
        "tab_laos": asian_systems.render_tab_laos,
        "tab_mahabote": asian_systems.render_tab_mahabote,
        "tab_nine_star_ki": asian_systems.render_tab_nine_star_ki,
        "tab_celtic_tree": asian_systems.render_tab_celtic_tree,
        "tab_khmer": asian_systems.render_tab_khmer,
        "tab_tojeong": asian_systems.render_tab_tojeong,
        "tab_tibetan": asian_systems.render_tab_tibetan,
        "tab_zurkhai": asian_systems.render_tab_zurkhai,
        "tab_polynesian": asian_systems.render_tab_polynesian,
        "tab_wariga": asian_systems.render_tab_wariga,
        "tab_jawa_weton": asian_systems.render_tab_jawa_weton,
        "tab_bintang_duabelas": asian_systems.render_tab_bintang_duabelas,
        "tab_kinketika": asian_systems.render_tab_kinketika,
        "tab_liuyao_lifetime": asian_systems.render_tab_liuyao_lifetime,
        "tab_byzantine_astrology": asian_systems.render_tab_byzantine_astrology,
        "tab_kabbalistic": mideast_systems.render_tab_kabbalistic,
        "tab_mazzalot": mideast_systems.render_tab_mazzalot,
        "tab_arabic": mideast_systems.render_tab_arabic,
        "tab_yemeni": mideast_systems.render_tab_yemeni,
        "tab_picatrix_behenian": mideast_systems.render_tab_picatrix_behenian,
        "tab_bahre_hasab": mideast_systems.render_tab_bahre_hasab,
        "tab_dogon_sirius": mideast_systems.render_tab_dogon_sirius,
        "tab_amazigh": mideast_systems.render_tab_amazigh,
        "tab_persian": mideast_systems.render_tab_persian,
        "tab_persian_deep": mideast_systems.render_tab_persian_deep,
        "tab_astro_geomancy": mideast_systems.render_tab_astro_geomancy,
        "tab_european_geomancy": mideast_systems.render_tab_european_geomancy,
        "tab_maya": ancient_systems.render_tab_maya,
        "tab_armenian": ancient_systems.render_tab_armenian,
        "tab_andean": ancient_systems.render_tab_andean,
        "tab_etruscan": ancient_systems.render_tab_etruscan,
        "tab_aztec": ancient_systems.render_tab_aztec,
        "tab_decans": ancient_systems.render_tab_decans,
        "tab_sumerian": ancient_systems.render_tab_sumerian,
        "tab_taiyi": sanshi_systems.render_tab_taiyi,
        "tab_qimen_luming": sanshi_systems.render_tab_qimen_luming,
        "tab_medical_astrology": sanshi_systems.render_tab_medical_astrology,
        "tab_shanghan_qianfa": sanshi_systems.render_tab_shanghan_qianfa,
        "tab_horary": sanshi_systems.render_tab_horary,
        "tab_sports_astrology": sanshi_systems.render_tab_sports_astrology,
    }


_DISPATCH: dict[str, Callable] | None = None


def render_system(system_id: str) -> bool:
    """Render the given system. Returns True if handled."""
    global _DISPATCH
    if _DISPATCH is None:
        _DISPATCH = _get_dispatch()
    handler = _DISPATCH.get(system_id)
    if handler is None:
        return False
    handler()
    return True
