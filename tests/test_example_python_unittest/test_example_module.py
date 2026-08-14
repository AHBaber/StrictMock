import os
import pathlib
import unittest

from strict_mock import Events, Expected, MockClassError, strict_mock
from tests.fakes import fake_widgets


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

    def test_module_class_with_inherited_init(self):
        # Widget declares no __init__; its constructor parameters come from BaseWidget
        expected = "<widget>"
        expected_calls = Events([
            Expected("Widget", "gauge", 3).returns_mock("MockWidget"),
            Expected("render").returns_value("<widget>"),
        ])
        mock_widget = strict_mock(fake_widgets.Widget, "MockWidget", events=expected_calls)
        mock_widgets = strict_mock(fake_widgets, "MockWidgets", events=expected_calls)

        widget = mock_widgets.Widget("gauge", 3)
        actual = widget.render()

        self.assertEqual(actual, expected, f"\nexpected: {expected}\nactual  : {actual}")
        mock_widget.assert_all_calls()
        mock_widgets.assert_all_calls()

    def test_module_class_without_introspectable_signature(self):
        # os.error is OSError, a C type whose signature inspect cannot read, so the
        # mock constructor falls back to an empty signature and takes no arguments
        expected_calls = Events([
            Expected("error").returns_mock("MockError"),
        ])
        mock_error = strict_mock(os.error, "MockError", events=expected_calls)
        mock_os = strict_mock(os, "MockOS", events=expected_calls)

        actual = mock_os.error()

        self.assertIs(actual, mock_error, f"\nexpected: {mock_error}\nactual  : {actual}")
        mock_error.assert_all_calls()
        mock_os.assert_all_calls()

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
