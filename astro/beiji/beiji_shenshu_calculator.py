#!/usr/bin/env python3
"""
北極神數 (Beiji Shenshu) 起盤與查詢工具
根據教程表格邏輯實現起盤方式，連接條文_fixed.txt 進行查詢。
支援多種預測類型 (父母屬相、 大運、性格、兄弟、 再婚妻姓氏等)。
"""

import re
from collections import defaultdict

# 條文文件路徑 (假設在同一目錄或指定路徑)
VERSES_FILE = "data/beiji_tiaowen.txt"

def load_verses(file_path=VERSES_FILE):
    """載入條文到字典 {code: text}"""
    verses = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                match = re.match(r'^(\d{4})\s+(.+)', line)
                if match:
                    code = match.group(1)
                    text = match.group(2)
                    verses[code] = text
        print(f"成功載入 {len(verses)} 條北極神數條文。")
    except FileNotFoundError:
        print(f"錯誤: 找不到條文文件 {file_path}")
        print("請確保已運行之前的 fix 腳本生成 fixed 文件。")
    return verses

# 預定義部分表格邏輯 (從教程TXT提取，簡化實現)
# 1. 第一宮乾100 - 論父母屬相壽亡 (示例表格映射)
# 行: 千子~千亥 (對應出生年支或計算值)
# 列: 10,20,...80 (對應拾位數/計算值)
# 單元格內容為預測關鍵字 (實際應用中用於構造或對應條文)
PARENTS_TABLE = {
    '子': {10: '以', 20: '以', 30: '以', 40: '以', 50: '以', 60: '以', 70: '以', 80: '以'},
    '丑': {10: '十', 20: '十', 30: '出', 40: '出', 50: '出', 60: '出', 70: '八', 80: '八'},
    '寅': {10: '二', 20: '二', 30: '生', 40: '生', 50: '生', 60: '生', 70: '字', 80: '字'},
    '卯': {10: '地', 20: '地', 30: '時', 40: '時', 50: '時', 60: '時', 70: '十', 80: '時'},
    '辰': {10: '支', 20: '支', 30: '辰', 40: '辰', 50: '辰', 60: '辰', 70: '二', 80: '二'},
    '巳': {10: '論', 20: '論', 30: '論', 40: '論', 50: '論', 60: '論', 70: '地', 80: '地'},
    '午': {10: '父', 20: '母', 30: '父', 40: '父', 50: '母', 60: '父', 70: '支', 80: '支'},
    '未': {10: '親', 20: '親', 30: '死', 40: '母', 50: '死', 60: '母', 70: '論', 80: '論'},
    '申': {10: '屬', 20: '屬', 30: '母', 40: '都', 50: '父', 60: '都', 70: '富', 80: '貴'},
    '酉': {10: '相', 20: '相', 30: '在', 40: '在', 50: '在', 60: '亡', 70: '命', 80: '命'},
    '戌': {10: '信', 20: '信', 30: '信', 40: '信', 50: '信', 60: '信', 70: '信', 80: '信'},
    '亥': {10: '息', 20: '息', 30: '息', 40: '息', 50: '息', 60: '息', 70: '息', 80: '息'},
}

# 2. 坎600 - 論再婚後妻之姓氏 (簡單映射表格)
REMARRIAGE_WIFE_TABLE = {
    '子': ['郝', '陶', '史', '吳', '沈', '秦', '曹', '許'],
    '丑': ['張', '金', '程', '江', '闫', '湯', '竇', '呂'],
    '寅': ['余', '黃', '宗', '樊', '蔣', '顧', '孔', '靳'],
    '卯': ['孫', '常', '劉', '康', '藺', '毛', '麻', '蘇'],
    '辰': ['王', '仲', '魏', '楊', '關', '董', '鮑', '崔'],
    '巳': ['李', '蘆', '姚', '潘', '朱', '胡', '林', '殷'],
    '午': ['丁', '卞', '陳', '巫', '武', '瞿', '鄧', '白'],
    '未': ['孟', '馬', '徐', '賈', '高', '杜', '薛', '栗'],
    '申': ['何', '謝', '和', '馮', '田', '牛', '唐', '童'],
    '酉': ['趙', '范', '袁', '屈', '喬', '申', '苗', '郭'],
    '戌': ['周', '雷', '鄭', '羅', '紀', '陸', '魯', '安'],
    '亥': ['梁', '倪', '錢', '司', '苟', '敬', '鐘', '侯'],
}

def get_stem_branch(year):
    """簡單示例: 將年份轉為天干地支 (實際應用需精確農曆/陽曆轉換)"""
    stems = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
    branches = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
    # 簡化: 以1900為基準
    offset = (year - 1900) % 60
    stem = stems[offset % 10]
    branch = branches[offset % 12]
    return stem, branch

def calculate_parents_code(birth_year, calculated_tens=10):
    """
    示例起盤: 父母屬相壽亡 (第一宮乾100)
    輸入: birth_year (用於計算地支), calculated_tens (拾位數, 實際需根據教程公式計算, e.g. 月或日)
    返回: 4位數代碼 (示例構造)
    """
    _, branch = get_stem_branch(birth_year)
    if branch not in PARENTS_TABLE:
        branch = '子'  # 默认
    
    # 簡化: 根據表格位置構造代碼 (實際需更精確映射)
    # 假設 row_index 對應千位, column 對應其他
    row_map = {'子': '1', '丑': '2', '寅': '3', '卯': '4', '辰': '5', 
               '巳': '6', '午': '7', '未': '8', '申': '9', '酉': '1', '戌': '1', '亥': '1'}
    
    # 簡化構造 (實際應根據表格單元格或位置確定完整4位數)
    code_prefix = row_map.get(branch, '1') + '1'  # 示例
    # 進一步可根據 calculated_tens 調整
    if calculated_tens == 10:
        code = code_prefix + '11'
    else:
        code = code_prefix + str(calculated_tens)  # 簡化
    
    return code

def calculate_remarriage_wife_surname(birth_year, calculated_value=10):
    """
    示例起盤: 再婚後妻姓氏 (坎600)
    輸入: birth_year, calculated_value (拾千位數或計算值)
    返回: 姓氏 + 對應條文代碼示例
    """
    _, branch = get_stem_branch(birth_year)
    if branch not in REMARRIAGE_WIFE_TABLE:
        branch = '子'
    
    col_index = (calculated_value // 10 - 1) % 8  # 簡化映射到列
    surname = REMARRIAGE_WIFE_TABLE[branch][col_index]
    
    # 對應條文代碼示例 (坎宮 ~61xx)
    code = f"61{calculated_value:02d}"  # 簡化
    return surname, code

def lookup_verse(verses_dict, code):
    """查詢條文"""
    if code in verses_dict:
        return verses_dict[code]
    else:
        # 嘗試模糊匹配或返回提示
        similar = [c for c in verses_dict if c.startswith(code[:2])]
        if similar:
            return f"未找到精確代碼 {code}，相似代碼示例: {similar[:3]}... 請檢查起盤計算。"
        return f"未找到代碼 {code} 的條文。請確認起盤結果或手動查表。"

def main():
    print("=" * 60)
    print("北極神數 起盤與條文查詢工具")
    print("基於教程表格邏輯 + 6144條文庫")
    print("=" * 60)
    
    verses = load_verses()
    if not verses:
        return
    
    while True:
        print("\n選擇功能:")
        print("1. 直接查詢條文 (輸入4位數代碼)")
        print("2. 起盤示例 - 父母屬相壽亡 (乾宮)")
        print("3. 起盤示例 - 再婚後妻姓氏 (坎宮)")
        print("4. 顯示系統簡介與起盤說明")
        print("0. 退出")
        
        choice = input("請輸入選項: ").strip()
        
        if choice == '1':
            code = input("輸入4位數代碼 (例如 1111): ").strip()
            if len(code) == 4 and code.isdigit():
                result = lookup_verse(verses, code)
                print(f"\n【{code}】條文:\n{result}")
            else:
                print("請輸入有效的4位數字代碼。")
        
        elif choice == '2':
            try:
                year = int(input("輸入出生年份 (例如 1990): "))
                tens = int(input("輸入拾位數/計算值 (10-80, 教程中根據月日等計算): "))
                code = calculate_parents_code(year, tens)
                print(f"\n起盤結果代碼: {code}")
                result = lookup_verse(verses, code)
                print(f"對應條文:\n{result}")
                print("(注意: 完整起盤需精確計算拾位數與千未數，參考教程表格)")
            except ValueError:
                print("輸入無效，請輸入數字。")
        
        elif choice == '3':
            try:
                year = int(input("輸入出生年份 (例如 1990): "))
                val = int(input("輸入計算值 (10-80): "))
                surname, code = calculate_remarriage_wife_surname(year, val)
                print(f"\n起盤結果: 再婚妻姓氏可能為【{surname}】")
                print(f"對應條文代碼示例: {code}")
                result = lookup_verse(verses, code)
                print(f"條文內容:\n{result}")
            except ValueError:
                print("輸入無效。")
        
        elif choice == '4':
            print("""
【北極神數起盤說明】
- 本系統基於五大神數之一， 以北斗七星、奇門、64卦為基礎。
- 起盤方式: 根據查詢類型 (父母、婚姻、運勢等) 使用對應宮的表格。
  - 計算「千未數」(出生年支/特定值) 和「拾位數」(月、日、刻等)。
  - 在表格中定位行 (地支) 和列 (拾位數)，得到預測關鍵字或對應條文代碼。
- 條文庫: 6144條詳細解釋 (已修正編號)。
- 示例中使用了簡化映射；完整應用需結合出生時辰刻 (子初刻等) 和多表格綜合。
- 參考教程TXT/PDF中的各宮表格進行精確計算。
- 系統強調實用、快而準，區分相同八字不同命運 (靠精確刻)。
            """)
        
        elif choice == '0':
            print("感謝使用北極神數工具！")
            break
        else:
            print("無效選項，請重新輸入。")

if __name__ == "__main__":
    main()