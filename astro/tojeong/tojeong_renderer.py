"""
土亭數渲染器 (Tojeong Shu Renderer)

純 SVG 渲染土亭數命盤
包含：
- 四柱顯示
- 先天數/後天數計算過程
- 格局代碼
- 129 格局斷語（三元/卞元）
"""

import streamlit as st
from typing import Dict, Any, Optional


def render_tojeong_chart(chart: Dict[str, Any], 
                         after_chart_hook: Optional[callable] = None):
    """
    渲染土亭數命盤
    
    參數：
    - chart: compute_tojeong_chart() 返回的命盤數據
    - after_chart_hook: 渲染完成後的回調函數（用於 AI 按鈕等）
    """
    birth_info = chart.get("birth_info", {})
    four_pillars = chart.get("four_pillars", {})
    calculation = chart.get("calculation", {})
    pattern = chart.get("pattern")
    yuan = chart.get("yuan", "上元")
    interpretation = chart.get("interpretation", {})
    
    # 標題
    st.markdown("### 🔮 土亭數命盤")
    
    # 出生信息
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**出生年份**: {birth_info.get('year', 'N/A')}")
        st.markdown(f"**出生月份**: {birth_info.get('month', 'N/A')}")
        st.markdown(f"**出生日期**: {birth_info.get('day', 'N/A')}")
    with col2:
        st.markdown(f"**出生時辰**: {birth_info.get('hour', 'N/A')}")
        st.markdown(f"**性別**: {'男' if birth_info.get('gender') == 'male' else '女'}")
        st.markdown(f"**三元**: {yuan}")
    
    st.divider()
    
    # 四柱干支
    st.markdown("#### 📅 四柱干支")
    gz_cols = st.columns(4)
    gz_labels = ["年柱", "月柱", "日柱", "時柱"]
    gz_keys = ["year_gz", "month_gz", "day_gz", "hour_gz"]
    
    for i, (label, key) in enumerate(zip(gz_labels, gz_keys)):
        with gz_cols[i]:
            gz = four_pillars.get(key, "")
            st.markdown(f"**{label}**")
            st.markdown(f"<div style='text-align:center; font-size:24px; padding:10px; background:linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); border-radius:8px; color:white; font-weight:bold;'>{gz}</div>", 
                       unsafe_allow_html=True)
    
    st.divider()
    
    # 計算過程
    st.markdown("#### 🔢 計算過程")
    
    shi = calculation.get("shi", [])
    fa = calculation.get("fa", [])
    products = calculation.get("products", [])
    code = calculation.get("code", "")
    
    calc_cols = st.columns(4)
    calc_labels = ["年", "月", "日", "時"]
    
    for i, label in enumerate(calc_labels):
        with calc_cols[i]:
            st.markdown(f"**{label}**")
            st.markdown(f"先天數（實）: {shi[i] if i < len(shi) else 'N/A'}")
            st.markdown(f"後天數（法）: {fa[i] if i < len(fa) else 'N/A'}")
            st.markdown(f"乘積：{products[i] if i < len(products) else 'N/A'}")
    
    st.markdown(f"**格局代碼**: `{code}`")
    
    st.divider()
    
    # 格局信息
    st.markdown("#### 📜 格局斷語")
    
    if pattern:
        # 格局名存在 "name" key 中
        pattern_name = pattern.get("name", "未知格局")
        
        st.markdown(f"##### {pattern_name}")
        
        # 三元斷語
        yuan_cols = st.columns(3)
        yuan_labels = ["上元", "中元", "下元"]
        
        for i, yuan_label in enumerate(yuan_labels):
            with yuan_cols[i]:
                yu = pattern.get(yuan_label, "")
                st.markdown(f"**{yuan_label}**")
                if yu:
                    st.info(yu)
                else:
                    st.warning("暫無斷語")
        
        # 卞元（女命）
        if birth_info.get('gender') == 'female':
            bian_yuan = pattern.get("卞元", "")
            st.markdown(f"**卞元**（女命）")
            if bian_yuan:
                st.info(bian_yuan)
            else:
                st.warning("暫無斷語")
        
        # 格局狀態
        status = pattern.get('status', 'unknown')
        if status == 'complete':
            st.success("✅ 完整格局")
        elif status == 'partial':
            st.warning("⚠️ 部分斷語")
        elif status == 'missing':
            st.error("❌ 待補完格局")
        elif status == 'approximate':
            st.info("ℹ️ 近似格局")
    else:
        st.warning("❌ 未找到對應格局")
    
    st.divider()
    
    # 說明
    with st.expander("📖 土亭數簡介"):
        st.markdown("""
        **土亭數**（土亭子數）是朝鮮時代土亭李先生所創的占數系統。
        
        **核心算法**：
        1. **先天數**：甲己子午九、乙庚丑未八、丙辛寅申七、丁壬卯酉六、戊癸辰戌五、己亥四
           - 干順支逆，除十取零 → 置上為實
        2. **後天數**：壬子一、丁巳二、甲寅三、辛酉四、戊辰戊五、癸亥六、丙午七、乙卯八、庚申九、丑未十、己百
           - 順計干支，除百十取零 → 置下為法
        3. **位位相乘**：實 × 法，位位相乘
        4. **去首尾**：去首尾兩位，得格局代碼
        5. **查格局**：查 129 格局斷語
        
        **三元**：
        - 上元：冬至、小寒、大寒
        - 中元：春分、清明、穀雨
        - 下元：其他節氣
        
        **卞元**：女命專用，參考卞元斷語
        """)
    
    # 回調鉤子
    if after_chart_hook:
        after_chart_hook()


def render_tojeong_svg(chart: Dict[str, Any]) -> str:
    """
    生成土亭數命盤的純 SVG
    
    返回 SVG 字符串
    """
    four_pillars = chart.get("four_pillars", {})
    calculation = chart.get("calculation", {})
    pattern = chart.get("pattern")
    
    # 獲取格局名
    pattern_name = "未知格局"
    if pattern:
        for key in pattern.keys():
            if key not in ['id', 'code', '上元', '中元', '下元', '卞元', 'status']:
                pattern_name = key
                break
    
    # 基礎 SVG 結構
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 800" width="600" height="800">
  <!-- 背景 -->
  <rect width="600" height="800" fill="#fafafa"/>
  
  <!-- 標題 -->
  <text x="300" y="50" text-anchor="middle" font-size="28" font-weight="bold" fill="#333">🔮 土亭數命盤</text>
  
  <!-- 四柱 -->
  <g transform="translate(50, 100)">
    <rect width="500" height="80" fill="#f0f0f0" rx="8"/>
    <text x="250" y="25" text-anchor="middle" font-size="16" font-weight="bold" fill="#333">📅 四柱干支</text>
    
    <!-- 年柱 -->
    <text x="62.5" y="55" text-anchor="middle" font-size="14" fill="#666">年柱</text>
    <text x="62.5" y="75" text-anchor="middle" font-size="24" font-weight="bold" fill="#c00">{four_pillars.get("year_gz", "")}</text>
    
    <!-- 月柱 -->
    <text x="187.5" y="55" text-anchor="middle" font-size="14" fill="#666">月柱</text>
    <text x="187.5" y="75" text-anchor="middle" font-size="24" font-weight="bold" fill="#c00">{four_pillars.get("month_gz", "")}</text>
    
    <!-- 日柱 -->
    <text x="312.5" y="55" text-anchor="middle" font-size="14" fill="#666">日柱</text>
    <text x="312.5" y="75" text-anchor="middle" font-size="24" font-weight="bold" fill="#c00">{four_pillars.get("day_gz", "")}</text>
    
    <!-- 時柱 -->
    <text x="437.5" y="55" text-anchor="middle" font-size="14" fill="#666">時柱</text>
    <text x="437.5" y="75" text-anchor="middle" font-size="24" font-weight="bold" fill="#c00">{four_pillars.get("hour_gz", "")}</text>
  </g>
  
  <!-- 計算過程 -->
  <g transform="translate(50, 220)">
    <rect width="500" height="100" fill="#f5f5f5" rx="8"/>
    <text x="250" y="25" text-anchor="middle" font-size="16" font-weight="bold" fill="#333">🔢 計算過程</text>
    
    <text x="20" y="55" font-size="12" fill="#666">先天數（實）: {calculation.get("shi", [])}</text>
    <text x="20" y="75" font-size="12" fill="#666">後天數（法）: {calculation.get("fa", [])}</text>
    <text x="20" y="95" font-size="12" fill="#666">格局代碼：{calculation.get("code", "")}</text>
  </g>
  
  <!-- 格局 -->
  <g transform="translate(50, 360)">
    <rect width="500" height="200" fill="#fff5f5" rx="8" stroke="#fcc" stroke-width="2"/>
    <text x="250" y="30" text-anchor="middle" font-size="18" font-weight="bold" fill="#c00">📜 {pattern_name}</text>
    
    <!-- 上元 -->
    <text x="20" y="60" font-size="14" font-weight="bold" fill="#333">上元：</text>
    <text x="80" y="60" font-size="13" fill="#666">{pattern.get("上元", "") if pattern else ""}</text>
    
    <!-- 中元 -->
    <text x="20" y="90" font-size="14" font-weight="bold" fill="#333">中元：</text>
    <text x="80" y="90" font-size="13" fill="#666">{pattern.get("中元", "") if pattern else ""}</text>
    
    <!-- 下元 -->
    <text x="20" y="120" font-size="14" font-weight="bold" fill="#333">下元：</text>
    <text x="80" y="120" font-size="13" fill="#666">{pattern.get("下元", "") if pattern else ""}</text>
    
    <!-- 卞元 -->
    <text x="20" y="150" font-size="14" font-weight="bold" fill="#333">卞元：</text>
    <text x="80" y="150" font-size="13" fill="#666">{pattern.get("卞元", "") if pattern else ""}</text>
    
    <!-- 狀態 -->
    <text x="250" y="185" text-anchor="middle" font-size="12" fill="#999">
        {pattern.get("status", "unknown") if pattern else "unknown"}
    </text>
  </g>
  
  <!-- 底部說明 -->
  <g transform="translate(50, 600)">
    <rect width="500" height="150" fill="#f9f9f9" rx="8"/>
    <text x="250" y="25" text-anchor="middle" font-size="14" font-weight="bold" fill="#333">📖 土亭數簡介</text>
    
    <text x="20" y="50" font-size="11" fill="#666">
        土亭數是朝鮮時代土亭李先生所創的占數系統。
    </text>
    <text x="20" y="70" font-size="11" fill="#666">
        先天數：甲己子午九、乙庚丑未八、丙辛寅申七、丁壬卯酉六、戊癸辰戌五、己亥四
    </text>
    <text x="20" y="90" font-size="11" fill="#666">
        後天數：壬子一、丁巳二、甲寅三、辛酉四、戊辰戊五、癸亥六、丙午七、乙卯八、庚申九、丑未十、己百
    </text>
    <text x="20" y="110" font-size="11" fill="#666">
        計算：先天數（除十取零）× 後天數（除百十取零）→ 去首尾 → 查 129 格局
    </text>
    <text x="20" y="130" font-size="11" fill="#666">
        三元：上元（冬至/小寒/大寒）、中元（春分/清明/穀雨）、下元（其他）
    </text>
  </g>
</svg>'''
    
    return svg
