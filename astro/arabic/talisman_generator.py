import streamlit as st
from pathlib import Path
import json

# 從 picatrix_data.py 引入所有已載入的資料
from .picatrix_data import (
    PICATRIX_TALISMANS,
    PICATRIX_CORRESPONDENCES,
    PICATRIX_INCENSES,
    PICATRIX_MANSIONS,
    PICATRIX_NATURAL_RECIPES,
    get_mansion_by_longitude
)

st.set_page_config(page_title="Talisman Generator", page_icon="🔮", layout="wide")
st.title("🔮 Picatrix 魔法圖像生成器")
st.markdown("**根據 Picatrix 經典製作魔法圖像（Talisman）**")

# ==================== 側邊欄 ====================
with st.sidebar:
    st.header("🔍 搜尋條件")
    intent = st.text_input("你的意圖 / 目的", placeholder="例如：求愛、求財、摧毀敵人、治療疾病、捕魚...")
    
    st.subheader("行星偏好")
    planet_filter = st.multiselect(
        "希望使用的行星（可多選）",
        options=[p["name_zh"] for p in PICATRIX_CORRESPONDENCES],
        default=[]
    )
    
    st.subheader("月宮限制")
    use_mansion = st.checkbox("考慮目前月宮", value=True)

# ==================== 主頁面 ====================
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("推薦魔法圖像")
    
    # 搜尋過濾
    filtered_talismans = []
    keyword = intent.lower().strip()
    
    for tal in PICATRIX_TALISMANS:
        purpose = tal.get("purpose", "").lower()
        title = tal.get("title_zh", "").lower() + " " + tal.get("title_en", "").lower()
        
        # 關鍵字匹配
        if keyword and (keyword in purpose or keyword in title):
            filtered_talismans.append(tal)
        # 無關鍵字時顯示全部
        elif not keyword:
            filtered_talismans.append(tal)
    
    # 行星過濾
    if planet_filter:
        filtered_talismans = [
            t for t in filtered_talismans
            if any(p in str(t.get("timing", "")) for p in planet_filter)
        ]
    
    if filtered_talismans:
        for i, tal in enumerate(filtered_talismans[:15]):  # 最多顯示15個
            with st.expander(f"**{tal['title_zh']}** ({tal['title_en']})"):
                st.write(f"**目的**：{tal.get('purpose', '—')}")
                st.write(f"**製作時機**：{tal.get('timing', '—')}")
                st.write(f"**圖像描述**：{tal.get('image_description', '—')}")
                st.write(f"**材質**：{tal.get('materials', '—')}")
                st.write(f"**製作步驟**：{tal.get('procedure', '—')}")
                
                # 對應熏香
                if "incense" in tal or "planet" in tal:
                    st.caption("💨 推薦熏香")
                    st.write(tal.get("incense", "使用對應行星熏香"))
                
                # 對應石頭
                st.caption("🪨 推薦石頭")
                st.write("請參考行星對應表")
    else:
        st.info("目前沒有找到符合的圖像，請調整搜尋條件。")

with col2:
    st.subheader("📋 製作輔助資訊")
    
    if intent:
        st.success(f"**目前意圖**：{intent}")
    
    st.markdown("### 行星對應速查")
    for p in PICATRIX_CORRESPONDENCES:
        st.write(f"**{p['name_zh']}** → {p.get('stone', '—')} / {p.get('metal', '—')}")
    
    st.markdown("### 常用熏香")
    for inc in PICATRIX_INCENSES["planets"][:7]:
        st.write(f"**{inc['name_zh']}**：{inc['primary_incense']}")
    
    # 月宮快速提示
    if use_mansion:
        st.markdown("### 🌙 目前月宮建議")
        st.info("請在主程式中傳入月亮經度以顯示精確月宮")

st.caption("資料來源：Picatrix Book I Ch.5 + Book II Ch.9–10（Greer & Warnock 譯本）\n\n⚠️ 僅供歷史、學術、研究用途")
