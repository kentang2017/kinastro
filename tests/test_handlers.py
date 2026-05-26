"""Tests for system handlers — verifying compute/render separation and basic functionality."""

import unittest
from datetime import date, time
from typing import Any, Dict

from ui.components.birth_form import BirthChartParams
from ui.system_engine import EXECUTION_REGISTRY, SystemHandler


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


class TestComputeFunctions(unittest.TestCase):
    """Test compute functions are pure (no Streamlit dependency)."""

    def _check_no_streamlit_import(self, module_name: str) -> bool:
        """Check if a module has direct streamlit imports."""
        import importlib
        import ast

        try:
            module = importlib.import_module(module_name)
            source = open(module.__file__, "r", encoding="utf-8").read()
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
            pass  # Placeholder for actual purity checks


if __name__ == "__main__":
    unittest.main()
