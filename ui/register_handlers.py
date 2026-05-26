"""Auto-registration for all astrology system handlers.

This module provides a centralized registration mechanism for all 70+ handlers,
keeping app.py clean and maintainable.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Dict

if TYPE_CHECKING:
    from ui.system_engine import SystemEngine, SystemHandler


def register_all_handlers(
    registry: "SystemEngine",
    ai_button_sink: Callable,
) -> int:
    """
    Modern modular registration entry point.

    All handlers are expected to expose a `register(registry, ai_button_sink)` function
    that handles its own imports (true lazy loading).
    """
    registered_count = 0

    # List of modules that provide self-contained registration
    # (All modern self-registering handlers — generated during 全部 migration)
    handler_modules = [
        # Core + Phase 1
        "ui.system_handlers.phase1_handlers",          # Ziwei (紫微)
        "ui.system_handlers.build_andean_handler",     # Andean

        # Chinese / East Asian core
        "ui.system_handlers.build_bazi_handler",       # Bazi 八字
        "ui.system_handlers.build_damo_handler",       # Damo 達摩神數
        "ui.system_handlers.build_tieban_handler",     # Tieban 鐵板神數
        "ui.system_handlers.build_chinese_handler",    # Qizheng / 七政四餘
        "ui.system_handlers.build_beiji_handler",      # Beiji 北極神數
        "ui.system_handlers.build_nanji_handler",      # Nanji 南極神數
        "ui.system_handlers.build_wuyunliuqi_handler", # Wuyunliuqi 五運六氣
        "ui.system_handlers.build_twelve_ci_handler",  # Twelve Ci 十二次
        "ui.system_handlers.build_chinstar_handler",   # Chinstar 萬化仙禽
        "ui.system_handlers.build_liuren_handler",     # Liuren 大六壬
        "ui.system_handlers.build_taiyi_handler",      # Taiyi 太乙神數
        "ui.system_handlers.build_qimen_handler",      # Qimen 奇門遁甲
        "ui.system_handlers.build_zurkhai_handler",    # Zurkhai 蒙古祖爾海

        # Western core + advanced
        "ui.system_handlers.build_western_handler",    # Western (西洋占星)
        "ui.system_handlers.build_vedic_handler",      # Vedic (印度占星)
        "ui.system_handlers.build_hellenistic_handler",# Hellenistic
        "ui.system_handlers.build_uranian_handler",    # Uranian (漢堡學派)
        "ui.system_handlers.build_harmonic_handler",   # Harmonic
        "ui.system_handlers.build_sabian_handler",     # Sabian
        "ui.system_handlers.build_astrocartography_handler", # Astrocartography

        # Indian branches
        "ui.system_handlers.build_jaimini_handler",    # Jaimini
        "ui.system_handlers.build_nadi_handler",       # Nadi
        "ui.system_handlers.build_lal_kitab_handler",  # Lal Kitab
        "ui.system_handlers.build_kp_handler",         # KP System

        # Asian / Southeast
        "ui.system_handlers.build_thai_handler",       # Thai 泰國占星
        "ui.system_handlers.build_burmese_handler",    # Burmese Mahabote
        "ui.system_handlers.build_tibetan_handler",    # Tibetan 藏傳
        "ui.system_handlers.build_nine_star_ki_handler", # Nine Star Ki
        "ui.system_handlers.build_wariga_handler",     # Wariga
        "ui.system_handlers.build_weton_handler",      # Jawa Weton
        "ui.system_handlers.build_bintang_handler",    # Bintang Duabelas
        "ui.system_handlers.build_kinketika_handler",  # Kinketika

        # Middle East / Arabic family
        "ui.system_handlers.build_arabic_handler",     # Arabic
        "ui.system_handlers.build_yemeni_handler",     # Yemeni
        "ui.system_handlers.build_picatrix_handler",   # Picatrix
        "ui.system_handlers.build_persian_handler",    # Persian / Sasanian

        # Americas & Africa
        "ui.system_handlers.build_maya_handler",       # Maya
        "ui.system_handlers.build_aztec_handler",      # Aztec
        "ui.system_handlers.build_amazigh_handler",    # Amazigh
        "ui.system_handlers.build_dogon_handler",      # Dogon
        "ui.system_handlers.build_bahre_hasab_handler",# Bahre Hasab

        # Ancient / Obscure
        "ui.system_handlers.build_babylonian_handler", # Babylonian
        "ui.system_handlers.build_egyptian_handler",   # Egyptian Decans
        "ui.system_handlers.build_kabbalistic_handler",# Kabbalistic
        "ui.system_handlers.build_mazzalot_handler",   # Jewish Mazzalot
        "ui.system_handlers.build_etruscan_handler",   # Etruscan
        "ui.system_handlers.build_armenian_handler",   # Armenian
        "ui.system_handlers.build_polynesian_handler", # Polynesian
        "ui.system_handlers.build_geomancy_handler",   # Geomancy

        # Specialized
        "ui.system_handlers.build_medical_handler",    # Medical Astrology
        "ui.system_handlers.build_byzantine_handler",  # Byzantine
        "ui.system_handlers.build_horary_handler",     # Horary
        "ui.system_handlers.build_electional_handler", # Electional
        "ui.system_handlers.build_sports_handler",     # Sports
        "ui.system_handlers.build_mundane_handler",    # Mundane

        # More Asian / Other
        "ui.system_handlers.build_celtic_handler",
        "ui.system_handlers.build_cetian_handler",
        "ui.system_handlers.build_chunzi_handler",
        "ui.system_handlers.build_cosmobiology_handler",
        "ui.system_handlers.build_diqiyijue_handler",
        "ui.system_handlers.build_kaiyuan_handler",
        "ui.system_handlers.build_laos_handler",
        "ui.system_handlers.build_liuyao_lifetime_handler",
        "ui.system_handlers.build_shanghan_qianfa_handler",
        "ui.system_handlers.build_sukkayodo_handler",
        "ui.system_handlers.build_taixuan_handler",
        "ui.system_handlers.build_tojeong_handler",
        # ... (add any remaining as their register() is completed)
    ]

    for mod_name in handler_modules:
        try:
            mod = __import__(mod_name, fromlist=["register"])
            if hasattr(mod, "register"):
                mod.register(registry, ai_button_sink)
                registered_count += 1
        except Exception as e:
            print(f"[Handler Registry] Failed to register {mod_name}: {e}")

    print(f"[Handler Registry] Registered {registered_count} handlers (modular mode)")
    return registered_count


# ============================================================
# DEAD CODE — removed during "全部" self-register migration
# All handlers now live in their own build_xxx_handler.py with
# a register(registry, ai_button_sink) that does true lazy imports.
# The giant central maps below are no longer called from anywhere.
# Safe to delete after final verification.
# ============================================================

# _register_self_registering_handlers, _register_phase1_3,
# _build_function_maps, _register_phase4 and the old handlers_config
# have been fully superseded by the modular handler_modules list above.
# (Kept as comments only for git history / rollback reference.)

# (200+ lines of old centralized Phase 4 logic removed — see git diff)
