"""
astro/tieban/tieban_browser.py — 鐵板神數條文瀏覽工具

Tie Ban Shen Shu Verse Browser Tool

提供條文搜索、分類瀏覽、標籤篩選等功能，並整合完整 12000 條文資料庫。

使用方式：
    from astro.tieban.tieban_browser import render_verse_browser
    render_verse_browser()
"""

from collections.abc import Sequence
import html
from math import ceil
from typing import Any

import streamlit as st

from astro.tieban.suanpan_full_structure import SuanpanTiaowenDatabase
from astro.tieban.tieban_calculator import TiaowenDatabase, VerseDatabase

PALACE_ORDER = [
    "命宮", "兄弟宮", "夫妻宮", "子女宮", "財帛宮", "疾厄宮",
    "遷移宮", "交友宮", "官祿宮", "田宅宮", "福德宮", "父母宮",
]

PALACE_NAMES_EN = {
    "命宮": "Life",
    "兄弟宮": "Siblings",
    "夫妻宮": "Spouse",
    "子女宮": "Children",
    "財帛宮": "Wealth",
    "疾厄宮": "Health",
    "遷移宮": "Travel",
    "交友宮": "Friends",
    "官祿宮": "Career",
    "田宅宮": "Property",
    "福德宮": "Fortune",
    "父母宮": "Parents",
}

CATEGORY_TRANS = {
    "綜合": "General",
    "父母": "Parents",
    "兄弟": "Siblings",
    "夫妻": "Spouse",
    "子女": "Children",
    "財運": "Wealth",
    "事業": "Career",
    "健康": "Health",
    "災厄": "Disaster",
    "遷移": "Travel",
}


def _slice_page(items: Sequence[Any], *, page: int, page_size: int) -> list[Any]:
    """Return a single page of items with bounds clamped safely."""
    if page_size <= 0:
        raise ValueError("page_size must be positive")
    total_pages = max(1, ceil(len(items) / page_size))
    current_page = min(max(page, 1), total_pages)
    start_idx = (current_page - 1) * page_size
    end_idx = start_idx + page_size
    return list(items[start_idx:end_idx])


def _paginate_items(
    items: Sequence[Any],
    *,
    page_size: int,
    key_prefix: str,
    label: str = "頁碼",
) -> tuple[list[Any], int, int]:
    """Return the current page slice and total page count."""
    total_pages = max(1, ceil(len(items) / page_size))
    if total_pages == 1:
        return list(items), total_pages, 1

    selected_page = st.selectbox(
        label,
        options=list(range(1, total_pages + 1)),
        index=0,
        key=f"{key_prefix}_page",
    )
    page = selected_page if selected_page is not None else 1
    return _slice_page(items, page=page, page_size=page_size), total_pages, page


def _normalize_palace_verse_items(
    palace_verses: dict[str, dict[str, Any]],
    *,
    language: str = "zh",
) -> list[dict[str, Any]]:
    """Normalize palace verse data for shared renderers."""
    no_verse_text = "No verse yet" if language == "en" else "暫無條文"
    items = []
    for palace_name in PALACE_ORDER:
        palace_info = palace_verses.get(palace_name, {})
        category = palace_info.get("category", "")
        items.append(
            {
                "palace_name": palace_name,
                "name": PALACE_NAMES_EN.get(palace_name, palace_name) if language == "en" else palace_name,
                "branch": palace_info.get("branch", ""),
                "category": CATEGORY_TRANS.get(category, category) if language == "en" else category,
                "verse": palace_info.get("verse", no_verse_text),
                "number": palace_info.get("number", ""),
                "tags": palace_info.get("tags", []),
            }
        )
    return items


def render_palace_verses_paginated(
    palace_verses: dict[str, dict[str, Any]],
    *,
    language: str = "zh",
    page_size: int = 4,
    key_prefix: str = "tieban_palace_verses",
) -> None:
    """Render paginated 12-palace verse cards."""
    items = _normalize_palace_verse_items(palace_verses, language=language)

    display_items, total_pages, current_page = _paginate_items(
        items,
        page_size=page_size,
        key_prefix=key_prefix,
        label="Page" if language == "en" else "頁碼",
    )

    cards_html = ""
    for item in display_items:
        safe_name = html.escape(str(item["name"]))
        safe_branch = html.escape(str(item["branch"]))
        safe_category = html.escape(str(item["category"]))
        safe_verse = html.escape(str(item["verse"]))
        cat_badge = (
            f'<span style="font-size:10px;color:#FF6B35;margin-left:6px;">'
            f'【{safe_category}】</span>'
        ) if safe_category else ""
        cards_html += (
            '<div style="border-left:3px solid rgba(255,107,53,0.5);'
            'padding:10px 12px;margin-bottom:10px;'
            'background:rgba(255,255,255,0.03);border-radius:0 8px 8px 0;">'
            f'<div style="font-size:13px;font-weight:700;color:#FFD93D;margin-bottom:4px;">'
            f'{safe_name}'
            f'<span style="font-size:11px;color:#9090b0;font-weight:400;margin-left:4px;">({safe_branch})</span>'
            f'{cat_badge}'
            '</div>'
            f'<div style="font-size:13px;color:#c8c8e8;line-height:1.6;">{safe_verse}</div>'
            '</div>'
        )

    st.markdown(f'<div style="width:100%;">{cards_html}</div>', unsafe_allow_html=True)
    if total_pages > 1:
        if language == "en":
            st.caption(f"Page {current_page}/{total_pages} · {len(items)} verses")
        else:
            st.caption(f"第 {current_page}/{total_pages} 頁，共 {len(items)} 條")


def render_palace_verses_subtabs(
    palace_verses: dict[str, dict[str, Any]],
    *,
    language: str = "zh",
) -> None:
    """Render one sub-tab per palace for detailed verse content."""
    items = _normalize_palace_verse_items(palace_verses, language=language)
    tab_labels = [
        f'{item["name"]}{f" · {item["branch"]}" if item["branch"] else ""}'
        for item in items
    ]
    tabs = st.tabs(tab_labels)
    tags_label = "Tags" if language == "en" else "標籤"

    for tab, item in zip(tabs, items):
        with tab:
            meta_parts = []
            if item["number"]:
                meta_parts.append(
                    f'<span style="background:rgba(255,107,53,0.12);border:1px solid rgba(255,107,53,0.35);'
                    f'border-radius:8px;padding:4px 10px;font-size:12px;color:#FF9966;">#{html.escape(str(item["number"]))}</span>'
                )
            if item["category"]:
                meta_parts.append(
                    f'<span style="background:rgba(255,217,61,0.10);border:1px solid rgba(255,217,61,0.3);'
                    f'border-radius:8px;padding:4px 10px;font-size:12px;color:#FFD93D;">{html.escape(str(item["category"]))}</span>'
                )
            if item["branch"]:
                meta_parts.append(
                    f'<span style="background:rgba(107,203,119,0.10);border:1px solid rgba(107,203,119,0.25);'
                    f'border-radius:8px;padding:4px 10px;font-size:12px;color:#6BCB77;">{html.escape(str(item["branch"]))}</span>'
                )
            if meta_parts:
                st.markdown(
                    f'<div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:10px;">{"".join(meta_parts)}</div>',
                    unsafe_allow_html=True,
                )

            st.markdown(
                '<div style="background:rgba(255,255,255,0.03);border-left:4px solid #FF6B35;'
                'border-radius:0 12px 12px 0;padding:14px 18px;font-size:15px;'
                f'color:#f0d9c8;line-height:1.9;letter-spacing:0.5px;">{html.escape(str(item["verse"]))}</div>',
                unsafe_allow_html=True,
            )
            if item["tags"]:
                safe_tags = "、".join(html.escape(str(tag)) for tag in item["tags"])
                st.caption(f"{tags_label}：{safe_tags}")


def render_verse_browser():
    """
    渲染條文瀏覽工具（verses.json，6208 條，含分類標籤）
    
    在 Streamlit 中顯示條文搜索、分類瀏覽、標籤篩選界面
    """
    st.header("📜 鐵板神數條文瀏覽")
    st.caption("搜索和瀏覽鐵板神數條文資料庫")
    
    # 初始化資料庫
    db = VerseDatabase()
    
    # 側邊欄：搜索和篩選
    with st.sidebar:
        st.subheader("🔍 搜索")
        
        # 號碼搜索
        search_number = st.text_input(
            "按號碼搜索",
            placeholder="例：0001",
            help="輸入萬千百十號（4 位數字）"
        )
        
        # 關鍵字搜索
        search_keyword = st.text_input(
            "按關鍵字搜索",
            placeholder="例：父母、兄弟、夫妻",
            help="在條文中搜索關鍵字"
        )
        
        st.divider()
        
        # 分類篩選
        categories = db.get_categories()
        selected_category = st.selectbox(
            "選擇分類",
            options=["全部"] + categories,
            help="按條文分類篩選"
        )
        
        st.divider()
        
        # 標籤雲
        st.subheader("🏷️ 熱門標籤")
        all_tags = []
        for verse_data in db.verses.values():
            if 'tags' in verse_data:
                all_tags.extend(verse_data['tags'])
        
        # 統計標籤頻率
        tag_counts: dict[str, int] = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # 顯示前 20 個热门标签
        top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:20]
        
        selected_tag = st.selectbox(
            "選擇標籤",
            options=["全部"] + [tag for tag, _ in top_tags],
            help="按標籤篩選條文"
        )
    
    # 主界面：條文列表
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"共 {len(db.verses)} 條條文")
    
    with col2:
        # 導出按鈕
        st.download_button(
            label="📥 導出 JSON",
            data=str(db.verses),
            file_name="tieban_verses.json",
            mime="application/json",
        )
    
    st.divider()
    
    # 搜索和篩選邏輯
    filtered_verses = []
    
    for number, verse_data in db.verses.items():
        # 號碼搜索
        if search_number and number != search_number:
            continue
        
        # 關鍵字搜索
        if search_keyword:
            verse_text = verse_data.get('verse', '')
            if search_keyword not in verse_text:
                continue
        
        # 分類篩選
        if selected_category != "全部":
            verse_category = verse_data.get('category', '')
            if verse_category != selected_category:
                continue
        
        # 標籤篩選
        if selected_tag != "全部":
            verse_tags = verse_data.get('tags', [])
            if selected_tag not in verse_tags:
                continue
        
        filtered_verses.append({
            'number': number,
            **verse_data
        })
    
    # 顯示結果
    if not filtered_verses:
        st.info("未找到符合條件的條文")
        return
    
    st.markdown(f"找到 {len(filtered_verses)} 條條文")
    
    # 分頁顯示
    page_size = 20
    total_pages = (len(filtered_verses) - 1) // page_size + 1
    
    if total_pages > 1:
        page = st.selectbox(
            "頁碼",
            options=list(range(1, total_pages + 1)),
            index=0,
        )
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        display_verses = filtered_verses[start_idx:end_idx]
    else:
        display_verses = filtered_verses
    
    # 顯示條文
    for verse_item in display_verses:
        with st.expander(
            f"📜 {verse_item['number']}號 - {verse_item.get('category', '未知')}",
            expanded=False
        ):
            st.markdown(f"**條文**：{verse_item.get('verse', '')}")
            
            if verse_item.get('tags'):
                st.markdown(f"**標籤**：{' · '.join(verse_item['tags'])}")
            
            # 統計信息
            verse_text = verse_item.get('verse', '')
            st.caption(f"字數：{len(verse_text)} | 分類：{verse_item.get('category', '未知')}")
    
    # 統計信息
    st.divider()
    st.subheader("📊 統計信息")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("總條文數", len(db.verses))
    
    with col2:
        st.metric("分類數", len(categories))
    
    with col3:
        st.metric("標籤數", len(tag_counts))
    
    # 分類統計
    st.markdown("##### 分類統計")
    category_counts: dict[str, int] = {}
    for verse_data in db.verses.values():
        cat = verse_data.get('category', '未知')
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    category_df_data = [
        {"分類": cat, "條文數": count}
        for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
    ]
    st.dataframe(category_df_data, width="stretch", hide_index=True)
    
    # 標籤雲可視化
    st.markdown("##### 標籤雲")
    if top_tags:
        tags_html = '<div style="line-height: 2;">'
        for tag, count in top_tags:
            font_size = 12 + (count - 1) * 2  # 根據頻率調整字體大小
            tags_html += f'<span style="display: inline-block; margin: 5px; padding: 3px 8px; background: #16213e; border-radius: 15px; font-size: {font_size}px;">{tag} ({count})</span>'
        tags_html += '</div>'
        st.markdown(tags_html, unsafe_allow_html=True)


def render_tiaowen_full_browser():
    """
    渲染完整 12000 條文資料庫瀏覽工具
    
    整合坤集扣入法，支援編號搜索、全文搜索與範圍瀏覽。
    """
    st.header("📚 鐵板神數完整條文（12000 條）")
    st.caption("搜索和瀏覽完整 tiaowen_full_12000 資料庫，附坤集扣入法天干序列")
    
    db = TiaowenDatabase()
    
    tab_search, tab_range = st.tabs(["🔍 搜索", "📋 範圍瀏覽"])
    
    with tab_search:
        col_num, col_kw = st.columns(2)
        with col_num:
            search_num = st.number_input(
                "按編號查詢（1001–13000）",
                min_value=1001, max_value=13000, value=1001,
                step=1,
            )
            if st.button("查詢編號"):
                entry = db.get(int(search_num))
                if entry:
                    st.success(f"**條文 {int(search_num)}**：{entry['text']}")
                    st.caption(f"扣入天干：{'  '.join(entry.get('tiangan', []))}")
                    if entry.get('is_blank'):
                        st.warning("此條文為空白條文（尚未收錄原文）")
                else:
                    st.error(f"未找到條文 {int(search_num)}")
        
        with col_kw:
            search_kw = st.text_input(
                "全文搜索關鍵字",
                placeholder="例：殘花、鼓盆、入泮",
            )
            if search_kw:
                results = db.search(search_kw)
                st.info(f"找到 {len(results)} 條包含「{search_kw}」的條文")
                display_results, total_pages, current_page = _paginate_items(
                    results,
                    page_size=50,
                    key_prefix="tiaowen_full_search_kw",
                )
                for item in display_results:
                    with st.expander(f"條文 {item['number']}：{item['text'][:30]}…", expanded=False):
                        st.markdown(f"**全文**：{item['text']}")
                        st.caption(f"扣入天干：{'  '.join(item.get('tiangan', []))}")
                if total_pages > 1:
                    st.caption(f"第 {current_page}/{total_pages} 頁，共 {len(results)} 條")
    
    with tab_range:
        col_s, col_e = st.columns(2)
        with col_s:
            range_start = st.number_input("起始編號", min_value=1001, max_value=13000, value=1001, step=1)
        with col_e:
            range_end = st.number_input("結束編號", min_value=1001, max_value=13000, value=1050, step=1)
        
        include_blank = st.checkbox("包含空白條文", value=False)
        
        if st.button("瀏覽範圍"):
            entries = db.get_range(int(range_start), int(range_end), include_blank=include_blank)
            st.info(f"共 {len(entries)} 條")
            for item in entries:
                blank_marker = " *(空白)*" if item.get('is_blank') else ""
                st.markdown(f"**{item['number']}**{blank_marker}：{item['text']}")
                st.caption(f"扣入天干：{'  '.join(item.get('tiangan', []))}")
                st.divider()
    
    st.metric("資料庫總條文數", db.total)


def render_tiaowen_full_browser_inline():
    """
    渲染完整 12000 條文資料庫瀏覽工具（不使用巢狀 tabs）

    與 render_tiaowen_full_browser 功能相同，但以 st.radio 替換
    st.tabs，避免 Streamlit 不允許 tab 內嵌 tab 的限制。
    在 app.py 鐵板神數子頁籤中呼叫此函式。
    """
    st.caption("搜索和瀏覽完整 tiaowen_full_12000 資料庫，附坤集扣入法天干序列")

    db = TiaowenDatabase()

    sub_mode = st.radio(
        "瀏覽模式",
        ["🔍 搜索", "📋 範圍瀏覽"],
        horizontal=True,
        label_visibility="collapsed",
    )

    if sub_mode == "🔍 搜索":
        col_num, col_kw = st.columns(2)
        with col_num:
            search_num = st.number_input(
                "按編號查詢（1001–13000）",
                min_value=1001, max_value=13000, value=1001,
                step=1,
                key="tiaowen_inline_num",
            )
            if st.button("查詢編號", key="tiaowen_inline_btn_num"):
                entry = db.get(int(search_num))
                if entry:
                    st.success(f"**條文 {int(search_num)}**：{entry['text']}")
                    st.caption(f"扣入天干：{'  '.join(entry.get('tiangan', []))}")
                    if entry.get('is_blank'):
                        st.warning("此條文為空白條文（尚未收錄原文）")
                else:
                    st.error(f"未找到條文 {int(search_num)}")

        with col_kw:
            search_kw = st.text_input(
                "全文搜索關鍵字",
                placeholder="例：殘花、鼓盆、入泮",
                key="tiaowen_inline_kw",
            )
            if search_kw:
                results = db.search(search_kw)
                st.info(f"找到 {len(results)} 條包含「{search_kw}」的條文")
                display_results, total_pages, current_page = _paginate_items(
                    results,
                    page_size=50,
                    key_prefix="tiaowen_inline_search_kw",
                )
                for item in display_results:
                    with st.expander(f"條文 {item['number']}：{item['text'][:30]}…", expanded=False):
                        st.markdown(f"**全文**：{item['text']}")
                        st.caption(f"扣入天干：{'  '.join(item.get('tiangan', []))}")
                if total_pages > 1:
                    st.caption(f"第 {current_page}/{total_pages} 頁，共 {len(results)} 條")

    else:  # 範圍瀏覽
        col_s, col_e = st.columns(2)
        with col_s:
            range_start = st.number_input(
                "起始編號", min_value=1001, max_value=13000, value=1001, step=1,
                key="tiaowen_inline_rs",
            )
        with col_e:
            range_end = st.number_input(
                "結束編號", min_value=1001, max_value=13000, value=1050, step=1,
                key="tiaowen_inline_re",
            )

        include_blank = st.checkbox("包含空白條文", value=False, key="tiaowen_inline_blank")

        if st.button("瀏覽範圍", key="tiaowen_inline_btn_range"):
            entries = db.get_range(int(range_start), int(range_end), include_blank=include_blank)
            st.info(f"共 {len(entries)} 條")
            for item in entries:
                blank_marker = " *(空白)*" if item.get('is_blank') else ""
                st.markdown(f"**{item['number']}**{blank_marker}：{item['text']}")
                st.caption(f"扣入天干：{'  '.join(item.get('tiangan', []))}")
                st.divider()

    st.metric("資料庫總條文數", db.total)


def render_suanpan_tiaowen_browser_inline():
    """
    渲染算盤打數五部條文資料庫瀏覽工具（不使用巢狀 tabs）

    讓使用者依五部（水/火/木/金/土）× 性別（男命/女命/歲運）瀏覽或
    搜索 suanpan_tiaowen_full.json 中的條文。
    在 app.py 鐵板神數條文庫頁籤中呼叫此函式。
    """
    st.caption("瀏覽算盤打數五部條文資料庫（曹展碩實務版，suanpan_tiaowen_full.json）")

    db = SuanpanTiaowenDatabase()

    DEPARTMENTS = ["水", "火", "木", "金", "土"]
    GENDER_TYPES = ["男命", "女命", "歲運"]

    col_dept, col_gender = st.columns(2)
    with col_dept:
        sel_dept = st.selectbox(
            "五行部",
            options=DEPARTMENTS,
            key="sp_browser_dept",
        )
    with col_gender:
        sel_gender = st.selectbox(
            "性別類型",
            options=GENDER_TYPES,
            key="sp_browser_gender",
        )

    sub_mode = st.radio(
        "瀏覽模式",
        ["🔍 按編號查詢", "🔤 全文搜索", "📋 瀏覽全部"],
        horizontal=True,
        label_visibility="collapsed",
        key="sp_browser_mode",
    )

    if sub_mode == "🔍 按編號查詢":
        search_num = st.text_input(
            "條文編號（如 2241）",
            placeholder="輸入數字編號",
            key="sp_browser_num",
        )
        if st.button("查詢", key="sp_browser_btn_num"):
            if search_num.strip():
                entry = db.get(sel_dept, sel_gender, search_num.strip())
                if entry:
                    st.success(
                        f"**{sel_dept}部 {sel_gender} {search_num.strip()}**："
                        f"{entry.get('text', '（條文待補充）')}"
                    )
                    raw = entry.get("raw_key", "")
                    if raw:
                        st.caption(f"原始鍵：{raw}")
                else:
                    st.warning(f"在 {sel_dept}部 {sel_gender} 中找不到編號 {search_num.strip()}")

    elif sub_mode == "🔤 全文搜索":
        search_kw = st.text_input(
            "搜索關鍵字",
            placeholder="例：舟、波、洞庭",
            key="sp_browser_kw",
        )
        if search_kw.strip():
            all_entries = db.get_all(sel_dept, sel_gender)
            results = [
                (num, entry)
                for num, entry in all_entries.items()
                if search_kw.strip() in entry.get("text", "")
            ]
            st.info(f"在 {sel_dept}部 {sel_gender} 中找到 {len(results)} 條包含「{search_kw.strip()}」的條文")
            display_results, total_pages, current_page = _paginate_items(
                results,
                page_size=50,
                key_prefix="sp_browser_search_kw",
            )
            for num, entry in display_results:
                with st.expander(f"條文 {num}：{entry.get('text', '')[:30]}…", expanded=False):
                    st.markdown(f"**全文**：{entry.get('text', '')}")
                    raw = entry.get("raw_key", "")
                    if raw:
                        st.caption(f"原始鍵：{raw}")
            if total_pages > 1:
                st.caption(f"第 {current_page}/{total_pages} 頁，共 {len(results)} 條")

    else:  # 瀏覽全部
        all_entries = db.get_all(sel_dept, sel_gender)
        st.info(f"{sel_dept}部 {sel_gender}：共 {len(all_entries)} 條條文")
        if all_entries:
            page_size = 30
            sorted_keys = sorted(all_entries.keys())
            total_pages = max(1, (len(sorted_keys) - 1) // page_size + 1)
            page = st.selectbox(
                "頁碼",
                options=list(range(1, total_pages + 1)),
                index=0,
                key="sp_browser_page",
            )
            start_idx = (page - 1) * page_size
            page_keys = sorted_keys[start_idx:start_idx + page_size]
            _cards = ""
            for num in page_keys:
                entry = all_entries[num]
                text = entry.get("text", "")
                raw = entry.get("raw_key", "")
                raw_badge = (
                    f'<span style="font-size:10px;color:#9090b0;margin-left:6px;">({raw})</span>'
                    if raw else ""
                )
                _cards += (
                    f'<div style="border-left:3px solid rgba(107,203,119,0.5);'
                    f'padding:8px 12px;margin-bottom:8px;'
                    f'background:rgba(255,255,255,0.03);border-radius:0 8px 8px 0;">'
                    f'<div style="font-size:12px;font-weight:700;color:#6BCB77;margin-bottom:2px;">'
                    f'{num}{raw_badge}</div>'
                    f'<div style="font-size:13px;color:#c8c8e8;line-height:1.6;">{text}</div>'
                    f'</div>'
                )
            st.markdown(f'<div style="width:100%;">{_cards}</div>', unsafe_allow_html=True)

    # 統計資訊
    st.divider()
    stats = db.stats()
    dept_stats = stats.get(sel_dept, {})
    total_dept = sum(dept_stats.values())
    st.caption(
        f"{sel_dept}部總計：{total_dept} 條"
        f"（男命 {dept_stats.get('男命', 0)} ／ "
        f"女命 {dept_stats.get('女命', 0)} ／ "
        f"歲運 {dept_stats.get('歲運', 0)}）"
        f"　　資料庫合計：{db.total} 條"
    )


def render_verse_comparison():
    """
    渲染條文對比工具
    
    允許用戶對比多個條文
    """
    st.header("📊 鐵板神數條文對比")
    st.caption("對比多個條文的異同")
    
    db = VerseDatabase()
    
    # 輸入條文號碼
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        num1 = st.text_input("條文 1", value="0001", key="num1")
    with col2:
        num2 = st.text_input("條文 2", value="0002", key="num2")
    with col3:
        num3 = st.text_input("條文 3", value="", key="num3")
    with col4:
        num4 = st.text_input("條文 4", value="", key="num4")
    
    numbers = [num1, num2, num3, num4]
    numbers = [n for n in numbers if n]  # 過濾空值
    
    if not numbers:
        st.info("請至少輸入一個條文號碼")
        return
    
    # 獲取條文
    verses = []
    for num in numbers:
        verse_data = db.lookup(num)
        verses.append({
            'number': num,
            **verse_data
        })
    
    # 顯示對比
    st.divider()
    
    for i, verse_item in enumerate(verses):
        st.markdown(f"##### {verse_item['number']}號")
        st.markdown(f"**條文**：{verse_item.get('verse', '')}")
        
        if verse_item.get('category'):
            st.markdown(f"**分類**：{verse_item['category']}")
        
        if verse_item.get('tags'):
            st.markdown(f"**標籤**：{' · '.join(verse_item['tags'])}")
        
        if i < len(verses) - 1:
            st.divider()
    
    # 共同標籤分析
    st.divider()
    st.subheader("🔍 共同標籤分析")
    
    all_tags_list = [set(verse.get('tags', [])) for verse in verses if verse.get('tags')]
    
    if len(all_tags_list) >= 2:
        common_tags = set.intersection(*all_tags_list)
        if common_tags:
            st.success(f"共同標籤：{', '.join(common_tags)}")
        else:
            st.info("沒有共同標籤")
    
    # 標籤並集
    all_tags_union = set.union(*all_tags_list) if all_tags_list else set()
    st.markdown(f"**所有標籤**：{', '.join(sorted(all_tags_union))}")


def render_verse_statistics():
    """
    渲染條文統計工具
    """
    st.header("📈 鐵板神數條文統計")
    st.caption("分析條文資料庫的統計信息")
    
    db = VerseDatabase()
    
    # 基本統計
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("總條文數", len(db.verses))
    
    with col2:
        st.metric("分類數", len(db.get_categories()))
    
    # 計算標籤總數
    all_tags = []
    for verse_data in db.verses.values():
        if 'tags' in verse_data:
            all_tags.extend(verse_data['tags'])
    unique_tags = len(set(all_tags))
    
    with col3:
        st.metric("唯一標籤數", unique_tags)
    
    with col4:
        avg_tags = len(all_tags) / len(db.verses) if db.verses else 0
        st.metric("平均每條標籤數", f"{avg_tags:.2f}")
    
    st.divider()
    
    # 分類分布
    st.subheader("📊 分類分布")
    
    category_counts: dict[str, int] = {}
    for verse_data in db.verses.values():
        cat = verse_data.get('category', '未知')
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    import pandas as pd
    
    category_df = pd.DataFrame([
        {"分類": cat, "條文數": count}
        for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
    ])
    
    st.bar_chart(category_df.set_index("分類"))
    
    # 標籤頻率
    st.subheader("🏷️ 標籤頻率 Top 20")
    
    tag_counts: dict[str, int] = {}
    for tag in all_tags:
        tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:20]
    
    tag_df = pd.DataFrame([
        {"標籤": tag, "頻率": count}
        for tag, count in top_tags
    ])
    
    st.bar_chart(tag_df.set_index("標籤"))
    
    # 詳細數據表
    st.divider()
    st.subheader("📋 詳細數據")
    
    with st.expander("查看所有條文統計"):
        all_data = []
        for number, verse_data in db.verses.items():
            all_data.append({
                "號碼": number,
                "分類": verse_data.get('category', '未知'),
                "標籤數": len(verse_data.get('tags', [])),
                "字數": len(verse_data.get('verse', '')),
            })
        
        st.dataframe(all_data, width="stretch")


def main():
    """
    主函數：條文瀏覽工具入口
    """
    st.set_page_config(
        page_title="鐵板神數條文瀏覽",
        page_icon="📜",
        layout="wide",
    )
    
    st.title("📜 鐵板神數條文瀏覽工具")
    
    # 導航
    page = st.selectbox(
        "選擇頁面",
        ["條文瀏覽", "完整 12000 條文", "條文對比", "統計分析"],
    )
    
    if page == "條文瀏覽":
        render_verse_browser()
    elif page == "完整 12000 條文":
        render_tiaowen_full_browser()
    elif page == "條文對比":
        render_verse_comparison()
    elif page == "統計分析":
        render_verse_statistics()


if __name__ == "__main__":
    main()
