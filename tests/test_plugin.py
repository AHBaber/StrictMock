pytest_plugins = ["pytester"]


def test_plugin_cleanup_passes_when_assert_all_calls_called(pytester):
    pytester.makepyfile("""
        from strict_mock import Events, Expected, strict_mock

        class Spec:
            def method(self):
                pass

        def test_no_leak():
            mock = strict_mock(Spec, "CleanMock", Events([
                Expected("method"),
            ]))
            mock.method()
            assert mock.assert_all_calls()
    """)
    result = pytester.runpytest()
    result.assert_outcomes(passed=1)


def test_plugin_cleanup_raises_error_when_mock_leaks(pytester):
    pytester.makepyfile("""
        from strict_mock import Events, Expected, strict_mock

        class Spec:
            def method(self):
                pass

        def test_leaked_mock():
            mock = strict_mock(Spec, "LeakedMock", Events([
                Expected("method"),
            ]))
            # intentionally never calls mock.method() or assert_all_calls()
    """)
    result = pytester.runpytest()
    result.assert_outcomes(passed=1, errors=1)
    result.stdout.fnmatch_lines([
        "*Mocks created but assert_all_calls() was never called*",
        "*LeakedMock*",
    ])


def test_plugin_cleanup_raises_error_when_multiple_mocks_leak(pytester):
    pytester.makepyfile("""
        from strict_mock import Events, Expected, strict_mock

        class Spec:
            def method(self):
                pass

        def test_multiple_leaked_mocks():
            mock1 = strict_mock(Spec, "LeakedMock1", Events([]))
            mock2 = strict_mock(Spec, "LeakedMock2", Events([]))
            # intentionally never calls assert_all_calls() on either
    """)
    result = pytester.runpytest()
    result.assert_outcomes(passed=1, errors=1)
    result.stdout.fnmatch_lines([
        "*Mocks created but assert_all_calls() was never called*",
        "*LeakedMock1*",
        "*LeakedMock2*",
    ])


def test_plugin_cleanup_only_reports_unreported_mocks(pytester):
    pytester.makepyfile("""
        from strict_mock import Events, Expected, strict_mock

        class Spec:
            def method(self):
                pass

        def test_one_asserted_one_leaked():
            mock1 = strict_mock(Spec, "AssertedMock", Events([]))
            mock2 = strict_mock(Spec, "LeakedMock", Events([]))
            assert mock1.assert_all_calls()
            # mock2 intentionally never asserted
    """)
    result = pytester.runpytest()
    result.assert_outcomes(passed=1, errors=1)
    result.stdout.fnmatch_lines([
        "*LeakedMock*",
    ])
    assert "AssertedMock" not in result.stdout.str()
