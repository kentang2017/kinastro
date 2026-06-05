"""Trung Châu Tam Hợp (中州三合派) interpretation templates and rules."""

from __future__ import annotations

TRUNG_CHAU_CORE_THEMES: dict[str, str] = {
    "psychology": "重視心理韌性、壓力管理與認知調整。",
    "physiology": "重視生理節律、作息、飲食與慢性壓力體質。",
    "self_effort": "強調後天努力可重塑命運曲線，先修身再求運。",
}

TRUNG_CHAU_PATTERNS: list[dict[str, object]] = [
    {
        "name": "紫府同宮格",
        "requires": {"all_of": ["紫微", "天府"]},
        "insight": "領導與資源調度並重，宜走管理或創業整合路線。",
        "effort": "建立制度與團隊授權可放大格局。",
    },
    {
        "name": "機月同梁格",
        "requires": {"all_of": ["天機", "太陰", "天梁"]},
        "insight": "思辨細膩且具照護傾向，適合顧問、教育、療癒領域。",
        "effort": "避免過度內耗，建立輸出節奏。",
    },
    {
        "name": "殺破狼動能格",
        "requires": {"all_of": ["七殺", "破軍", "貪狼"]},
        "insight": "高變動高成長，適合轉型、開創、跨域競爭。",
        "effort": "需嚴格風控與現金流管理。",
    },
]

DAI_HAN_STYLE_GUIDE = {
    "zh": "大限著重十年戰略：關注心理韌性、生理承載、技能升級三軸。",
    "vi": "Đại hạn nhấn mạnh chiến lược 10 năm: tâm lý, thể chất, nâng cấp kỹ năng.",
    "en": "Đại hạn emphasizes a 10-year strategy across psychology, physiology, and upskilling.",
}

LUU_NIEN_STYLE_GUIDE = {
    "zh": "流年著重年度調整：用小步迭代應對流年起伏。",
    "vi": "Lưu niên tập trung điều chỉnh theo năm bằng các bước nhỏ.",
    "en": "Lưu niên focuses on yearly calibration through small iterative steps.",
}
