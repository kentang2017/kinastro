"""Unified orchestrator for Malay Ilmu Nujum systems."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from astro.bintang_duabelas.core import BintangDuabelasEngine

from .bintang_tujuh import compute_bintang_tujuh
from .common import compute_name_abjad_profile
from .mata_angin import compute_mata_angin_lapan
from .perkisaran_naga import compute_perkisaran_naga

MalayNujumMethod = Literal[
    "mata_angin_lapan",
    "bintang_tujuh",
    "bintang_duabelas_plus",
    "perkisaran_naga",
]


@dataclass(frozen=True)
class MalayNujumRequest:
    """Request payload for Malay Nujum API/UI orchestration."""

    method: MalayNujumMethod
    name: str = ""
    mother_name: str = ""
    moment: datetime | None = None
    latitude: float = 0.0
    longitude: float = 0.0
    script_hint: str = "auto"


class MalayNujumEngine:
    """Compute and package all Malay Ilmu Nujum systems."""

    def __init__(self) -> None:
        self._bintang_duabelas = BintangDuabelasEngine()

    def compute_mata_angin_lapan(
        self,
        name: str,
        moment: datetime,
        *,
        latitude: float = 0.0,
        longitude: float = 0.0,
        script_hint: str = "auto",
    ) -> dict[str, object]:
        return compute_mata_angin_lapan(
            name,
            moment,
            latitude=latitude,
            longitude=longitude,
            script_hint=script_hint,
        )

    def compute_bintang_tujuh(
        self,
        name: str,
        moment: datetime,
        *,
        script_hint: str = "auto",
    ) -> dict[str, object]:
        return compute_bintang_tujuh(name, moment, script_hint=script_hint)

    def compute_perkisaran_naga(self, moment: datetime) -> dict[str, object]:
        return compute_perkisaran_naga(moment)

    def compute_bintang_duabelas_plus(
        self,
        name: str,
        mother_name: str,
        *,
        script_hint: str = "auto",
        mother_script_hint: str = "auto",
    ) -> dict[str, object]:
        reading = self._bintang_duabelas.get_full_reading(
            name,
            mother_name,
            person_script_hint=script_hint,
            mother_script_hint=mother_script_hint,
        )
        person_abjad = compute_name_abjad_profile(name, script_hint=script_hint)
        mother_abjad = compute_name_abjad_profile(mother_name, script_hint=mother_script_hint)

        house = reading["house"]
        house_number = house.get("house_number", 1)
        interpretation = {
            "zh": {
                "summary": f"命主落在第 {house_number} 宮，主題為 {house.get('domain_zh', '人生課題')}。",
                "auspicious_focus": "宜先強化該宮對應資源與人脈，再啟動重大決策。",
                "caution": "若遇凶時段，先做準備與修正，不宜硬推。",
            },
            "en": {
                "summary": f"Native maps to House {house_number}, emphasizing {house.get('domain_en', 'life themes')}.",
                "auspicious_focus": "Strengthen house-related resources and alliances before major moves.",
                "caution": "During difficult periods, prioritize preparation and correction over forced execution.",
            },
        }

        return {
            "system": "bintang_duabelas_plus",
            "name_profile": person_abjad,
            "mother_profile": mother_abjad,
            "star_sign": reading.get("star_sign", {}),
            "reading": reading,
            "process_summary": {
                "zh": "整合姓名 Abjad、母系星宮映射與十二宮主題，輸出擴充版解讀模板。",
                "en": "Combines name Abjad, maternal star mapping, and house themes into an enhanced reading template.",
            },
            "fortune": {
                "verdict": "profiled",
                "verdict_zh": "已完成擴充解讀",
            },
            "interpretation_template": interpretation,
            "advice": {
                "zh": {
                    "timing": "搭配吉時再推進該宮主題事項。",
                    "direction": "可與 Mata Angin 主吉方向交叉比對。",
                },
                "en": {
                    "timing": "Execute house-related tasks during favorable periods.",
                    "direction": "Cross-check with Mata Angin dominant direction for elections.",
                },
            },
        }

    def run_request(self, request: MalayNujumRequest) -> dict[str, object]:
        """Dispatch request by method and return structured payload."""
        moment = request.moment or datetime.now()
        if request.method == "mata_angin_lapan":
            result = self.compute_mata_angin_lapan(
                request.name,
                moment,
                latitude=request.latitude,
                longitude=request.longitude,
                script_hint=request.script_hint,
            )
        elif request.method == "bintang_tujuh":
            result = self.compute_bintang_tujuh(request.name, moment, script_hint=request.script_hint)
        elif request.method == "perkisaran_naga":
            result = self.compute_perkisaran_naga(moment)
        else:
            result = self.compute_bintang_duabelas_plus(
                request.name,
                request.mother_name,
                script_hint=request.script_hint,
            )
        return {
            "method": request.method,
            "moment": moment.isoformat(),
            "result": result,
        }


__all__ = ["MalayNujumEngine", "MalayNujumMethod", "MalayNujumRequest"]
