import os
import pathlib
import unittest

from strict_mock import Events, Expected, MockClassError, strict_mock


class TestExampleModule(unittest.TestCase):
    def test_module_pathlib_path(self):
        expected = "users/eg/unit_test_examples"
        expected_calls = Events([
            Expected("Path", "~").returns_mock("MockPath"),
            Expected("resolve").returns_value("users/eg/unit_test_examples"),
        ])
        mock_path = strict_mock(pathlib.Path, "MockPath", events=expected_calls)
        mock_pathlib = strict_mock(pathlib, "MockPathLib", events=expected_calls)

        path = mock_pathlib.Path("~")
        actual = path.resolve()

        self.assertEqual(actual, expected, f"\nexpected: {expected}\nactual  : {actual}")
        mock_path.assert_all_calls()
        mock_pathlib.assert_all_calls()

    def test_module_pathlib_path_raises_error(self):
        expected = (
            'StrictMock: MockPathLib Discrepancies\n'
            'Data Length\n'
            '    expected: 2\n'
            '    actual  : 1\n'
            'Mismatched     0: Expected("Path", "~").returns_mock("MockPath")\n'
            '                      fix: Expected("Path", args: _empty, kwargs: _empty)\n'
            'Extra          1: Expected("resolve").returns_value("users/eg/unit_test_examples")\n'
            'Mismatched     0: Actual("Path")\n\n'
        )
        expected_calls = Events([
            Expected("Path", "~").returns_mock("MockPath"),
            Expected("resolve").returns_value("users/eg/unit_test_examples"),
        ])
        mock_path = strict_mock(pathlib.Path, "MockPath", events=expected_calls)
        mock_pathlib = strict_mock(pathlib, "MockPathLib", events=expected_calls)

        with self.assertRaises(MockClassError) as ex:
            _ = mock_pathlib.Path()
        actual = str(ex.exception)

        self.assertEqual(actual, expected, f"\nexpected: {expected}\nactual  : {actual}")
        mock_path.assert_all_calls()
        mock_pathlib.assert_all_calls()

    def test_module_os_getcwd(self):
        expected = "this directory"
        expected_calls = Events([
            Expected("getcwd").returns_value("this directory"),
        ])

        mock = strict_mock(os, "MockOS", expected_calls)
        actual = mock.getcwd()

        self.assertEqual(actual, expected, f"\nexpected: {expected}\nactual  : {actual}")
        mock.assert_all_calls()

    def test_module_os_execl(self):
        expected = None
        expected_calls = Events([
            Expected("execl", "/bin/ls", "ls", "-l"),
        ])
        mock = strict_mock(os, "MockExec", expected_calls)
        actual = mock.execl("/bin/ls", "ls", "-l")

        self.assertEqual(actual, expected, f"\nexpected: {expected}\nactual  : {actual}")
        mock.assert_all_calls()
