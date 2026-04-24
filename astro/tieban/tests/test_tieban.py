"""
astro/tieban/tests/test_tieban.py — 鐵板神數模組測試

Test suite for Tie Ban Shen Shu module
"""

import sys
import os
from datetime import datetime

# 添加父目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from astro.tieban import TieBanShenShu, TieBanBirthData
from astro.tieban.tieban_calculator import Ganzhi


def test_ganzhi_creation():
    """測試干支創建"""
    print("測試干支創建...")
    
    gz = Ganzhi('甲', '子')
    assert str(gz) == '甲子'
    assert gz.stem_index == 0
    assert gz.branch_index == 0
    
    gz2 = Ganzhi.from_index(0, 0)
    assert str(gz2) == '甲子'
    
    print("✅ 干支創建測試通過")


def test_ganzhi_from_year():
    """測試從年份計算干支"""
    print("測試從年份計算干支...")
    
    # 1984 年為甲子年
    gz_1984 = Ganzhi.from_year(1984)
    assert str(gz_1984) == '甲子'
    
    # 1990 年為庚午年
    gz_1990 = Ganzhi.from_year(1990)
    assert str(gz_1990) == '庚午'
    
    # 2024 年為甲辰年
    gz_2024 = Ganzhi.from_year(2024)
    assert str(gz_2024) == '甲辰'
    
    print("✅ 年份計算干支測試通過")


def test_mapping_he_luo():
    """測試河洛配數"""
    print("測試河洛配數...")
    
    from astro.tieban.tieban_calculator import Mapping
    
    # 甲己子午 9
    assert Mapping.get_he_luo_num('甲', '子') == 9
    assert Mapping.get_he_luo_num('己', '午') == 9
    
    # 乙庚丑未 8
    assert Mapping.get_he_luo_num('乙', '丑') == 8
    assert Mapping.get_he_luo_num('庚', '未') == 8
    
    # 丙辛寅申 7
    assert Mapping.get_he_luo_num('丙', '寅') == 7
    assert Mapping.get_he_luo_num('辛', '申') == 7
    
    print("✅ 河洛配數測試通過")


def test_mapping_nayin():
    """測試納音"""
    print("測試納音...")
    
    from astro.tieban.tieban_calculator import Mapping
    
    # 甲子乙丑海中金
    assert Mapping.get_nayin(Ganzhi('甲', '子')) == '海中金'
    assert Mapping.get_nayin(Ganzhi('乙', '丑')) == '海中金'
    
    # 丙寅丁卯爐中火
    assert Mapping.get_nayin(Ganzhi('丙', '寅')) == '爐中火'
    assert Mapping.get_nayin(Ganzhi('丁', '卯')) == '爐中火'
    
    print("✅ 納音測試通過")


def test_mapping_wuxing_ju():
    """測試五行局"""
    print("測試五行局...")
    
    from astro.tieban.tieban_calculator import Mapping
    
    # 海中金 = 金四局
    nayin, ju = Mapping.get_wuxing_ju(Ganzhi('甲', '子'))
    assert nayin == '海中金'
    assert ju == 4
    
    # 爐中火 = 火六局
    nayin, ju = Mapping.get_wuxing_ju(Ganzhi('丙', '寅'))
    assert nayin == '爐中火'
    assert ju == 6
    
    print("✅ 五行局測試通過")


def test_star_placement_an_ming():
    """測試安命宮"""
    print("測試安命宮...")
    
    from astro.tieban.tieban_calculator import StarPlacement
    
    # 示例：寅月午時
    result = StarPlacement.an_ming(
        Ganzhi('庚', '午'),  # 年
        Ganzhi('戊', '寅'),  # 月（寅月）
        Ganzhi('壬', '午'),  # 時（午時）
    )
    
    assert '命宮' in result
    assert '身宮' in result
    assert result['命宮'] in ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
    
    print(f"  命宮：{result['命宮']}")
    print(f"  身宮：{result['身宮']}")
    print("✅ 安命宮測試通過")


def test_ke_fen_calculation():
    """測試考刻分"""
    print("測試考刻分...")
    
    from astro.tieban.tieban_calculator import KeFenEngine
    
    engine = KeFenEngine()
    
    # 14:30 為未時（13-15 點）
    birth_dt = datetime(1990, 5, 15, 14, 30)
    ke, fen, candidates = engine.calculate_ke_fen(birth_dt, Ganzhi('己', '未'))
    
    assert 0 <= ke <= 7
    assert 0 <= fen <= 14
    assert len(candidates) == 120  # 8 刻 × 15 分
    
    print(f"  刻：{ke}, 分：{fen}")
    print(f"  候選數：{len(candidates)}")
    print("✅ 考刻分測試通過")


def test_verse_database():
    """測試條文資料庫"""
    print("測試條文資料庫...")
    
    from astro.tieban.tieban_calculator import VerseDatabase
    
    db = VerseDatabase()
    
    # 測試查詢
    result = db.lookup('0001')
    assert isinstance(result, dict)
    assert 'verse' in result
    assert 'category' in result or result.get('category') == '綜合'
    
    print(f"  條文 0001: {result.get('verse', '')[:30]}...")
    print(f"  分類：{result.get('category', '未知')}")
    
    # 測試分類
    categories = db.get_categories()
    assert len(categories) > 0
    print(f"  分類數：{len(categories)}")
    
    # 測試搜索
    results = db.search_by_tag('父母雙全')
    assert len(results) > 0
    print(f"  '父母雙全' 標籤條文數：{len(results)}")
    
    print("✅ 條文資料庫測試通過")


def test_secret_code_table():
    """測試密碼表"""
    print("測試密碼表...")
    
    from astro.tieban.tieban_calculator import SecretCodeTable
    
    table = SecretCodeTable()
    
    # 測試查詢
    result = table.lookup('甲己子午')
    assert isinstance(result, str)
    
    print(f"  甲己子午：{result}")
    
    # 測試號碼生成
    number = table.get_number_from_code('甲', '子', 3, 7)
    assert isinstance(number, str)
    assert len(number) >= 4
    
    print(f"  生成號碼：{number}")
    print("✅ 密碼表測試通過")


def test_full_calculation():
    """測試完整計算"""
    print("測試完整計算...")
    
    tbss = TieBanShenShu()
    
    birth_data = TieBanBirthData(
        birth_dt=datetime(1990, 5, 15, 14, 30),
        year_gz=Ganzhi('庚', '午'),
        month_gz=Ganzhi('辛', '巳'),
        day_gz=Ganzhi('戊', '辰'),
        hour_gz=Ganzhi('己', '未'),
        gender="男",
    )
    
    result = tbss.calculate(birth_data)
    
    # 驗證結果
    assert result.ming_palace in ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
    assert result.shen_palace in ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
    assert isinstance(result.tieban_number, str)
    assert isinstance(result.verse, str)
    assert len(result.verse) > 0
    
    print(f"  命宮：{result.ming_palace}")
    print(f"  身宮：{result.shen_palace}")
    print(f"  五行局：{result.wuxing_ju}")
    print(f"  刻分：{result.ke}刻{result.fen}分")
    print(f"  神數號碼：{result.tieban_number}")
    print(f"  條文：{result.verse[:50]}...")
    
    print("✅ 完整計算測試通過")


def test_report_generation():
    """測試報告生成"""
    print("測試報告生成...")
    
    tbss = TieBanShenShu()
    
    birth_data = TieBanBirthData(
        birth_dt=datetime(1990, 5, 15, 14, 30),
        year_gz=Ganzhi('庚', '午'),
        month_gz=Ganzhi('辛', '巳'),
        day_gz=Ganzhi('戊', '辰'),
        hour_gz=Ganzhi('己', '未'),
        gender="男",
    )
    
    report = tbss.get_full_report(birth_data)
    
    assert isinstance(report, str)
    assert len(report) > 500
    assert '鐵板神數' in report
    assert '命宮' in report
    assert '條文' in report
    
    print("  報告生成成功")
    print(f"  報告長度：{len(report)} 字元")
    print("✅ 報告生成測試通過")


def run_all_tests():
    """運行所有測試"""
    print("=" * 60)
    print("鐵板神數模組測試套件")
    print("=" * 60)
    print()
    
    tests = [
        test_ganzhi_creation,
        test_ganzhi_from_year,
        test_mapping_he_luo,
        test_mapping_nayin,
        test_mapping_wuxing_ju,
        test_star_placement_an_ming,
        test_ke_fen_calculation,
        test_verse_database,
        test_secret_code_table,
        test_full_calculation,
        test_report_generation,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__} 失敗：{e}")
            import traceback
            traceback.print_exc()
            failed += 1
        print()
    
    print("=" * 60)
    print(f"測試結果：{passed} 通過，{failed} 失敗")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
