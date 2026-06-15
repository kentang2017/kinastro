"""Tests for Liu Ren solar-return annual sub-tab support."""

from __future__ import annotations

from astro.annual.timeline import compute_sr_liuren_for_virtual_age
from astro.system_registry import get_system
from tests.test_annual_sr_timeline import BIRTH


def test_liuren_has_sr_annual_subtab():
    system = get_system("tab_liuren")
    assert system is not None
    assert system.supports_return is True
    subtab_keys = [item.i18n_key for item in system.sub_tabs]
    assert "liuren_subtab_natal" in subtab_keys
    assert "liuren_subtab_sr_annual" in subtab_keys


def test_sr_sanshi_sidebar_tab_removed():
    assert get_system("tab_sr_sanshi") is None


def test_compute_sr_liuren_single_virtual_age():
    flow_year = compute_sr_liuren_for_virtual_age(BIRTH, virtual_age_years=35)
    assert flow_year.age == 35
    assert flow_year.year == BIRTH.year + 34
    assert flow_year.liuren_chart
    assert flow_year.liuren_lunming
    assert flow_year.exact_sr_datetime_local


def test_virtual_age_bounds():
    import pytest

    with pytest.raises(ValueError, match="virtual age"):
        compute_sr_liuren_for_virtual_age(BIRTH, 0)
    with pytest.raises(ValueError, match="virtual age"):
        compute_sr_liuren_for_virtual_age(BIRTH, 121)