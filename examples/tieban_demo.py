#!/usr/bin/env python3
"""
examples/tieban_demo.py — 鐵板神數使用示例

Tie Ban Shen Shu Demo Script

展示如何使用鐵板神數模組進行完整推算
"""

import sys
import os
from datetime import datetime

# 添加專案根目錄到路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from astro.tieban import TieBanShenShu, TieBanBirthData
from astro.tieban.tieban_calculator import Ganzhi


def example_basic_usage():
    """基本使用示例"""
    print("=" * 70)
    print("鐵板神數基本使用示例")
    print("=" * 70)
    print()
    
    # 創建實例
    tbss = TieBanShenShu()
    
    # 準備出生資料
    birth_data = TieBanBirthData(
        birth_dt=datetime(1990, 5, 15, 14, 30),
        year_gz=Ganzhi('庚', '午'),
        month_gz=Ganzhi('辛', '巳'),
        day_gz=Ganzhi('戊', '辰'),
        hour_gz=Ganzhi('己', '未'),
        gender="男",
    )
    
    # 計算
    result = tbss.calculate(birth_data)
    
    # 顯示結果
    print(f"出生時間：{birth_data.birth_dt}")
    print(f"八字：{birth_data.year_gz} {birth_data.month_gz} {birth_data.day_gz} {birth_data.hour_gz}")
    print()
    print(f"命宮：{result.ming_palace}")
    print(f"身宮：{result.shen_palace}")
    print(f"五行局：{result.wuxing_ju}")
    print()
    print(f"考刻分：{result.ke}刻{result.fen}分")
    print(f"河洛數：{result.he_luo_number}")
    print()
    print(f"神數號碼：{result.tieban_number}")
    print(f"密碼：{result.secret_code}")
    print()
    print(f"條文：{result.verse}")
    print()
    
    if isinstance(result.verse_data, dict):
        print(f"分類：{result.verse_data.get('category', '未知')}")
        if result.verse_data.get('tags'):
            print(f"標籤：{' · '.join(result.verse_data['tags'])}")
    
    print()


def example_full_report():
    """完整報告示例"""
    print("=" * 70)
    print("鐵板神數完整報告示例")
    print("=" * 70)
    print()
    
    tbss = TieBanShenShu()
    
    birth_data = TieBanBirthData(
        birth_dt=datetime(1985, 8, 20, 9, 15),
        year_gz=Ganzhi('乙', '丑'),
        month_gz=Ganzhi('甲', '申'),
        day_gz=Ganzhi('壬', '寅'),
        hour_gz=Ganzhi('乙', '巳'),
        gender="女",
    )
    
    report = tbss.get_full_report(birth_data)
    print(report)


def example_verse_search():
    """條文搜索示例"""
    print("=" * 70)
    print("鐵板神數條文搜索示例")
    print("=" * 70)
    print()
    
    from astro.tieban.tieban_calculator import VerseDatabase
    
    db = VerseDatabase()
    
    # 示例 1：按號碼查詢
    print("【按號碼查詢】")
    verse = db.lookup('0001')
    print(f"0001 號：{verse.get('verse', '')}")
    print(f"分類：{verse.get('category', '未知')}")
    print(f"標籤：{verse.get('tags', [])}")
    print()
    
    # 示例 2：按標籤搜索
    print("【按標籤搜索：父母雙全】")
    results = db.search_by_tag('父母雙全')
    for result in results[:5]:  # 顯示前 5 個
        print(f"{result['number']}號：{result['verse'][:50]}...")
    print(f"共找到 {len(results)} 條")
    print()
    
    # 示例 3：獲取所有分類
    print("【所有分類】")
    categories = db.get_categories()
    for cat in categories:
        print(f"  - {cat}")
    print()


def example_different_birth_times():
    """不同出生時辰示例"""
    print("=" * 70)
    print("鐵板神數不同出生時辰對比示例")
    print("=" * 70)
    print()
    
    tbss = TieBanShenShu()
    
    # 同一日期，不同時辰
    test_cases = [
        (datetime(1990, 5, 15, 1, 30), "丑時"),
        (datetime(1990, 5, 15, 5, 30), "卯時"),
        (datetime(1990, 5, 15, 9, 30), "巳時"),
        (datetime(1990, 5, 15, 13, 30), "未時"),
        (datetime(1990, 5, 15, 17, 30), "酉時"),
        (datetime(1990, 5, 15, 21, 30), "亥時"),
    ]
    
    print(f"日期：1990 年 5 月 15 日")
    print(f"年柱：庚午 月柱：辛巳 日柱：戊辰")
    print()
    print(f"{'時辰':<8} {'命宮':<6} {'身宮':<6} {'刻分':<10} {'神數號碼':<10}")
    print("-" * 50)
    
    for birth_dt, shi_name in test_cases:
        birth_data = TieBanBirthData(
            birth_dt=birth_dt,
            year_gz=Ganzhi('庚', '午'),
            month_gz=Ganzhi('辛', '巳'),
            day_gz=Ganzhi('戊', '辰'),
            hour_gz=Ganzhi.from_index(0, birth_dt.hour // 2),  # 簡化計算
            gender="男",
        )
        
        result = tbss.calculate(birth_data)
        
        print(f"{shi_name:<8} {result.ming_palace:<6} {result.shen_palace:<6} "
              f"{result.ke}刻{result.fen}分  {result.tieban_number:<10}")
    
    print()


def example_verse_categories():
    """條文分類統計示例"""
    print("=" * 70)
    print("鐵板神數條文分類統計示例")
    print("=" * 70)
    print()
    
    from astro.tieban.tieban_calculator import VerseDatabase
    
    db = VerseDatabase()
    
    # 統計各分類條文數
    category_counts = {}
    for verse_data in db.verses.values():
        cat = verse_data.get('category', '未知')
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    print(f"總條文數：{len(db.verses)}")
    print(f"分類數：{len(category_counts)}")
    print()
    print(f"{'分類':<10} {'條文數':>8} {'佔比':>10}")
    print("-" * 30)
    
    for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = count / len(db.verses) * 100
        print(f"{cat:<10} {count:>8} {percentage:>9.1f}%")
    
    print()
    
    # 統計標籤
    all_tags = []
    for verse_data in db.verses.values():
        if 'tags' in verse_data:
            all_tags.extend(verse_data['tags'])
    
    tag_counts = {}
    for tag in all_tags:
        tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    print("熱門標籤 Top 10：")
    for tag, count in top_tags:
        print(f"  {tag}: {count}次")
    
    print()


def example_svg_rendering():
    """SVG 渲染示例"""
    print("=" * 70)
    print("鐵板神數 SVG 渲染示例")
    print("=" * 70)
    print()
    
    from astro.tieban import render_tieban_chart_svg
    
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
    
    # 渲染 SVG
    svg = render_tieban_chart_svg(result, language='zh')
    
    print(f"SVG 長度：{len(svg)} 字元")
    print(f"命宮：{result.ming_palace}, 身宮：{result.shen_palace}")
    print(f"神數號碼：{result.tieban_number}")
    print(f"條文：{result.verse[:50]}...")
    print()
    print("✅ SVG 渲染成功，可在 Streamlit 中使用 st.components.v1.html(svg, height=650) 顯示")
    print()


def main():
    """運行所有示例"""
    print()
    print("╔" + "═" * 69 + "╗")
    print("║" + " " * 20 + "鐵板神數模組使用示例" + " " * 24 + "║")
    print("╚" + "═" * 69 + "╝")
    print()
    
    examples = [
        ("基本使用", example_basic_usage),
        ("完整報告", example_full_report),
        ("條文搜索", example_verse_search),
        ("時辰對比", example_different_birth_times),
        ("分類統計", example_verse_categories),
        ("SVG 渲染", example_svg_rendering),
    ]
    
    for name, func in examples:
        try:
            func()
        except Exception as e:
            print(f"❌ {name} 示例失敗：{e}")
            import traceback
            traceback.print_exc()
            print()
    
    print("=" * 70)
    print("所有示例運行完成")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
