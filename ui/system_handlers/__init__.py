"""System handlers for executable registry.

Auto-generated exports for all astrology system handlers.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

# Phase 1 handlers (established)
from .phase1_handlers import build_ziwei_handler

# Phase 2 handlers (modern packages)
from .build_andean_handler import build_andean_handler

# Phase 3 handlers (major systems with full sub-tab support)
from .build_western_handler import build_western_handler
from .build_vedic_handler import build_vedic_handler
from .build_chinese_handler import build_chinese_handler

# Phase 4 handlers (batch generated - Chinese systems)
from .build_bazi_handler import build_bazi_handler
from .build_damo_handler import build_damo_handler
from .build_tieban_handler import build_tieban_handler
from .build_cetian_handler import build_cetian_handler
from .build_diqiyijue_handler import build_diqiyijue_handler
from .build_beiji_handler import build_beiji_handler
from .build_nanji_handler import build_nanji_handler
from .build_chunzi_handler import build_chunzi_handler
from .build_kaiyuan_handler import build_kaiyuan_handler
from .build_twelve_ci_handler import build_twelve_ci_handler
from .build_wuyunliuqi_handler import build_wuyunliuqi_handler
from .build_chinstar_handler import build_chinstar_handler
from .build_liuren_handler import build_liuren_handler
from .build_taiyi_handler import build_taiyi_handler
from .build_qimen_handler import build_qimen_handler
from .build_liuyao_lifetime_handler import build_liuyao_lifetime_handler
from .build_shanghan_qianfa_handler import build_shanghan_qianfa_handler
from .build_taixuan_handler import build_taixuan_handler

# Phase 4 handlers (batch generated - Western systems)
from .build_hellenistic_handler import build_hellenistic_handler
from .build_uranian_handler import build_uranian_handler
from .build_harmonic_handler import build_harmonic_handler
from .build_draconic_handler import build_draconic_handler
from .build_sabian_handler import build_sabian_handler
from .build_astrocartography_handler import build_astrocartography_handler
from .build_cosmobiology_handler import build_cosmobiology_handler
from .build_celtic_handler import build_celtic_handler

# Phase 4 handlers (batch generated - Indian systems)
from .build_jaimini_handler import build_jaimini_handler
from .build_nadi_handler import build_nadi_handler
from .build_lal_kitab_handler import build_lal_kitab_handler
from .build_kp_handler import build_kp_handler

# Phase 4 handlers (batch generated - Asian systems)
from .build_thai_handler import build_thai_handler
from .build_burmese_handler import build_burmese_handler
from .build_tibetan_handler import build_tibetan_handler
from .build_zurkhai_handler import build_zurkhai_handler
from .build_nine_star_ki_handler import build_nine_star_ki_handler
from .build_wariga_handler import build_wariga_handler
from .build_weton_handler import build_weton_handler
from .build_bintang_handler import build_bintang_handler
from .build_kinketika_handler import build_kinketika_handler
from .build_laos_handler import build_laos_handler
from .build_brahma_jati_handler import build_brahma_jati_handler
from .build_sukkayodo_handler import build_sukkayodo_handler
from .build_tojeong_handler import build_tojeong_handler

# Phase 4 handlers (batch generated - Middle East systems)
from .build_arabic_handler import build_arabic_handler
from .build_yemeni_handler import build_yemeni_handler
from .build_picatrix_handler import build_picatrix_handler
from .build_persian_handler import build_persian_handler

# Phase 4 handlers (batch generated - African systems)
from .build_maya_handler import build_maya_handler
from .build_aztec_handler import build_aztec_handler
from .build_amazigh_handler import build_amazigh_handler
from .build_dogon_handler import build_dogon_handler
from .build_bahre_hasab_handler import build_bahre_hasab_handler

# Phase 4 handlers (batch generated - Ancient/Obscure systems)
from .build_babylonian_handler import build_babylonian_handler
from .build_egyptian_handler import build_egyptian_handler
from .build_kabbalistic_handler import build_kabbalistic_handler
from .build_mazzalot_handler import build_mazzalot_handler
from .build_etruscan_handler import build_etruscan_handler
from .build_armenian_handler import build_armenian_handler
from .build_polynesian_handler import build_polynesian_handler
from .build_geomancy_handler import build_geomancy_handler

# Phase 4 handlers (batch generated - Specialized systems)
from .build_medical_handler import build_medical_handler
from .build_byzantine_handler import build_byzantine_handler
from .build_horary_handler import build_horary_handler
from .build_electional_handler import build_electional_handler
from .build_sports_handler import build_sports_handler
from .build_mundane_handler import build_mundane_handler

__all__ = [
    # Phase 1
    "build_ziwei_handler",
    # Phase 2
    "build_andean_handler",
    # Phase 3
    "build_western_handler",
    "build_vedic_handler",
    "build_chinese_handler",
    # Phase 4 - Chinese
    "build_bazi_handler",
    "build_damo_handler",
    "build_tieban_handler",
    "build_cetian_handler",
    "build_diqiyijue_handler",
    "build_beiji_handler",
    "build_nanji_handler",
    "build_chunzi_handler",
    "build_kaiyuan_handler",
    "build_twelve_ci_handler",
    "build_wuyunliuqi_handler",
    "build_chinstar_handler",
    "build_liuren_handler",
    "build_taiyi_handler",
    "build_qimen_handler",
    "build_liuyao_lifetime_handler",
    "build_shanghan_qianfa_handler",
    "build_taixuan_handler",
    # Phase 4 - Western
    "build_hellenistic_handler",
    "build_uranian_handler",
    "build_harmonic_handler",
    "build_draconic_handler",
    "build_sabian_handler",
    "build_astrocartography_handler",
    "build_cosmobiology_handler",
    "build_celtic_handler",
    # Phase 4 - Indian
    "build_jaimini_handler",
    "build_nadi_handler",
    "build_lal_kitab_handler",
    "build_kp_handler",
    # Phase 4 - Asian
    "build_thai_handler",
    "build_burmese_handler",
    "build_tibetan_handler",
    "build_zurkhai_handler",
    "build_nine_star_ki_handler",
    "build_wariga_handler",
    "build_weton_handler",
    "build_bintang_handler",
    "build_kinketika_handler",
    "build_laos_handler",
    "build_brahma_jati_handler",
    "build_sukkayodo_handler",
    "build_tojeong_handler",
    # Phase 4 - Middle East
    "build_arabic_handler",
    "build_yemeni_handler",
    "build_picatrix_handler",
    "build_persian_handler",
    # Phase 4 - African
    "build_maya_handler",
    "build_aztec_handler",
    "build_amazigh_handler",
    "build_dogon_handler",
    "build_bahre_hasab_handler",
    # Phase 4 - Ancient/Obscure
    "build_babylonian_handler",
    "build_egyptian_handler",
    "build_kabbalistic_handler",
    "build_mazzalot_handler",
    "build_etruscan_handler",
    "build_armenian_handler",
    "build_polynesian_handler",
    "build_geomancy_handler",
    # Phase 4 - Specialized
    "build_medical_handler",
    "build_byzantine_handler",
    "build_horary_handler",
    "build_electional_handler",
    "build_sports_handler",
    "build_mundane_handler",
]
