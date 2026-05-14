import importlib.util
import sys
import types
from pathlib import Path

import pytest


@pytest.fixture
def financial_modules():
    fake_st = types.ModuleType("streamlit")
    fake_st.markdown = lambda *args, **kwargs: None
    sys.modules["streamlit"] = fake_st

    package_roots = [
        ("astro", Path(__file__).resolve().parents[1] / "astro"),
        ("astro.qizheng", Path(__file__).resolve().parents[1] / "astro" / "qizheng"),
        (
            "astro.qizheng.financial",
            Path(__file__).resolve().parents[1] / "astro" / "qizheng" / "financial",
        ),
    ]
    for package_name, package_path in package_roots:
        package = types.ModuleType(package_name)
        package.__path__ = [str(package_path)]
        sys.modules[package_name] = package

    loaded_modules = {}
    for module_name, file_name in (
        ("astro.qizheng.financial.name_wuxing", "name_wuxing.py"),
        ("astro.qizheng.financial.stock_renderer", "stock_renderer.py"),
    ):
        file_path = (
            Path(__file__).resolve().parents[1]
            / "astro"
            / "qizheng"
            / "financial"
            / file_name
        )
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        loaded_modules[module_name] = module

    yield loaded_modules

    for module_name in (
        "streamlit",
        "astro",
        "astro.qizheng",
        "astro.qizheng.financial",
        "astro.qizheng.financial.name_wuxing",
        "astro.qizheng.financial.stock_renderer",
    ):
        sys.modules.pop(module_name, None)


def test_merge_wuxing_distributions_sums_each_element(financial_modules):
    stock_renderer = financial_modules["astro.qizheng.financial.stock_renderer"]

    merged = stock_renderer._merge_wuxing_distributions(
        {"木": 2, "火": 1, "土": 0, "金": 0, "水": 0},
        {"木": 0, "火": 0, "土": 1, "金": 2, "水": 1},
    )

    assert merged == {"木": 2, "火": 1, "土": 1, "金": 2, "水": 1}


def test_composite_compatibility_grade_with_merged_distributions(financial_modules):
    name_wuxing = financial_modules["astro.qizheng.financial.name_wuxing"]
    stock_renderer = financial_modules["astro.qizheng.financial.stock_renderer"]

    personal_distribution = {"木": 3, "火": 0, "土": 0, "金": 0, "水": 0}
    combined_stock_distribution = stock_renderer._merge_wuxing_distributions(
        {"木": 0, "火": 0, "土": 0, "金": 0, "水": 1},
        {"木": 0, "火": 0, "土": 0, "金": 0, "水": 2},
    )

    comparison = name_wuxing.compare_wuxing(
        personal_distribution,
        "命主",
        combined_stock_distribution,
        "股票綜合能量",
    )
    grade = stock_renderer._compatibility_grade(
        comparison,
        personal_distribution,
        combined_stock_distribution,
    )

    assert comparison["relationship_code"] == "stock_feeds_you"
    assert comparison["dominant_b"] == "水"
    assert grade == {
        "grade": "S",
        "title_zh": "絕對配合",
        "title_en": "Absolute Match",
    }
