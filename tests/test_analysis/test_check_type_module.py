import unittest

from strict_mock.analysis import ImportedTypes
from tests.test_analysis import dummy_module_v1, dummy_module_v2
from tests.test_analysis.dummy_module_v1 import Dummy as Dummy1
from tests.test_analysis.dummy_module_v2 import Dummy as Dummy2

V1 = "tests.test_analysis.dummy_module_v1.Dummy"
V2 = "tests.test_analysis.dummy_module_v2.Dummy"


class TestCheckTypeModule(unittest.TestCase):
    def test_check_type_aliased_types_returns_expected(self):
        cases = [
            (Dummy1, Dummy1(1), True),
            (dummy_module_v1.Dummy, Dummy1(1), True),
            (Dummy2, Dummy2(5), True),
            (dummy_module_v2.Dummy, Dummy2(1), True),
        ]
        for t, value, expected in cases:
            with self.subTest(t=t, value=value):
                it = ImportedTypes()
                ct = it.check_type
                actual = ct(t, value)
                self.assertEqual(expected, actual, f"\ntype : {t}\nvalue: {value}")

    def test_check_type_str_concat_eval_using_module_returns_expected(self):
        cases = [
            ("Dummy | None", None, True),
            (V1, dummy_module_v1.Dummy(1), True),
            (f"{V1} | None", "nope", False),
            ("Dummy | None", Dummy2(3), True),
            ("Dummy", Dummy2(4), True),
            (V2, Dummy2(4), True),
        ]
        for t, value, expected in cases:
            with self.subTest(t=t, value=value):
                it = ImportedTypes(dummy_module_v1.Dummy, dummy_module_v2.Dummy)
                ct = it.check_type
                actual = ct(t, value)
                self.assertEqual(expected, actual, f"\ntype : {t}\nvalue: {value}")

    def test_check_type_str_eval_fails_using_module_returns_expected(self):
        cases = [
            # this fails due to the fact that Dummy2 overwrites the entry for Dummy1
            ("Dummy | None", Dummy1(5), False),
            ("Dummy | None", Dummy2(5), True),
        ]
        for t, value, expected in cases:
            with self.subTest(t=t, value=value):
                it = ImportedTypes(Dummy1, Dummy2)
                ct = it.check_type
                actual = ct(t, value)
                self.assertEqual(expected, actual, f"\ntype : {t}\nvalue: {value}")


if __name__ == "__main__":
    unittest.main()
