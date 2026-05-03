"""
鐵板神數模組 (Tie Ban Shen Shu / Iron Plate Divine Numbers)

基於《鐵板神數清刻足本》（心一堂術數珍本古籍叢刊·星命類·神數類，2013）
底本為虛白廬藏清中葉「貞元書屋」刻本，含秘鈔密碼表

核心特點：
- 時分八刻，每刻十五分（120 分/時，融入西洋分鐘制）
- 考刻分：結合父母八字、六親信息精確定位刻分
- 八卦加則例：天干配卦、地支配卦、河洛配數
- 紫微斗數安星、十二宮、太歲祿神、大限小限
- 秘鈔密碼表：卦象、流度、納甲卦爻快速查表
- 坤集扣入法（kou_ru_fa）：萬千百十 → 天干序列
- 完整 12000 條文資料庫（TiaowenDatabase，延遲載入）
- 九十六刻天干數表（BAKE_96_KE）與六親刻分圖（SIX_QIN_KE_FEN）

使用方式：
    from astro.tieban import TieBanShenShu, TieBanBirthData

    tbss = TieBanShenShu()

    # 基本推算
    result = tbss.calculate(birth_data)

    # 查詢完整 12000 條文
    info = tbss.get_tiaowen(1001)   # -> {'text': '一樹殘花,有枝復茂', ...}

    # 坤集扣入法
    seq = tbss.kou_ru_fa(1001)      # -> ['癸', '甲', '癸', '癸', '甲']

    # 九十六刻查詢
    bake = tbss.lookup_bake_96ke('子', '父母兄弟', 0)  # -> '交初坤得'
"""

from astro.tieban.tieban_calculator import (
    TieBanShenShu,
    TieBanBirthData,
    TieBanResult,
    TiaowenDatabase,
)
from astro.tieban.tieban_renderer import render_tieban_chart_svg
from astro.tieban.kunji_full_structure import (
    kou_ru_fa,
    advanced_kou_ru_fa,
    BAKE_96_KE,
    SIX_QIN_KE_FEN,
    KUNJI_TIANGAN_CODE,
)

__all__ = [
    "TieBanShenShu",
    "TieBanBirthData",
    "TieBanResult",
    "TiaowenDatabase",
    "render_tieban_chart_svg",
    "kou_ru_fa",
    "advanced_kou_ru_fa",
    "BAKE_96_KE",
    "SIX_QIN_KE_FEN",
    "KUNJI_TIANGAN_CODE",
]
