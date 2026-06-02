from astro.i18n import TRANSLATIONS
from astro.system_registry import get_system, search_systems


def test_malay_nujum_registered_for_sidebar() -> None:
    system = get_system("tab_malay_nujum")
    assert system is not None
    assert system.category == "cat_asian"
    assert system.tab_key == "tab_malay_nujum"


def test_malay_nujum_search_and_translations_exist() -> None:
    hits = [system.id for system in search_systems("mata angin")]
    assert "tab_malay_nujum" in hits

    for key in (
        "tab_malay_nujum",
        "desc_malay_nujum",
        "spinner_malay_nujum",
        "sys_hint_malay_nujum",
        "info_malay_nujum_prompt",
    ):
        assert key in TRANSLATIONS
        assert TRANSLATIONS[key]["zh"]
        assert TRANSLATIONS[key]["en"]
