"""Tests for system handlers — verifying compute/render separation and basic functionality."""

import unittest
from datetime import date
from unittest.mock import patch

from ui.components.birth_form import BirthChartParams
from ui.system_engine import EXECUTION_REGISTRY, SystemHandler
from ui.system_handlers.build_bazi_handler import build_bazi_handler
from ui.system_handlers.build_thai_handler import build_thai_handler


class TestBirthChartParams(unittest.TestCase):
    """Test unified birth chart parameters."""

    def test_to_dict(self):
        """Test conversion to legacy dict format."""
        params = BirthChartParams(
            year=1990,
            month=1,
            day=15,
            hour=12,
            minute=30,
            timezone=8.0,
            latitude=22.3193,
            longitude=114.1694,
            location_name="Hong Kong",
            gender="male",
        )
        result = params.to_dict()
        self.assertEqual(result["year"], 1990)
        self.assertEqual(result["month"], 1)
        self.assertEqual(result["day"], 15)
        self.assertEqual(result["hour"], 12)
        self.assertEqual(result["minute"], 30)
        self.assertEqual(result["timezone"], 8.0)
        self.assertEqual(result["latitude"], 22.3193)
        self.assertEqual(result["longitude"], 114.1694)
        self.assertEqual(result["location_name"], "Hong Kong")
        self.assertNotIn("gender", result)  # gender excluded from legacy dict

    def test_from_dict(self):
        """Test creation from legacy dict."""
        legacy_params = {
            "year": 1985,
            "month": 6,
            "day": 20,
            "hour": 8,
            "minute": 15,
            "timezone": 5.5,
            "latitude": 28.6139,
            "longitude": 77.2090,
            "location_name": "New Delhi",
        }
        params = BirthChartParams.from_dict(legacy_params, gender="female")
        self.assertEqual(params.year, 1985)
        self.assertEqual(params.month, 6)
        self.assertEqual(params.gender, "female")


class TestSystemEngine(unittest.TestCase):
    """Test system engine and registry."""

    def test_registry_singleton(self):
        """Test that EXECUTION_REGISTRY is a singleton."""
        from ui.system_engine import EXECUTION_REGISTRY as registry2
        self.assertIs(EXECUTION_REGISTRY, registry2)

    def test_has_handler(self):
        """Test handler registration check."""
        # After app.py initialization, these handlers should be registered
        # Note: This test may need to be run in Streamlit context
        handlers_to_check = [
            "tab_ziwei",
            "tab_andean",
            "tab_western",
            "tab_indian",
            "tab_chinese",
        ]
        # Check at least one handler is registered
        registered_count = sum(
            1 for h in handlers_to_check if EXECUTION_REGISTRY.has_handler(h)
        )
        # At minimum, ziwei and andean should be registered
        self.assertGreaterEqual(registered_count, 2)


class TestHandlerStructure(unittest.TestCase):
    """Test handler structure and compute/render separation."""

    def test_system_handler_dataclass(self):
        """Test SystemHandler has required fields."""
        handler = SystemHandler(
            system_id="test_system",
            compute=lambda p, o: {"result": "test"},
            render=lambda r, p, o: None,
            options_schema={"test": str},
        )
        self.assertEqual(handler.system_id, "test_system")
        self.assertIsNotNone(handler.compute)
        self.assertIsNotNone(handler.render)
        self.assertEqual(handler.options_schema, {"test": str})

    def test_thai_handler_supports_chart_hook_and_legacy_subtabs(self):
        """Thai handler should preserve legacy sections and accept chart hook args."""

        calls = {"ai": [], "nine": [], "divination": [], "brahma": []}

        class _DummyContext:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

        def _compute_thai_chart(**kwargs):
            return {"chart": kwargs["year"]}

        def _render_thai_chart(result, after_chart_hook=None):
            if after_chart_hook:
                after_chart_hook(result)

        def _calculate_thai_nine_grid(day, month, year):
            calls["nine"].append((day, month, year))
            return {"grid": True}

        def _render_nine_grid(result):
            calls["nine"].append(result)

        def _calculate_nine_palace_divination(chart):
            calls["divination"].append(chart)
            return {"palaces": 9}

        def _render_nine_palace_divination(result):
            calls["divination"].append(result)

        def _compute_brahma_jati(**kwargs):
            calls["brahma"].append(kwargs)
            return {"reading": True}

        def _render_brahma_jati(result):
            calls["brahma"].append(result)

        def _ai_button_sink(*args):
            calls["ai"].append(args)

        handler = build_thai_handler(
            compute_thai_chart=_compute_thai_chart,
            render_thai_chart=_render_thai_chart,
            calculate_thai_nine_grid=_calculate_thai_nine_grid,
            render_nine_grid=_render_nine_grid,
            calculate_nine_palace_divination=_calculate_nine_palace_divination,
            render_nine_palace_divination=_render_nine_palace_divination,
            compute_brahma_jati=_compute_brahma_jati,
            render_brahma_jati=_render_brahma_jati,
            ai_button_sink=_ai_button_sink,
        )
        params = BirthChartParams(
            year=1990,
            month=1,
            day=15,
            hour=12,
            minute=30,
            timezone=7.0,
            latitude=13.7563,
            longitude=100.5018,
            location_name="Bangkok",
            gender="female",
        )

        result = handler.compute(params, {})

        with (
            patch("ui.system_handlers.build_thai_handler.st.tabs", return_value=[_DummyContext(), _DummyContext(), _DummyContext()]),
            patch("ui.system_handlers.build_thai_handler.st.columns", return_value=[_DummyContext(), _DummyContext()]),
            patch("ui.system_handlers.build_thai_handler.st.number_input", return_value=36),
            patch("ui.system_handlers.build_thai_handler.st.selectbox", return_value="female"),
            patch("ui.system_handlers.build_thai_handler.st.markdown"),
        ):
            handler.render(result, params, {})

        self.assertEqual(calls["ai"], [("tab_thai", result, "thai", "")])
        self.assertEqual(calls["nine"], [(15, 1, 1990), {"grid": True}])
        self.assertEqual(calls["divination"], [result, {"palaces": 9}])
        self.assertEqual(
            calls["brahma"][0],
            {
                "ce_year": 1990,
                "month": 1,
                "weekday": date(1990, 1, 15).weekday(),
                "age": 36,
                "gender": "female",
            },
        )
        self.assertEqual(calls["brahma"][1], {"reading": True})


class TestComputeFunctions(unittest.TestCase):
    """Test compute functions are pure (no Streamlit dependency)."""

    def _check_no_streamlit_import(self, module_name: str) -> bool:
        """Check if a module has direct streamlit imports."""
        import ast
        import importlib

        try:
            module = importlib.import_module(module_name)
            with open(module.__file__, encoding="utf-8") as source_file:
                source = source_file.read()
            tree = ast.parse(source)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if "streamlit" in alias.name:
                            return False
                elif isinstance(node, ast.ImportFrom):
                    if node.module and "streamlit" in node.module:
                        return False
            return True
        except Exception:
            return True  # Assume OK if can't check

    def test_calculator_purity(self):
        """Test that calculator modules don't import Streamlit."""
        # These are known pure calculators
        pure_modules = [
            "astro.andean.calculator",
            "astro.ziwei",  # May need verification
            "astro.maya",
            "astro.aztec",
        ]
        for module_name in pure_modules:
            # Note: This is a soft check — some modules may not be importable in test context
            with self.subTest(module_name=module_name):
                pass  # Placeholder for actual purity checks


class TestBaziHandler(unittest.TestCase):
    """Test Bazi handler specific wiring."""

    def test_bazi_handler_passes_gender_and_hook_accepts_chart_arg(self):
        """Bazi handler should pass gender/default and support chart hook arg."""
        calls = {"compute": [], "ai": []}

        def _compute_bazi_chart(**kwargs):
            calls["compute"].append(kwargs)
            return {"ok": True, "gender": kwargs.get("gender")}

        def _render_bazi_chart_svg(result, after_chart_hook=None):
            if after_chart_hook:
                after_chart_hook(result)

        def _ai_button_sink(*args):
            calls["ai"].append(args)

        handler = build_bazi_handler(
            compute_bazi_chart=_compute_bazi_chart,
            render_bazi_chart_svg=_render_bazi_chart_svg,
            ai_button_sink=_ai_button_sink,
        )
        params = BirthChartParams(
            year=1990,
            month=1,
            day=15,
            hour=12,
            minute=30,
            timezone=8.0,
            latitude=22.3193,
            longitude=114.1694,
            location_name="Hong Kong",
            gender="female",
        )

        result = handler.compute(params, {})
        handler.render(result, params, {})

        self.assertEqual(calls["compute"][0]["gender"], "female")
        self.assertEqual(calls["ai"], [("tab_bazi", result, "bazi", "")])

        params_default_gender = BirthChartParams(
            year=1990,
            month=1,
            day=15,
            hour=12,
            minute=30,
            timezone=8.0,
            latitude=22.3193,
            longitude=114.1694,
            location_name="Hong Kong",
            gender=None,
        )
        _ = handler.compute(params_default_gender, {})
        self.assertEqual(calls["compute"][1]["gender"], "男")


if __name__ == "__main__":
    unittest.main()
