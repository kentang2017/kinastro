"""Vietnam Tử Vi star localization table and remedies."""

from __future__ import annotations

from astro.vietnam.models import StarProfileVN

STAR_PROFILES_VN: dict[str, StarProfileVN] = {
    "紫微": StarProfileVN("紫微", "Tử Vi", "Emperor Star", "領導、自尊、統御", "廟旺主領導格局", ["行祖先感恩儀式", "每月行善一次"]),
    "天機": StarProfileVN("天機", "Thiên Cơ", "Strategist Star", "機智、善變、思辨", "得地則智謀顯", ["建立固定作息", "避免過度思慮"]),
    "太陽": StarProfileVN("太陽", "Thái Dương", "Sun Star", "外向、責任、名望", "白天生人更顯", ["規律晨起曝曬", "提升公眾服務"]),
    "武曲": StarProfileVN("武曲", "Vũ Khúc", "Wealth General", "務實、果斷、財務", "旺則理財能力強", ["財務記帳", "避免高槓桿投機"]),
    "天同": StarProfileVN("天同", "Thiên Đồng", "Blessing Star", "溫和、享受、福氣", "逢吉更安逸", ["節制飲食", "培養耐力運動"]),
    "廉貞": StarProfileVN("廉貞", "Liêm Trinh", "Integrity Star", "魅力、原則、爭議", "化祿有名望", ["慎言", "避免情緒性決策"]),
    "天府": StarProfileVN("天府", "Thiên Phủ", "Treasury Star", "穩定、守成、資源", "主庫藏與管理", ["長期資產配置", "建立家庭儲備"]),
    "太陰": StarProfileVN("太陰", "Thái Âm", "Moon Star", "細膩、內在、安全感", "夜生較佳", ["睡眠衛生", "陰性能量調養"]),
    "貪狼": StarProfileVN("貪狼", "Tham Lang", "Desire Star", "才藝、欲望、社交", "入廟多才", ["節制酒色", "專注一項長期技能"]),
    "巨門": StarProfileVN("巨門", "Cự Môn", "Debate Star", "口才、分析、疑慮", "得化解可成名", ["溝通前先書寫", "降低無效爭辯"]),
    "天相": StarProfileVN("天相", "Thiên Tướng", "Support Star", "公正、協調、輔佐", "官祿表現佳", ["建立界線", "保持制度化工作"]),
    "天梁": StarProfileVN("天梁", "Thiên Lương", "Protection Star", "慈悲、照護、道德", "逢吉有庇蔭", ["定期義工", "健康檢查"]),
    "七殺": StarProfileVN("七殺", "Thất Sát", "Commander Star", "衝勁、決戰、冒險", "駕馭則成大器", ["風險控管", "高強度運動釋壓"]),
    "破軍": StarProfileVN("破軍", "Phá Quân", "Breaker Star", "改革、破舊立新", "宜創業轉型", ["預留現金流", "分階段變革"]),
    "火星": StarProfileVN("火星", "Hỏa Tinh", "Fire Malefic", "急躁、爆發", "遇煞增風險", ["遠離危險駕駛", "冥想降躁"]),
    "鈴星": StarProfileVN("鈴星", "Linh Tinh", "Bell Malefic", "焦慮、突發", "逢煞易受驚", ["減少熬夜", "規律呼吸訓練"]),
    "地空": StarProfileVN("地空", "Địa Không", "Void Star", "落空、空轉", "財務波動", ["建立備用金", "避免情緒性消費"]),
    "地劫": StarProfileVN("地劫", "Địa Kiếp", "Loss Star", "突損、破耗", "宜守不宜攻", ["高風險保險配置", "重要決策雙重審核"]),
}

STAR_NAME_MAP: dict[str, dict[str, str]] = {
    key: {"zh": profile.name_zh, "vi": profile.name_vi, "en": profile.name_en}
    for key, profile in STAR_PROFILES_VN.items()
}


def get_star_profile(star_name: str) -> StarProfileVN | None:
    """Return star profile if available."""
    return STAR_PROFILES_VN.get(star_name)


def get_star_name(star_name: str, lang: str = "zh") -> str:
    """Return localized star name in zh/vi/en."""
    mapping = STAR_NAME_MAP.get(star_name)
    if not mapping:
        return star_name
    return mapping.get(lang, mapping["zh"])
