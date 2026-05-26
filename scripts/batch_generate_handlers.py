#!/usr/bin/env python3
"""
Batch generate handlers for all remaining astrology systems.

This script scans the astro/ directory for compute/render function pairs
and generates handler files for each system.
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.generate_handler import generate_handler

# Define systems to generate handlers for
# Format: (system_id, system_name_zh, system_name_en, compute_fn, render_fn, category)
SYSTEMS = [
    # Chinese systems
    ("tab_bazi", "八字", "Bazi", "compute_bazi_chart", "render_bazi_chart_svg", "cat_chinese"),
    ("tab_damo", "達摩一掌經", "Damo", "compute_damo_chart", "render_damo_chart", "cat_chinese"),
    ("tab_tieban", "鐵板神數", "Tie Ban", "compute_tieban_chart", "render_tieban_chart_svg", "cat_chinese"),
    ("tab_cetian", "策天飛星", "Ce Tian", "compute_cetian_ziwei_chart", "render_cetian_ziwei_chart", "cat_chinese"),
    ("tab_diqiyijue", "滌器遺訣", "Diqiyijue", "compute_diqiyijue_chart", "render_diqiyijue_chart", "cat_chinese"),
    ("tab_beiji", "北極神數", "Beiji", "compute_beiji_chart", "render_beiji_chart", "cat_chinese"),
    ("tab_nanji", "南極神數", "Nanji", "compute_nanji_chart", "render_nanji_chart", "cat_chinese"),
    ("tab_chunzi", "蠢子數", "ChunZi", "compute_chunzi_chart", "render_chunzi_chart", "cat_chinese"),
    ("tab_kaiyuan", "開元占經", "Kaiyuan", "compute_kaiyuan_chart", "render_kaiyuan_chart", "cat_chinese"),
    ("tab_twelve_ci", "十二星次", "Twelve Ci", "compute_twelve_ci_chart", "render_twelve_ci_chart", "cat_chinese"),
    ("tab_wuyunliuqi", "五運六氣", "Wu Yun Liu Qi", "compute_wuyunliuqi", "render_wuyunliuqi_chart", "cat_chinese"),
    ("tab_chinstar", "辰星", "ChinStar", "compute_chinstar_chart", "render_chinstar_chart", "cat_chinese"),

    # Three Formulae (Sanshi)
    ("tab_liuren", "大六壬", "Da Liu Ren", "compute_liuren_chart", "render_liuren_chart", "cat_sanshi"),
    ("tab_taiyi", "太乙", "Taiyi", "compute_taiyi_chart", "render_taiyi_chart", "cat_sanshi"),
    ("tab_qimen", "奇門", "Qimen", "compute_qimen_chart", "render_qimen_chart", "cat_sanshi"),

    # Western systems
    ("tab_hellenistic", "希臘占星", "Hellenistic", "compute_hellenistic_chart", "render_hellenistic_chart", "cat_western"),
    ("tab_uranian", "天王星漢堡", "Uranian", "compute_uranian_chart", "render_uranian_chart", "cat_western"),
    ("tab_harmonic", "和諧占星", "Harmonic", "compute_harmonic_chart", "render_harmonic_chart", "cat_western"),
    ("tab_draconic", " draconic 占星", "Draconic", "compute_draconic_chart", "render_draconic_chart", "cat_western"),
    ("tab_sabian", "Sabian 符號", "Sabian Symbols", "compute_sabian_chart", "render_sabian_chart", "cat_western"),
    ("tab_astrocartography", "地點占星", "Astrocartography", "compute_astrocartography", "render_astrocartography", "cat_western"),
    ("tab_cosmobiology", "宇宙生物學", "Cosmobiology", "compute_cosmobiology_chart", "render_cosmobiology", "cat_western"),
    ("tab_celtic", "凱爾特樹木", "Celtic Tree", "compute_celtic_tree_chart", "render_celtic_tree_chart", "cat_western"),

    # Vedic / Indian systems
    ("tab_jaimini", "Jaimini 占星", "Jaimini", "compute_jaimini_chart", "render_jaimini_chart", "cat_indian"),
    ("tab_nadi", "納迪占星", "Nadi", "compute_nadi_chart", "render_nadi_chart", "cat_indian"),
    ("tab_lal_kitab", "紅皮書", "Lal Kitab", "compute_lal_kitab_chart", "render_lal_kitab_chart", "cat_indian"),
    ("tab_kp", "KP 占星", "KP Astrology", "compute_kp_chart", "render_kp_chart", "cat_indian"),

    # Asian systems
    ("tab_thai", "泰國占星", "Thai", "compute_thai_chart", "render_thai_chart", "cat_asian"),
    ("tab_burmese", "緬甸占星", "Burmese", "compute_mahabote_chart", "render_mahabote_chart", "cat_asian"),
    ("tab_tibetan", "藏傳占星", "Tibetan", "compute_tibetan_chart", "render_tibetan_chart", "cat_asian"),
    ("tab_zurkhai", "蒙古祖爾海", "Zurkhai", "compute_zurkhai_chart", "render_zurkhai_chart", "cat_asian"),
    ("tab_nine_star_ki", "九星氣學", "Nine Star Ki", "compute_nine_star_ki_chart", "render_nine_star_ki_chart", "cat_asian"),
    ("tab_wariga", "巴厘 Wariga", "Wariga", "compute_wariga", "render_wariga_chart", "cat_asian"),
    ("tab_weton", "爪哇 Weton", "Weton", "compute_weton", "render_jawa_weton_chart", "cat_asian"),
    ("tab_bintang", "馬來十二星", "Bintang Duabelas", "compute_bintang_duabelas", "render_bintang_duabelas_chart", "cat_asian"),
    ("tab_kinketika", "馬來七星", "Kinketika", "compute_kinketika", "render_kinketika_chart", "cat_asian"),
    ("tab_laos", "老撾 Horasat", "Lao Horasat", "compute_lao_chart", "render_lao_horasat", "cat_asian"),
    ("tab_brahma_jati", "梵天", "Brahma Jati", "compute_brahma_jati", "render_brahma_jati", "cat_asian"),
    ("tab_sukkayodo", "宿曜道", "Sukkayodo", "compute_sukkayodo_chart", "render_sukkayodo_chart", "cat_asian"),
    ("tab_tojeong", "土亭數", "Tojeong", "compute_tojeong_chart", "render_tojeong_chart", "cat_asian"),

    # Middle East systems
    ("tab_arabic", "阿拉伯占星", "Arabic", "compute_arabic_chart", "render_arabic_chart", "cat_middle_east"),
    ("tab_yemeni", "也門占星", "Yemeni", "compute_yemeni_chart", "render_yemeni_chart", "cat_middle_east"),
    ("tab_picatrix", "Picatrix", "Picatrix", "compute_picatrix", "render_picatrix", "cat_middle_east"),
    ("tab_persian", "波斯占星", "Persian", "compute_deep_sassanian_chart", "render_deep_sassanian_chart", "cat_middle_east"),

    # African systems
    ("tab_maya", "瑪雅占星", "Maya", "compute_maya_chart", "render_maya_chart", "cat_africa"),
    ("tab_aztec", "阿茲特克", "Aztec", "compute_aztec_chart", "render_aztec_chart", "cat_africa"),
    ("tab_amazigh", "柏柏爾", "Amazigh", "compute_amazigh_chart", "render_amazigh_chart", "cat_africa"),
    ("tab_dogon", "多貢", "Dogon", "compute_dogon_sirius_chart", "render_dogon_sirius_chart", "cat_africa"),
    ("tab_bahre_hasab", "衣索比亞", "Bahre Hasab", "compute_bahre_hasab", "render_bahre_hasab", "cat_africa"),

    # Ancient / Obscure systems
    ("tab_babylonian", "巴比倫", "Babylonian", "compute_babylonian_chart", "render_babylonian_chart", "cat_ancient"),
    ("tab_egyptian", "古埃及", "Egyptian", "compute_decan_chart", "render_decan_chart", "cat_ancient"),
    ("tab_kabbalistic", "卡巴拉", "Kabbalah", "compute_kabbalistic_chart", "render_kabbalistic_chart", "cat_obscure"),
    ("tab_mazzalot", "猶太 Mazzalot", "Mazzalot", "compute_mazzalot_chart", "render_mazzalot_chart", "cat_obscure"),
    ("tab_andean", "安地斯", "Andean", "compute_andean_chart", "render_andean_chart_ui", "cat_ancient"),
    ("tab_etruscan", "伊特魯里亞", "Etruscan", "compute_etruscan_chart", "render_etruscan_chart_ui", "cat_ancient"),
    ("tab_armenian", "亞美尼亞", "Armenian", "compute_armenian_chart", "render_armenian_chart_ui", "cat_obscure"),
    ("tab_polynesian", "波利尼西亞", "Polynesian", "compute_polynesian_chart", "render_polynesian_chart_ui", "cat_ancient"),

    # Specialized systems
    ("tab_medical", "醫學占星", "Medical", "compute_medical_chart", "render_medical_chart", "cat_medical"),
    ("tab_byzantine", "拜占庭", "Byzantine", "compute_byzantine_chart", "render_byzantine_chart", "cat_medical"),
    ("tab_horary", "卜卦占星", "Horary", "compute_horary_chart", "render_horary_chart", "cat_horary"),
    ("tab_electional", "擇日占星", "Electional", "compute_electional_chart", "render_electional_chart", "cat_electional"),
    ("tab_sports", "運動占星", "Sports", "compute_sports_chart", "render_sports_chart", "cat_sports"),
    ("tab_mundane", "世俗占星", "Mundane", "compute_mundane_chart", "render_mundane_chart", "cat_mundane"),
    ("tab_geomancy", "地占", "Geomancy", "compute_geomancy_chart", "render_geomancy_chart", "cat_obscure"),

    # Other Chinese
    ("tab_liuyao_lifetime", "六爻終身卦", "Lifetime Liu Yao", "compute_lifetime_hexagram", "render_liuyao_lifetime_chart", "cat_chinese"),
    ("tab_shanghan_qianfa", "傷寒鈐法", "Shanghan Qianfa", "compute_shanghan_qianfa", "render_shanghan_qianfa_chart", "cat_chinese"),
    ("tab_taixuan", "太玄數", "Tai Xuan", "compute_taixuan_chart", "render_taixuan_chart", "cat_chinese"),
]


def main():
    """Generate all handler files."""
    output_dir = Path("ui/system_handlers")
    output_dir.mkdir(exist_ok=True)

    generated = []
    skipped = []

    # Check existing handlers
    existing_handlers = [
        "build_ziwei_handler.py",
        "build_andean_handler.py",
        "build_western_handler.py",
        "build_vedic_handler.py",
        "build_chinese_handler.py",
    ]

    for system_id, name_zh, name_en, compute_fn, render_fn, category in SYSTEMS:
        handler_filename = f"build_{system_id.replace('tab_', '')}_handler.py"
        handler_path = output_dir / handler_filename

        # Skip if already exists
        if handler_filename in existing_handlers:
            skipped.append((system_id, "already exists"))
            continue

        # Check if compute/render functions exist (soft check)
        # For now, we'll generate all and let users verify

        code = generate_handler(
            system_id=system_id,
            system_name=f"{name_zh} ({name_en})",
            compute_fn=compute_fn,
            render_fn=render_fn,
            category=category,
        )

        handler_path.write_text(code, encoding="utf-8")
        generated.append(system_id)
        print(f"[OK] Generated: {handler_filename}")

    print(f"\n{'='*60}")
    print(f"Generated: {len(generated)} handlers")
    print(f"Skipped: {len(skipped)} handlers")
    print(f"\nGenerated handlers: {generated}")
    if skipped:
        print(f"Skipped: {skipped}")


if __name__ == "__main__":
    main()
