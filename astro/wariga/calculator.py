"""
巴厘傳統 Wariga 計算模組 (Balinese Wariga Calendar Calculator)

使用傳統 Wuku (210天週期) + Wewaran (Eka~Dasa Wara) 的 Neptu/Urip 數值系統
進行巴厘傳統曆法計算。核心算法完全依照古典 Lontar Wariga / Dasar Wariga 規則，
不使用現代天文簡化公式或近似值。

Wewaran 計算階層規則：Wewaran alah dening Wuku
→ 總 Neptu 相加後再對各 Wara 週期取模

pyswisseph 僅用於：
- Gregorian → Julian Day 轉換
- 太陽/月亮黃經（用於 Sasih 月份近似驗證和季節參考）
- Orion (Waluku) 升落參考（用於季節校驗）

古法依據：Lontar Wariga / Dasar Wariga
"""

import math
from dataclasses import dataclass, field
from datetime import date

import swisseph as swe

from .constants import (
    EPOCH_YEAR, EPOCH_MONTH, EPOCH_DAY,
    WUKU_TABLE,
    EKA_WARA, DWI_WARA, TRI_WARA, CATUR_WARA,
    PANCA_WARA, SAD_WARA, SAPTA_WARA,
    ASTA_WARA, SANGA_WARA, DASA_WARA,
    INGKEL, WATEK_ALIT, WATEK_MADYA, PAWATEKAN,
    LINTANG,
    SASIH_NAMES,
    SEASON_LAHRU_RANGE, SEASON_RENGRENG_RANGE,
    PANCASUDA,
    PAWUKON_CYCLE,
    PANCA_DAUH, ASTA_DAUH,
    PENANGGAL_NAMES, PANGLONG_NAMES,
    WUKU_ATTRIBUTES, ALA_AYUNING_DEWASA,
)


# ============================================================
# 資料類定義 (Data Classes)
# ============================================================

@dataclass
class DauhInfo:
    """時辰（Dauh）資訊"""
    dauh_type: str       # 時辰系統名稱 (Panca Dauh / Asta Dauh)
    name: str            # 時辰名稱
    deity: str           # 主宰神明
    direction: str       # 方位
    quality: str         # 吉凶


@dataclass
class PenanggalInfo:
    """月相日（Penanggal/Panglong）資訊"""
    is_penanggal: bool   # True=月盈期(Penanggal), False=月虧期(Panglong)
    day_number: int      # 月相日數 (1-15)
    name: str            # 傳統名稱
    neptu: int           # Neptu/Urip 值
    moon_phase_deg: float  # 月相角度 (0-360)
    special: str = ""    # 特殊聖日標記 (Purnama / Tilem / 空白)


@dataclass
class WaraInfo:
    """單一 Wara（星期類別）的資訊"""
    wara_type: str       # Wara 類型名稱 (如 "Sapta Wara")
    name: str            # 該日的 Wara 名稱 (如 "Redite")
    neptu: int           # 該 Wara 的 Neptu/Urip 值


@dataclass
class WukuInfo:
    """Wuku（週）的資訊"""
    index: int           # Wuku 索引 (0-29)
    name: str            # Wuku 名稱
    neptu: int           # Wuku 的 Neptu 值


@dataclass
class DewasaInfo:
    """吉凶判斷資訊"""
    is_auspicious: bool              # 總體是否為吉日
    auspicious_labels: list          # 吉日標籤列表
    inauspicious_labels: list        # 凶日標籤列表
    neptu_sum: int                   # Panca Wara + Sapta Wara Neptu 總和
    pancasuda: str                   # Pancasuda 名稱
    pancasuda_meaning: str           # Pancasuda 含義
    notes: list = field(default_factory=list)  # 額外說明


@dataclass
class SasihInfo:
    """Sasih（月）與季節資訊"""
    sasih_index: int     # Sasih 索引 (0-11)
    sasih_name: str      # Sasih 名稱
    season: str          # 季節名稱 (Lahru / Rengreng)
    season_cn: str       # 季節中文 (乾季 / 雨季)
    ayana: str           # Uttarayana / Dakshinayana


@dataclass
class WarigaResult:
    """Wariga 計算完整結果"""
    year: int
    month: int
    day: int
    hour: int
    minute: int
    latitude: float
    longitude: float
    # Pawukon 資訊
    day_in_pawukon: int         # 在 210 天週期中的第幾天 (0-209)
    wuku: WukuInfo              # Wuku 資訊
    # 所有 Wara
    eka_wara: WaraInfo
    dwi_wara: WaraInfo
    tri_wara: WaraInfo
    catur_wara: WaraInfo
    panca_wara: WaraInfo
    sad_wara: WaraInfo
    sapta_wara: WaraInfo
    asta_wara: WaraInfo
    sanga_wara: WaraInfo
    dasa_wara: WaraInfo
    # 分類
    ingkel: str                 # Ingkel 動物分類
    watek_alit: str             # Watek Alit 分類
    watek_madya: str            # Watek Madya 分類
    lintang: str                # Lintang 星宿
    # 吉凶
    dewasa: DewasaInfo          # 吉凶判斷
    # 月份與季節
    sasih: SasihInfo            # Sasih 月份與季節
    # 時辰資訊（Panca Dauh / Asta Dauh）
    panca_dauh: DauhInfo        # Panca Dauh 時辰
    asta_dauh: DauhInfo         # Asta Dauh 時辰
    # 月相日（Penanggal / Panglong）
    penanggal: PenanggalInfo    # 月相日資訊
    # 天文參考（使用 pyswisseph 計算，僅供參考）
    sun_longitude: float        # 太陽黃經
    moon_longitude: float       # 月亮黃經
    julian_day: float           # 儒略日


# ============================================================
# 核心計算類 (Core Calculator)
# ============================================================

class WarigaCalculator:
    """
    巴厘傳統 Wariga 計算器

    根據傳統 Lontar Wariga / Dasar Wariga 的古法規則，
    從格里高利日期計算完整的 Wariga 資訊。

    核心算法：
    1. 計算目標日期與基準日 (epoch) 的天數差
    2. 天數差 mod 210 → 得到 Pawukon 日序
    3. Pawukon 日序 → Wuku 名稱 (日序 // 7)
    4. Pawukon 日序 → 各 Wara (各自的取模規則)
    5. Neptu 累加 → 吉凶判斷

    古法依據：Lontar Wariga / Dasar Wariga
    """

    def __init__(self, year, month, day, hour=0, minute=0, lat=None, lon=None):
        """
        初始化 Wariga 計算器

        參數：
            year   (int): 格里高利年份
            month  (int): 月份 (1-12)
            day    (int): 日 (1-31)
            hour   (int): 時 (0-23)，預設為 0
            minute (int): 分 (0-59)，預設為 0
            lat  (float): 緯度（可選，用於天文參考計算）
            lon  (float): 經度（可選，用於天文參考計算）
        """
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        # 巴厘島預設座標 (Ubud, Bali)
        self.lat = lat if lat is not None else -8.5069
        self.lon = lon if lon is not None else 115.2625

    # --------------------------------------------------------
    # 公開介面
    # --------------------------------------------------------

    def compute(self) -> dict:
        """
        執行完整的 Wariga 計算，回傳完整資訊字典

        回傳：
            dict: 包含所有 Wariga 資訊的字典，
                  等同於 WarigaResult 的所有欄位
        """
        result = self._compute_all()
        return self._result_to_dict(result)

    def compute_result(self) -> WarigaResult:
        """
        執行完整的 Wariga 計算，回傳 WarigaResult 資料類

        回傳：
            WarigaResult: 完整 Wariga 計算結果
        """
        return self._compute_all()

    # --------------------------------------------------------
    # 內部計算方法
    # --------------------------------------------------------

    def _compute_all(self) -> WarigaResult:
        """執行所有計算，回傳 WarigaResult"""
        # 1) 計算 Julian Day 與天文參考數據
        jd, sun_lon, moon_lon = self._compute_astro_reference()

        # 2) 計算 Pawukon 日序 (0-209)
        day_in_pawukon = self._compute_pawukon_day()

        # 3) 計算 Wuku
        wuku = self._compute_wuku(day_in_pawukon)

        # 4) 計算所有 Wara
        eka = self._compute_eka_wara(day_in_pawukon)
        dwi = self._compute_dwi_wara(day_in_pawukon)
        tri = self._compute_tri_wara(day_in_pawukon)
        catur = self._compute_catur_wara(day_in_pawukon)
        panca = self._compute_panca_wara(day_in_pawukon)
        sad = self._compute_sad_wara(day_in_pawukon)
        sapta = self._compute_sapta_wara(day_in_pawukon)
        asta = self._compute_asta_wara(day_in_pawukon)
        sanga = self._compute_sanga_wara(day_in_pawukon)
        dasa = self._compute_dasa_wara(panca, sapta)

        # 5) 計算分類
        ingkel = self._compute_ingkel(wuku.index)
        watek_alit, watek_madya = self._compute_watek(wuku.index)
        lintang = self._compute_lintang(day_in_pawukon)

        # 6) 計算吉凶 (Dewasa)
        dewasa = self._compute_dewasa(
            panca, sapta, tri, wuku, day_in_pawukon
        )

        # 7) 計算 Sasih 與季節
        sasih = self._compute_sasih(sun_lon, moon_lon)

        # 8) 計算時辰 (Panca Dauh / Asta Dauh)
        panca_dauh = self._compute_panca_dauh(self.hour)
        asta_dauh = self._compute_asta_dauh(self.hour)

        # 9) 計算月相日 (Penanggal / Panglong)
        penanggal = self._compute_penanggal(sun_lon, moon_lon)

        return WarigaResult(
            year=self.year,
            month=self.month,
            day=self.day,
            hour=self.hour,
            minute=self.minute,
            latitude=self.lat,
            longitude=self.lon,
            day_in_pawukon=day_in_pawukon,
            wuku=wuku,
            eka_wara=eka,
            dwi_wara=dwi,
            tri_wara=tri,
            catur_wara=catur,
            panca_wara=panca,
            sad_wara=sad,
            sapta_wara=sapta,
            asta_wara=asta,
            sanga_wara=sanga,
            dasa_wara=dasa,
            ingkel=ingkel,
            watek_alit=watek_alit,
            watek_madya=watek_madya,
            lintang=lintang,
            dewasa=dewasa,
            sasih=sasih,
            panca_dauh=panca_dauh,
            asta_dauh=asta_dauh,
            penanggal=penanggal,
            sun_longitude=sun_lon,
            moon_longitude=moon_lon,
            julian_day=jd,
        )

    def _compute_astro_reference(self):
        """
        使用 pyswisseph 計算天文參考數據

        回傳：
            tuple: (julian_day, sun_longitude, moon_longitude)
        """
        # 計算儒略日（使用 UTC 近似，巴厘時區 WITA = UTC+8）
        decimal_hour = self.hour + self.minute / 60.0 - 8.0
        jd = swe.julday(self.year, self.month, self.day, decimal_hour)

        # 太陽黃經、月亮黃經
        sun_lon = self._extract_longitude(jd, swe.SUN)
        moon_lon = self._extract_longitude(jd, swe.MOON)

        return jd, sun_lon, moon_lon

    @staticmethod
    def _extract_longitude(jd: float, planet_id: int) -> float:
        """
        從 pyswisseph 計算結果中提取天體黃經

        參數：
            jd        (float): 儒略日
            planet_id (int):   pyswisseph 天體 ID

        回傳：
            float: 黃經度數 (0-360)
        """
        result = swe.calc_ut(jd, planet_id)
        return result[0][0] if isinstance(result[0], (list, tuple)) else result[0]

    def _compute_pawukon_day(self) -> int:
        """
        計算目標日期在 Pawukon 210 天週期中的位置

        算法：
        1. 計算目標日期與基準日 (epoch: 1969-12-31) 的天數差
        2. 天數差 mod 210 = Pawukon 日序 (0-209)

        古法依據：Lontar Wariga — Pawukon 日序計算法

        回傳：
            int: Pawukon 日序 (0-209)
        """
        target = date(self.year, self.month, self.day)
        epoch = date(EPOCH_YEAR, EPOCH_MONTH, EPOCH_DAY)
        delta_days = (target - epoch).days
        return delta_days % PAWUKON_CYCLE

    def _compute_wuku(self, day_in_pawukon: int) -> WukuInfo:
        """
        計算 Wuku（週）名稱與 Neptu

        算法：Wuku 索引 = Pawukon 日序 // 7

        古法依據：Lontar Wariga — 30 Wuku 表

        回傳：
            WukuInfo: 包含 Wuku 索引、名稱、Neptu
        """
        wuku_idx = day_in_pawukon // 7
        name, neptu = WUKU_TABLE[wuku_idx]
        return WukuInfo(index=wuku_idx, name=name, neptu=neptu)

    def _compute_eka_wara(self, day_in_pawukon: int) -> WaraInfo:
        """
        計算 Eka Wara (1天週期)

        古法規則：Eka Wara 由 Panca Wara Urip + Sapta Wara Urip 總和的奇偶決定
        但傳統上 Eka Wara 只有 "Luang" 一值，所有日皆為 Luang。

        古法依據：Lontar Wariga — Eka Wara

        回傳：
            WaraInfo: Eka Wara 資訊
        """
        name, neptu = EKA_WARA[0]
        return WaraInfo(wara_type="Eka Wara", name=name, neptu=neptu)

    def _compute_dwi_wara(self, day_in_pawukon: int) -> WaraInfo:
        """
        計算 Dwi Wara (2天週期)

        古法規則：由 Panca Wara Urip + Sapta Wara Urip 總和奇偶決定
        偶數 → Menga(0)，奇數 → Pepet(5)

        古法依據：Lontar Wariga — Dwi Wara

        回傳：
            WaraInfo: Dwi Wara 資訊
        """
        # 先取得 Panca Wara 和 Sapta Wara 的 Urip
        panca_idx = day_in_pawukon % 5
        sapta_idx = day_in_pawukon % 7
        panca_neptu = PANCA_WARA[panca_idx][1]
        sapta_neptu = SAPTA_WARA[sapta_idx][1]
        total = panca_neptu + sapta_neptu
        # 偶數 → Menga，奇數 → Pepet
        dwi_idx = total % 2
        name, neptu = DWI_WARA[dwi_idx]
        return WaraInfo(wara_type="Dwi Wara", name=name, neptu=neptu)

    def _compute_tri_wara(self, day_in_pawukon: int) -> WaraInfo:
        """
        計算 Tri Wara (3天週期)

        算法：day_in_pawukon mod 3

        古法依據：Lontar Wariga — Tri Wara

        回傳：
            WaraInfo: Tri Wara 資訊
        """
        idx = day_in_pawukon % 3
        name, neptu = TRI_WARA[idx]
        return WaraInfo(wara_type="Tri Wara", name=name, neptu=neptu)

    def _compute_catur_wara(self, day_in_pawukon: int) -> WaraInfo:
        """
        計算 Catur Wara (4天週期)

        古法規則：非簡單 day % 4。
        在 Pawukon 週期中，Catur Wara 在特定日（第71、72天）
        會使用 Jaya 和 Menala 的特殊重複規則。

        修正算法：
        - 如果 day_in_pawukon < 71: idx = day_in_pawukon % 4
        - 如果 day_in_pawukon == 71 或 72: 使用固定值
        - 如果 day_in_pawukon > 72: idx = (day_in_pawukon - 2) % 4

        古法依據：Lontar Wariga — Catur Wara 排序法

        回傳：
            WaraInfo: Catur Wara 資訊
        """
        if day_in_pawukon < 71:
            idx = day_in_pawukon % 4
        elif day_in_pawukon == 71:
            idx = 2  # Jaya（重複）
        elif day_in_pawukon == 72:
            idx = 3  # Menala（重複）
        else:
            idx = (day_in_pawukon - 2) % 4
        name, neptu = CATUR_WARA[idx]
        return WaraInfo(wara_type="Catur Wara", name=name, neptu=neptu)

    def _compute_panca_wara(self, day_in_pawukon: int) -> WaraInfo:
        """
        計算 Panca Wara (5天週期)

        算法：day_in_pawukon mod 5

        古法依據：Lontar Wariga — Panca Wara

        回傳：
            WaraInfo: Panca Wara 資訊
        """
        idx = day_in_pawukon % 5
        name, neptu = PANCA_WARA[idx]
        return WaraInfo(wara_type="Panca Wara", name=name, neptu=neptu)

    def _compute_sad_wara(self, day_in_pawukon: int) -> WaraInfo:
        """
        計算 Sad Wara (6天週期)

        算法：day_in_pawukon mod 6

        古法依據：Lontar Wariga — Sad Wara

        回傳：
            WaraInfo: Sad Wara 資訊
        """
        idx = day_in_pawukon % 6
        name, neptu = SAD_WARA[idx]
        return WaraInfo(wara_type="Sad Wara", name=name, neptu=neptu)

    def _compute_sapta_wara(self, day_in_pawukon: int) -> WaraInfo:
        """
        計算 Sapta Wara (7天週期) — 星期

        算法：day_in_pawukon mod 7

        古法依據：Lontar Wariga — Sapta Wara

        回傳：
            WaraInfo: Sapta Wara 資訊
        """
        idx = day_in_pawukon % 7
        name, neptu = SAPTA_WARA[idx]
        return WaraInfo(wara_type="Sapta Wara", name=name, neptu=neptu)

    def _compute_asta_wara(self, day_in_pawukon: int) -> WaraInfo:
        """
        計算 Asta Wara (8天週期)

        古法規則：非簡單 day % 8。
        Asta Wara 在 Pawukon 週期中有特殊跳過規則：
        - 如果 day_in_pawukon < 71: idx = day_in_pawukon % 8
        - 如果 day_in_pawukon == 71 或 72: 使用固定值 (Kala, Uma)
        - 如果 day_in_pawukon > 72: idx = (day_in_pawukon - 2) % 8

        古法依據：Lontar Wariga — Asta Wara 排序法

        回傳：
            WaraInfo: Asta Wara 資訊
        """
        if day_in_pawukon < 71:
            idx = day_in_pawukon % 8
        elif day_in_pawukon == 71:
            idx = 6  # Kala
        elif day_in_pawukon == 72:
            idx = 7  # Uma
        else:
            idx = (day_in_pawukon - 2) % 8
        name, neptu = ASTA_WARA[idx]
        return WaraInfo(wara_type="Asta Wara", name=name, neptu=neptu)

    def _compute_sanga_wara(self, day_in_pawukon: int) -> WaraInfo:
        """
        計算 Sanga Wara (9天週期)

        古法規則：非簡單 day % 9。
        Sanga Wara 在 Pawukon 週期中有跳過規則：
        - 如果 day_in_pawukon < 4: idx = Dangu (索引0)
        - 否則: idx = (day_in_pawukon - 3) % 9
        （前4天 [索引0-3] 固定為 Dangu，從第5天 [索引4] 開始正常循環）

        古法依據：Lontar Wariga — Sanga Wara 排序法

        回傳：
            WaraInfo: Sanga Wara 資訊
        """
        if day_in_pawukon < 4:
            idx = 0  # Dangu（前四天固定）
        else:
            idx = (day_in_pawukon - 3) % 9
        name, neptu = SANGA_WARA[idx]
        return WaraInfo(wara_type="Sanga Wara", name=name, neptu=neptu)

    def _compute_dasa_wara(self, panca: WaraInfo, sapta: WaraInfo) -> WaraInfo:
        """
        計算 Dasa Wara (10天週期)

        古法規則：Dasa Wara 索引 = (Panca Wara Urip + Sapta Wara Urip) mod 10
        這是 Wewaran 階層規則「Wewaran alah dening Wuku」的體現。

        古法依據：Lontar Wariga — Dasa Wara 表

        回傳：
            WaraInfo: Dasa Wara 資訊
        """
        total = panca.neptu + sapta.neptu
        idx = total % 10
        name, neptu = DASA_WARA[idx]
        return WaraInfo(wara_type="Dasa Wara", name=name, neptu=neptu)

    def _compute_ingkel(self, wuku_index: int) -> str:
        """
        計算 Ingkel 動物分類

        算法：Wuku 索引 // 6 → Ingkel 索引 (0-4)

        古法依據：Lontar Wariga — Ingkel 分類

        回傳：
            str: Ingkel 名稱
        """
        return INGKEL[wuku_index // 6]

    def _compute_watek(self, wuku_index: int):
        """
        計算 Watek Alit 與 Watek Madya

        算法：查 PAWATEKAN 表，取對應的索引

        古法依據：Lontar Wariga — Pawatekan 對照表

        回傳：
            tuple: (Watek Alit 名稱, Watek Madya 名稱)
        """
        alit_idx, madya_idx = PAWATEKAN[wuku_index]
        return WATEK_ALIT[alit_idx], WATEK_MADYA[madya_idx]

    def _compute_lintang(self, day_in_pawukon: int) -> str:
        """
        計算 Lintang 星宿

        算法：day_in_pawukon mod 35 → Lintang 索引

        古法依據：Lontar Wariga — Lintang 表

        回傳：
            str: Lintang 名稱
        """
        idx = day_in_pawukon % 35
        return LINTANG[idx]

    def _compute_dewasa(self, panca, sapta, tri, wuku, day_in_pawukon):
        """
        計算 Ala Ayuning Dewasa（吉凶日判斷）

        核心規則：
        1. Neptu 總和 = Panca Wara Urip + Sapta Wara Urip
        2. Neptu 總和 ≤ 9 → 初步判為吉
        3. 檢查特定凶日組合（Kajeng Kliwon, Anggara Kasih 等）
        4. 計算 Pancasuda = Neptu 總和 mod 7

        古法依據：Lontar Wariga — Dewasa Ayu / Ala 章節 / Dasar Wariga

        回傳：
            DewasaInfo: 吉凶判斷結果
        """
        neptu_sum = panca.neptu + sapta.neptu
        auspicious_labels = []
        inauspicious_labels = []
        notes = []

        # (1) Pancasuda 計算
        pancasuda_idx = neptu_sum % 7
        ps_name, ps_meaning = PANCASUDA[pancasuda_idx]

        # (2) 基本吉凶判斷：Neptu ≤ 9 初步為吉
        if neptu_sum <= 9:
            auspicious_labels.append("Dewasa Ayu（Neptu 總和 ≤ 9）")

        # (3) 特殊吉日檢查
        # Beteng（平衡日）= Tri Wara Beteng
        if tri.name == "Beteng":
            auspicious_labels.append("Beteng（均衡日）")

        # (4) 特殊凶日檢查
        # Kajeng Kliwon = Tri Wara Kajeng + Panca Wara Kliwon
        if tri.name == "Kajeng" and panca.name == "Kliwon":
            inauspicious_labels.append("Kajeng Kliwon（大忌日）")
            notes.append("Kajeng Kliwon 為傳統大忌日，忌一切重要活動")

        # Anggara Kasih = Sapta Wara Anggara + Panca Wara Kliwon
        if sapta.name == "Anggara" and panca.name == "Kliwon":
            inauspicious_labels.append("Anggara Kasih（火曜凶日）")
            notes.append("Anggara Kasih 為火曜凶日，忌重大決定")

        # Buda Cemeng = Sapta Wara Buda + Panca Wara Kliwon
        if sapta.name == "Buda" and panca.name == "Kliwon":
            inauspicious_labels.append("Buda Cemeng（水曜凶日）")
            notes.append("Buda Cemeng 為水曜凶日，宜謹慎行事")

        # Tumpek = Sapta Wara Saniscara + Panca Wara Kliwon
        if sapta.name == "Saniscara" and panca.name == "Kliwon":
            # Tumpek 有多種類型，某些視為吉
            inauspicious_labels.append("Tumpek（土曜特殊日）")
            tumpek_type = self._get_tumpek_type(wuku.index)
            notes.append(f"Tumpek 類型：{tumpek_type}")

        # Buda Kliwon Pahang（大凶）
        if (sapta.name == "Buda" and panca.name == "Kliwon"
                and wuku.name == "Pahang"):
            inauspicious_labels.append("Buda Kliwon Pahang（大凶日）")

        # (5) Neptu 總和 ≥ 10 且無特殊吉日標記 → 偏凶
        if neptu_sum >= 10 and not auspicious_labels:
            inauspicious_labels.append("Neptu 總和偏高（≥ 10）")

        # (6) Pancasuda 吉凶判斷
        if pancasuda_idx in (0, 1, 2):
            auspicious_labels.append(f"Pancasuda 吉：{ps_name}")
        elif pancasuda_idx in (3, 4, 5, 6):
            inauspicious_labels.append(f"Pancasuda 凶：{ps_name}")

        # 總體判斷
        is_auspicious = (
            len(auspicious_labels) > 0
            and len(inauspicious_labels) == 0
        )

        return DewasaInfo(
            is_auspicious=is_auspicious,
            auspicious_labels=auspicious_labels,
            inauspicious_labels=inauspicious_labels,
            neptu_sum=neptu_sum,
            pancasuda=ps_name,
            pancasuda_meaning=ps_meaning,
            notes=notes,
        )

    def _get_tumpek_type(self, wuku_index: int) -> str:
        """
        根據 Wuku 判斷 Tumpek 類型

        每 35 天出現一次 Tumpek（Saniscara + Kliwon），
        在 210 天週期中共有 6 個 Tumpek，各有不同意義。

        古法依據：Lontar Wariga — Tumpek 分類

        回傳：
            str: Tumpek 類型名稱
        """
        # 6 種 Tumpek 類型，按 Wuku 範圍劃分
        tumpek_types = {
            (0, 4):   "Tumpek Landep（器具日）",
            (5, 9):   "Tumpek Uduh / Pengatag（植物日）",
            (10, 14): "Tumpek Kuningan（祖靈日）",
            (15, 19): "Tumpek Krulut（音樂/藝術日）",
            (20, 24): "Tumpek Kandang（動物日）",
            (25, 29): "Tumpek Wayang（皮影戲日）",
        }
        for (low, high), name in tumpek_types.items():
            if low <= wuku_index <= high:
                return name
        return "Tumpek（未分類）"

    def _compute_panca_dauh(self, hour: int) -> DauhInfo:
        """
        計算 Panca Dauh 時辰（5 時辰劃分）

        依照傳統 Lontar Wariga，一日分為 5 個 Dauh，
        每個 Dauh 約 4.8 小時，各歸屬特定神明掌管。

        古法依據：Lontar Wariga — Panca Dauh 時辰表

        回傳：
            DauhInfo: Panca Dauh 時辰資訊
        """
        selected = PANCA_DAUH[0]  # 預設
        for entry in PANCA_DAUH:
            name, start, end, deity, quality, desc = entry
            if start <= hour <= end:
                selected = entry
                break
        name, start, end, deity, quality, desc = selected
        return DauhInfo(
            dauh_type="Panca Dauh",
            name=name,
            deity=deity,
            direction=desc,
            quality=quality,
        )

    def _compute_asta_dauh(self, hour: int) -> DauhInfo:
        """
        計算 Asta Dauh 時辰（8 時辰劃分，每 3 小時）

        Asta Dauh 為更精細的時辰系統，嚴格依照
        Lontar Wariga Gemet 的 8 方位神明體系。

        古法依據：Lontar Wariga Gemet — Asta Dauh

        回傳：
            DauhInfo: Asta Dauh 時辰資訊
        """
        selected = ASTA_DAUH[0]  # 預設
        for entry in ASTA_DAUH:
            name, start, end, direction, quality, desc = entry
            if start <= hour <= end:
                selected = entry
                break
        name, start, end, direction, quality, desc = selected
        return DauhInfo(
            dauh_type="Asta Dauh",
            name=name,
            deity=desc,
            direction=direction,
            quality=quality,
        )

    def _compute_penanggal(self, sun_lon: float, moon_lon: float) -> PenanggalInfo:
        """
        計算 Penanggal / Panglong（月相日）

        月相角度 = (月亮黃經 - 太陽黃經) mod 360
        - 0°~180°  → Penanggal（月盈期）1-15
        - 180°~360° → Panglong（月虧期）1-15

        Sasih 的階層規則：
        「Penanggal/Panglong alah dening Śaśih」
        月相日的計算服從於 Sasih 月份體系。

        古法依據：Lontar Wariga — Penanggal/Panglong 計算法

        回傳：
            PenanggalInfo: 月相日資訊
        """
        # 月相角度 (0-360)
        phase_deg = (moon_lon - sun_lon) % 360.0

        if phase_deg < 180.0:
            # 月盈期 (Penanggal)：0° ~ 180°，共 15 天
            day_num = max(1, min(15, int(phase_deg / 12.0) + 1))
            table = PENANGGAL_NAMES
            is_penanggal = True
        else:
            # 月虧期 (Panglong)：180° ~ 360°，共 15 天
            day_num = max(1, min(15, int((phase_deg - 180.0) / 12.0) + 1))
            table = PANGLONG_NAMES
            is_penanggal = False

        # 查找對應的表格條目
        entry = table[day_num - 1]
        seq, name, sanskrit, neptu = entry

        # 特殊聖日標記
        special = ""
        if is_penanggal and day_num == 15:
            special = "Purnama（滿月聖日）"
        elif not is_penanggal and day_num == 15:
            special = "Tilem（新月聖日）"

        return PenanggalInfo(
            is_penanggal=is_penanggal,
            day_number=day_num,
            name=name,
            neptu=neptu,
            moon_phase_deg=phase_deg,
            special=special,
        )

    def _compute_sasih(self, sun_lon, moon_lon) -> SasihInfo:
        """
        計算 Sasih（月份）與季節

        巴厘傳統 Sasih 為陰陽合曆，以太陽位置決定月份歸屬：
        - 太陽黃經每 30° 劃分一個 Sasih
        - 起始點約為 Sasih Kasa（太陽在巨蟹座附近，約黃經 90°-120°）

        季節判斷：
        - Sasih 1-6 (Kasa ~ Kanem): Lahru (乾季) / Dakshinayana（太陽南行）
        - Sasih 7-12 (Kapitu ~ Sada): Rengreng (雨季) / Uttarayana（太陽北行）

        古法依據：Lontar Wariga — Sasih 與季節劃分

        回傳：
            SasihInfo: 月份與季節資訊
        """
        # 太陽黃經 → Sasih 索引
        # Sasih Kasa 起始約太陽黃經 90°（夏至附近）
        # 每個 Sasih 約 30° 太陽行程
        sasih_idx = int(((sun_lon - 90.0) % 360.0) / 30.0)
        if sasih_idx < 0:
            sasih_idx += 12
        sasih_idx = sasih_idx % 12

        sasih_name = SASIH_NAMES[sasih_idx]
        sasih_number = sasih_idx + 1  # 1-based

        # 季節判斷
        if SEASON_LAHRU_RANGE[0] <= sasih_number <= SEASON_LAHRU_RANGE[1]:
            season = "Lahru (Kemarau)"
            season_cn = "乾季"
            ayana = "Dakshinayana（太陽南行）"
        else:
            season = "Rengreng (Penghujan)"
            season_cn = "雨季"
            ayana = "Uttarayana（太陽北行）"

        return SasihInfo(
            sasih_index=sasih_idx,
            sasih_name=sasih_name,
            season=season,
            season_cn=season_cn,
            ayana=ayana,
        )

    # --------------------------------------------------------
    # 結果轉換
    # --------------------------------------------------------

    @staticmethod
    def _wara_to_dict(w: WaraInfo) -> dict:
        """將 WaraInfo 轉為字典"""
        return {
            "wara_type": w.wara_type,
            "name": w.name,
            "neptu": w.neptu,
        }

    def _result_to_dict(self, r: WarigaResult) -> dict:
        """將 WarigaResult 轉為字典"""
        return {
            "year": r.year,
            "month": r.month,
            "day": r.day,
            "hour": r.hour,
            "minute": r.minute,
            "latitude": r.latitude,
            "longitude": r.longitude,
            "day_in_pawukon": r.day_in_pawukon,
            "wuku": {
                "index": r.wuku.index,
                "name": r.wuku.name,
                "neptu": r.wuku.neptu,
            },
            "eka_wara": self._wara_to_dict(r.eka_wara),
            "dwi_wara": self._wara_to_dict(r.dwi_wara),
            "tri_wara": self._wara_to_dict(r.tri_wara),
            "catur_wara": self._wara_to_dict(r.catur_wara),
            "panca_wara": self._wara_to_dict(r.panca_wara),
            "sad_wara": self._wara_to_dict(r.sad_wara),
            "sapta_wara": self._wara_to_dict(r.sapta_wara),
            "asta_wara": self._wara_to_dict(r.asta_wara),
            "sanga_wara": self._wara_to_dict(r.sanga_wara),
            "dasa_wara": self._wara_to_dict(r.dasa_wara),
            "ingkel": r.ingkel,
            "watek_alit": r.watek_alit,
            "watek_madya": r.watek_madya,
            "lintang": r.lintang,
            "dewasa": {
                "is_auspicious": r.dewasa.is_auspicious,
                "auspicious_labels": r.dewasa.auspicious_labels,
                "inauspicious_labels": r.dewasa.inauspicious_labels,
                "neptu_sum": r.dewasa.neptu_sum,
                "pancasuda": r.dewasa.pancasuda,
                "pancasuda_meaning": r.dewasa.pancasuda_meaning,
                "notes": r.dewasa.notes,
            },
            "sasih": {
                "sasih_index": r.sasih.sasih_index,
                "sasih_name": r.sasih.sasih_name,
                "season": r.sasih.season,
                "season_cn": r.sasih.season_cn,
                "ayana": r.sasih.ayana,
            },
            "panca_dauh": {
                "name": r.panca_dauh.name,
                "deity": r.panca_dauh.deity,
                "direction": r.panca_dauh.direction,
                "quality": r.panca_dauh.quality,
            },
            "asta_dauh": {
                "name": r.asta_dauh.name,
                "deity": r.asta_dauh.deity,
                "direction": r.asta_dauh.direction,
                "quality": r.asta_dauh.quality,
            },
            "penanggal": {
                "is_penanggal": r.penanggal.is_penanggal,
                "day_number": r.penanggal.day_number,
                "name": r.penanggal.name,
                "neptu": r.penanggal.neptu,
                "moon_phase_deg": r.penanggal.moon_phase_deg,
                "special": r.penanggal.special,
            },
            "sun_longitude": r.sun_longitude,
            "moon_longitude": r.moon_longitude,
            "julian_day": r.julian_day,
        }
