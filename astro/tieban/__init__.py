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

使用方式：
    from astro.tieban import TieBanShenShu
    
    tbss = TieBanShenShu()
    result = tbss.calculate(birth_data, parents_data)
"""

from astro.tieban.tieban_calculator import TieBanShenShu, TieBanBirthData
from astro.tieban.tieban_renderer import render_tieban_chart_svg

__all__ = ["TieBanShenShu", "TieBanBirthData", "render_tieban_chart_svg"]
