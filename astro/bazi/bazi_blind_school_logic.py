#!/usr/bin/env python3
"""
盲派八字命學理論邏輯代碼化

"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Set
from enum import Enum
import json

# ==================== 基礎數據 ====================

STEMS: List[str] = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
BRANCHES: List[str] = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# 五行
STEM_ELEMENT: Dict[str, str] = {
    '甲': '木', '乙': '木',
    '丙': '火', '丁': '火',
    '戊': '土', '己': '土',
    '庚': '金', '辛': '金',
    '壬': '水', '癸': '水'
}

BRANCH_ELEMENT: Dict[str, str] = {
    '寅': '木', '卯': '木',
    '巳': '火', '午': '火',
    '申': '金', '酉': '金',
    '亥': '水', '子': '水',
    '辰': '土', '戌': '土', '丑': '土', '未': '土'
}

# 陰陽
STEM_YIN_YANG: Dict[str, str] = {s: ('陽' if i % 2 == 0 else '陰') for i, s in enumerate(STEMS)}

# 地支遁藏 (人元)
HIDDEN_STEMS: Dict[str, List[str]] = {
    '子': ['癸'],
    '丑': ['己', '癸', '辛'],
    '寅': ['甲', '丙', '戊'],
    '卯': ['乙'],
    '辰': ['戊', '癸', '乙'],
    '巳': ['丙', '戊', '庚'],
    '午': ['丁', '己'],
    '未': ['己', '乙', '丁'],
    '申': ['庚', '壬', '戊'],
    '酉': ['辛'],
    '戌': ['戊', '辛', '丁'],
    '亥': ['壬', '甲']
}

# 地支六合
SIX_COMBINE: Dict[str, str] = {
    '子': '丑', '丑': '子',
    '寅': '亥', '亥': '寅',
    '卯': '戌', '戌': '卯',
    '辰': '酉', '酉': '辰',
    '巳': '申', '申': '巳',
    '午': '未', '未': '午'
}

# 地支六沖
SIX_CLASH: Dict[str, str] = {
    '子': '午', '午': '子',
    '丑': '未', '未': '丑',
    '寅': '申', '申': '寅',
    '卯': '酉', '酉': '卯',
    '辰': '戌', '戌': '辰',
    '巳': '亥', '亥': '巳'
}

# 地支相穿 (盲派特別重視，殺傷力大)
# 來自書中：子未、丑午、寅巳、卯辰、申亥、酉戌
PIERCE: Dict[str, str] = {
    '子': '未', '未': '子',
    '丑': '午', '午': '丑',
    '寅': '巳', '巳': '寅',
    '卯': '辰', '辰': '卯',
    '申': '亥', '亥': '申',
    '酉': '戌', '戌': '酉'
}

# 三刑 (寅巳申、丑未戌)
PUNISH_GROUPS: List[List[str]] = [
    ['寅', '巳', '申'],
    ['丑', '未', '戌']
]

# 相破 (盲派提及，子破卯、卯破午等)
BREAK: Dict[str, str] = {
    '子': '卯', '卯': '子',
    '卯': '午', '午': '卯',
    '午': '酉', '酉': '午',
    '酉': '子', '子': '酉'  # 部分參考，實際以書中為主
}

# 五行墓庫
TOMB: Dict[str, str] = {
    '木': '未',
    '火': '戌',
    '金': '丑',
    '水': '辰',
    '土': '辰'   # 土墓多在辰戌
}

# 長生十二宮 (簡化，陽干為主，陰干可同論)
# 甲木為例
SHENG_WANG_TABLE: Dict[str, Dict[str, str]] = {
    # stem: {branch: state}
    '甲': {'亥':'長生', '子':'沐浴', '丑':'冠帶', '寅':'臨官', '卯':'帝旺',
           '辰':'衰', '巳':'病', '午':'死', '未':'墓', '申':'絕', '酉':'胎', '戌':'養'},
    '乙': {'亥':'長生', '子':'沐浴', '丑':'冠帶', '寅':'臨官', '卯':'帝旺',
           '辰':'衰', '巳':'病', '午':'死', '未':'墓', '申':'絕', '酉':'胎', '戌':'養'},
    # 其他干可擴展，簡化版使用相同或查表
}

# 納音 (部分示例，完整60甲子)
NA_YIN: Dict[str, str] = {
    '甲子': '海中金', '乙丑': '海中金',
    '丙寅': '爐中火', '丁卯': '爐中火',
    # ... 可擴展完整表
}

# ==================== 工具函數 ====================

def get_element(item: str) -> str:
    """獲取天干或地支的五行"""
    if item in STEM_ELEMENT:
        return STEM_ELEMENT[item]
    return BRANCH_ELEMENT.get(item, '')

def get_yin_yang(stem: str) -> str:
    return STEM_YIN_YANG.get(stem, '')

def get_hidden_stems(branch: str) -> List[str]:
    return HIDDEN_STEMS.get(branch, [])

def is_same_element(a: str, b: str) -> bool:
    return get_element(a) == get_element(b)

# ==================== 作用關係引擎 ====================

def get_interactions(b1: str, b2: str) -> List[str]:
    """
    判斷兩個地支之間的所有作用關係
    盲派特別重視「穿」的破壞力
    """
    interactions = []
    if b2 == SIX_COMBINE.get(b1):
        interactions.append('六合')
    if b2 == SIX_CLASH.get(b1):
        interactions.append('六沖')
    if b2 == PIERCE.get(b1):
        interactions.append('穿')  # 盲派重點
    if b2 == BREAK.get(b1):
        interactions.append('破')
    # 三刑檢查
    for group in PUNISH_GROUPS:
        if b1 in group and b2 in group:
            interactions.append('三刑')
            break
    return interactions

def check_three_combine(branches: List[str]) -> List[str]:
    """檢查三合局 (申子辰水、寅午戌火、巳酉丑金、亥卯未木)"""
    combos = []
    b_set = set(branches)
    if {'申', '子', '辰'} <= b_set:
        combos.append('申子辰水局')
    if {'寅', '午', '戌'} <= b_set:
        combos.append('寅午戌火局')
    if {'巳', '酉', '丑'} <= b_set:
        combos.append('巳酉丑金局')
    if {'亥', '卯', '未'} <= b_set:
        combos.append('亥卯未木局')
    return combos

def check_enter_tomb(stem: str, branch: str) -> bool:
    """檢查天干是否入墓於地支"""
    stem_elem = get_element(stem)
    tomb_branch = TOMB.get(stem_elem)
    return branch == tomb_branch

def get_branch_state_for_stem(stem: str, branch: str) -> str:
    """獲取地支對天干的狀態（長生、死、墓、絕等）"""
    # 簡化版，實際應有完整12宮表
    if stem in SHENG_WANG_TABLE:
        return SHENG_WANG_TABLE[stem].get(branch, '未知')
    # 其他干簡化處理
    return '未知'

# ==================== 數據類 ====================

@dataclass
class Pillar:
    stem: str
    branch: str

    def __post_init__(self):
        if self.stem not in STEMS or self.branch not in BRANCHES:
            raise ValueError(f"Invalid pillar: {self.stem}{self.branch}")

    @property
    def element(self) -> str:
        return get_element(self.stem)

    @property
    def hidden(self) -> List[str]:
        return get_hidden_stems(self.branch)

    def get_state(self, target_stem: Optional[str] = None) -> str:
        """對某天干的狀態"""
        if target_stem is None:
            target_stem = self.stem
        return get_branch_state_for_stem(target_stem, self.branch)

    def __str__(self):
        return f"{self.stem}{self.branch}"

@dataclass
class Bazi:
    year: Pillar
    month: Pillar
    day: Pillar
    hour: Pillar

    day_master: str = field(init=False)

    def __post_init__(self):
        self.day_master = self.day.stem

    def get_pillars(self) -> List[Pillar]:
        return [self.year, self.month, self.day, self.hour]

    def get_branches(self) -> List[str]:
        return [p.branch for p in self.get_pillars()]

    def get_stems(self) -> List[str]:
        return [p.stem for p in self.get_pillars()]

    def analyze_interactions(self) -> Dict[Tuple[str, str], List[str]]:
        """分析全盤地支作用關係"""
        branches = self.get_branches()
        result = {}
        for i in range(len(branches)):
            for j in range(i + 1, len(branches)):
                inters = get_interactions(branches[i], branches[j])
                if inters:
                    result[(branches[i], branches[j])] = inters
        # 三合局
        three = check_three_combine(branches)
        if three:
            result[('全局', '三合')] = three
        return result

    def find_pierce_break(self) -> List[str]:
        """找出所有穿破（盲派重點破壞力）"""
        branches = self.get_branches()
        findings = []
        for i in range(len(branches)):
            for j in range(i + 1, len(branches)):
                if branches[j] == PIERCE.get(branches[i]):
                    findings.append(f"{branches[i]}穿{branches[j]} (強破壞)")
        return findings

    def check_tombs(self) -> List[str]:
        """檢查入墓情況"""
        findings = []
        for p in self.get_pillars():
            if check_enter_tomb(p.stem, p.branch):
                findings.append(f"{p} 天干入墓")
            # 地支本身墓庫
            if p.branch in ['辰', '戌', '丑', '未']:
                findings.append(f"{p.branch}為墓庫宮")
        return findings

    # ==================== 盲派特定斷法 ====================

    def analyze_hour_for_siblings_face_sleep(self) -> Dict[str, str]:
        """
        利用時辰斷兄弟姐妹數量、臉型、睡覺姿勢
        來自書中「利用時辰斷...」
        """
        h = self.hour.branch
        result = {}
        # 兄弟姐妹
        if h in ['子', '午', '卯', '酉']:
            result['兄弟姐妹數'] = '1個 (月令旺則2個)'
        elif h in ['寅', '申', '巳', '亥']:
            result['兄弟姐妹數'] = '3個 (月令旺則5個)'
        elif h in ['辰', '戌', '丑', '未']:
            result['兄弟姐妹數'] = '獨生 (再多差3歲以上)'
        else:
            result['兄弟姐妹數'] = '未知'

        # 臉型
        if h in ['子', '午', '卯', '酉']:
            result['臉型'] = '四方臉，尖下顴'
        elif h in ['寅', '申', '巳', '亥']:
            result['臉型'] = '臉漫長'
        else:
            result['臉型'] = '團團臉'

        # 睡姿
        if h in ['子', '午', '卯', '酉']:
            result['睡姿'] = '仰面睡'
        elif h in ['寅', '申', '巳', '亥']:
            result['睡姿'] = '側身睡'
        else:
            result['睡姿'] = '俯面睡'

        return result

    def check_parents_ke(self) -> List[str]:
        """
        少年克父母斷法 (簡化實現)
        正印為母，偏財為父
        父母星坐支臨死病墓絕 → 早年克父母
        父母星坐長生旺地，流年見合主父母死亡
        父母宮逢沖穿合克主克父母
        """
        findings = []
        dm = self.day_master
        dm_elem = get_element(dm)

        # 簡單確定父母星五行
        # 正印：生我者
        parent_elem_map = {
            '木': {'正印': '水', '偏財': '土'},
            '火': {'正印': '木', '偏財': '金'},
            '土': {'正印': '火', '偏財': '木'},
            '金': {'正印': '土', '偏財': '水'},
            '水': {'正印': '金', '偏財': '火'},
        }
        parents_info = parent_elem_map.get(dm_elem, {})

        year_branch = self.year.branch
        month_branch = self.month.branch

        # 檢查年月支狀態
        for label, branch in [('年', year_branch), ('月', month_branch)]:
            state = get_branch_state_for_stem(dm, branch)  # 簡化
            if state in ['死', '病', '墓', '絕']:
                findings.append(f"{label}支{branch}臨{state}地，父母星坐支不利，早年可能克父母")

            # 穿破檢查
            if branch in PIERCE:
                findings.append(f"{label}支{branch}有穿的關係，父母宮可能受損")

        # 入墓檢查
        if check_enter_tomb(dm, year_branch) or check_enter_tomb(dm, month_branch):
            findings.append("父母宮或年月支見墓，父母緣薄或早年有損")

        return findings if findings else ["父母宮基本穩定，需結合大限流年細斷"]

    def check_first_child_gender(self) -> str:
        """
        八字中斷頭胎男孩女孩 (簡化)
        男命：正官女，偏官男，食為男，傷官女
        女命：傷官男，食神女，殺女，官男
        以月上子孫星為主，沖穿則換相
        """
        dm = self.day_master
        dm_elem = get_element(dm)
        month_branch = self.month.branch

        # 簡化：看月支藏干或本氣是否為子孫星
        # 實際需完整十神系統，這裡示範邏輯
        hidden = get_hidden_stems(month_branch)

        # 極簡規則示例
        if dm_elem in ['木', '火']:  # 陽日干示例
            if '庚' in hidden or '辛' in hidden:  # 官殺
                return "頭胎可能為男孩 (官殺為男)"
            else:
                return "頭胎可能為女孩 (需細看傷食)"
        else:
            return "頭胎性別需結合完整十神與沖穿換相判斷"

    def get_six_qin_from_palace(self) -> Dict[str, str]:
        """
        盲派看六親以宮位為主
        年宮父母，月宮兄弟，日宮夫妻/自己，時宮子女
        """
        return {
            '年宮 (父母宮)': f"{self.year} - 父母相關",
            '月宮 (兄弟宮)': f"{self.month} - 兄弟姐妹",
            '日宮 (夫妻/命宮)': f"{self.day} - 自己與配偶",
            '時宮 (子女宮)': f"{self.hour} - 子女"
        }

# ==================== 十神系統 ====================

def calculate_ten_gods(bazi: Bazi) -> Dict[str, Dict[str, str]]:
    """完整十神計算 - 對每個柱相對於日干"""
    day_stem = bazi.day.stem
    gods = {}
    for name, pillar in zip(['year', 'month', 'day', 'hour'], bazi.all_pillars()):
        gods[name] = {
            'stem_god': get_ten_god(day_stem, pillar.stem),
            'branch_gods': [get_ten_god(day_stem, h) for h in BRANCH_HIDDEN.get(pillar.branch, [])]
        }
    return gods

# ==================== 以病取用 (核心盲派邏輯) ====================

def detect_illness(bazi: Bazi) -> List[Dict]:
    """檢測八字之病 (盲派以病取用基礎)"""
    illnesses = []
    all_stems = [p.stem for p in bazi.all_pillars()]
    all_branches = [p.branch for p in bazi.all_pillars()]
    
    # 1. 穿破檢測 (盲派最重視)
    for i, b1 in enumerate(all_branches):
        if b1 in PIERCE_MAP:
            pierced = PIERCE_MAP[b1]
            if pierced in all_branches:
                illnesses.append({
                    'type': '穿破',
                    'description': f"{b1}穿{pierced} - 盲派殺傷力最強",
                    'severity': 'high'
                })
    
    # 2. 沖墓入墓
    for b in all_branches:
        if b in CHONG_MAP.values() or any(b in TOMB_MAP.get(el, []) for el in FIVE_ELEMENTS.values()):
            illnesses.append({'type': '墓沖', 'description': f"{b}入墓或沖", 'severity': 'medium'})
    
    # 3. 簡單旺衰 (過旺過弱)
    elem_count = {'木':0, '火':0, '土':0, '金':0, '水':0}
    for s in all_stems:
        elem_count[FIVE_ELEMENTS[s]] += 1
    for e, cnt in elem_count.items():
        if cnt >= 3:
            illnesses.append({'type': '過旺', 'element': e, 'count': cnt, 'description': f"{e}過旺為病"})
        if cnt == 0:
            illnesses.append({'type': '過弱', 'element': e, 'description': f"{e}極弱為病"})
    
    return illnesses

def recommend_use_god(bazi: Bazi, illnesses: List[Dict]) -> Dict:
    """以病取用 - 盲派核心技法"""
    day_stem = bazi.day.stem
    day_elem = FIVE_ELEMENTS[day_stem]
    
    use_gods = []
    for illness in illnesses:
        if illness['type'] == '穿破':
            # 穿破多用合、印、比肩化解
            use_gods.append({'god': '正印或比肩', 'reason': '制穿破，通關或合住'})
        elif illness['type'] == '過旺':
            weak_elem = {'木':'火', '火':'土', '土':'金', '金':'水', '水':'木'}[illness['element']]
            use_gods.append({'god': f"洩旺{illness['element']}的{weak_elem}神", 'reason': '洩秀制旺'})
        elif illness['type'] == '過弱':
            use_gods.append({'god': f"生扶{illness['element']}的印或比劫", 'reason': '補弱'})
    
    # 默認用神 (以日干為主)
    default_use = {'甲乙': '水木', '丙丁': '木火', '戊己': '火土', '庚辛': '土金', '壬癸': '金水'}.get(day_stem[0]+'類', '印比')
    
    return {
        'day_stem': day_stem,
        'illnesses': illnesses,
        'recommended_use': use_gods or [{'god': default_use, 'reason': '默認調候'}],
        'summary': f"日主{day_stem}，病處：{len(illnesses)}處，用神以{use_gods[0]['god'] if use_gods else default_use}為主"
    }

# ==================== 大限計算 (盲派特色限運) ====================

def calculate_limits(bazi: Bazi) -> List[Dict]:
    """盲派大限計算 - 以日柱為基點起限 (依書中示例)"""
    day_stem = bazi.day.stem
    # 盲派常見限運模式 (簡化版，依夏仲奇風格)
    # 例如：丙限主8歲前、庚限8-16歲等，結合虛歲
    limit_patterns = {
        '甲': [{'start': 0, 'end': 8, 'name': '甲限', 'desc': '頭部/父母宮主事'}],
        '乙': [{'start': 8, 'end': 16, 'name': '乙限', 'desc': '兄弟/財帛'}],
        '丙': [{'start': 0, 'end': 8, 'name': '丙限', 'desc': '8歲前主事'}],
        '丁': [{'start': 8, 'end': 16, 'name': '丁限', 'desc': '16歲前'}],
        # 可擴展更多...
    }
    
    base_limits = limit_patterns.get(day_stem, [{'start': 0, 'end': 10, 'name': f"{day_stem}限", 'desc': '基礎限運'}])
    
    # 加入大運交替提示
    limits = []
    for lim in base_limits:
        limits.append({
            'age_range': f"{lim['start']}-{lim['end']}歲",
            'limit_name': lim['name'],
            'description': lim['desc'],
            'note': '盲派以日柱起限，重點看限干引動宮位'
        })
    return limits

# ==================== 主分析函數 ====================

def analyze_bazi_full(bazi: Bazi) -> Dict:
    """完整盲派分析：十神 + 以病取用 + 大限"""
    ten_gods = calculate_ten_gods(bazi)
    illnesses = detect_illness(bazi)
    use_info = recommend_use_god(bazi, illnesses)
    limits = calculate_limits(bazi)
    
    return {
        'bazi': bazi.to_dict(),
        'ten_gods': ten_gods,
        'illness_analysis': use_info,
        'great_limits': limits,
        'summary': f"盲派完整分析完成 - 日主 {bazi.day.stem}{bazi.day.branch}，病處 {len(illnesses)} 處，大限 {len(limits)} 段"
    }

# ==================== 輔助：漂亮輸出 ====================

def print_bazi_analysis(bazi: Bazi):
    print("=" * 60)
    print(f"八字：{bazi.year} {bazi.month} {bazi.day} {bazi.hour}")
    print(f"日主：{bazi.day_master} ({get_element(bazi.day_master)})")
    print("-" * 60)
    print("【地支作用關係】")
    inters = bazi.analyze_interactions()
    for (b1, b2), acts in inters.items():
        print(f"  {b1} vs {b2}: {', '.join(acts)}")

    print("\n【穿破檢測】(盲派重點)")
    pierces = bazi.find_pierce_break()
    print("  " + ("\n  ".join(pierces) if pierces else "無明顯穿破"))

    print("\n【入墓情況】")
    tombs = bazi.check_tombs()
    print("  " + ("\n  ".join(tombs) if tombs else "無明顯入墓"))

    print("\n【時辰斷兄弟/臉型/睡姿】")
    hour_info = bazi.analyze_hour_for_siblings_face_sleep()
    for k, v in hour_info.items():
        print(f"  {k}: {v}")

    print("\n【父母克斷法】")
    parent_findings = bazi.check_parents_ke()
    for f in parent_findings:
        print(f"  - {f}")

    print("\n【頭胎子女】")
    print(f"  {bazi.check_first_child_gender()}")

    print("\n【六親宮位】")
    for k, v in bazi.get_six_qin_from_palace().items():
        print(f"  {k}: {v}")

    print("=" * 60)

# ==================== 示例 ====================

if __name__ == "__main__":
    # 示例：使用書中某造 (如第一編例)
    # 乾，壬壬甲丁 / 辰子辰卯
    example_bazi = Bazi(
        year=Pillar('壬', '辰'),
        month=Pillar('壬', '子'),
        day=Pillar('甲', '辰'),
        hour=Pillar('丁', '卯')
    )

    print_bazi_analysis(example_bazi)

    print("\n【代碼說明】")
    print("此代碼將盲派核心理論（地支穿破合沖刑墓、時辰斷法、父母克、六親宮位等）")
    print("結構化為可執行邏輯。可繼續擴展：")
    print("1. 完整十神系統 + 以病取用")
    print("2. 大限/流年計算 (需出生日期)")
    print("3. 更多夏仲奇實例驗證函數")
    print("4. 結合NaYin交運時間")
    print("5. GUI 或 Web 介面")
