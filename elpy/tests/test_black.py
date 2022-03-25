# coding: utf-8
"""Tests for the elpy.black module"""

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

from elpy import blackutil
from elpy.rpc import Fault
from elpy.tests.support import BackendTestCase


class BLACKTestCase(BackendTestCase):
    def setUp(self) -> None:
        self.environment = TestEnvironment()

    def tearDown(self) -> None:
        self.environment.clean()

    def test_fix_code_should_throw_error_for_invalid_code(self) -> None:
        src = "x = "
        with self.assertRaises(Fault):
            blackutil.fix_code(src, self.environment.get_working_directory())

    @mock.patch("elpy.blackutil.load_black")
    def test_fix_code_should_throw_error_without_black_installed(
        self, mocked_function: mock.Mock
    ) -> None:
        mocked_function.return_value = None
        src = "x=       123\n"
        with self.assertRaises(Fault):
            blackutil.fix_code(src, self.environment.get_working_directory())

    def test_fix_code(self) -> None:
        testdata = [
            ("x=       123\n", "x = 123\n"),
            ("x=1; \ny=2 \n", "x = 1\ny = 2\n"),
        ]
        for src, expected in testdata:
            self._assert_format(src, expected)

    def test_perfect_code(self) -> None:
        testdata = [
            ("x = 123\n", "x = 123\n"),
            ("x = 1\ny = 2\n", "x = 1\ny = 2\n"),
        ]
        for src, expected in testdata:
            self._assert_format(src, expected)

    def test_should_read_options_from_pyproject_toml(self) -> None:
        self.environment.create_or_replace_pyproject_toml(
            "[tool.black]\nline-length = 10"
        )

        testdata = [
            ("x=       123\n", "x = 123\n"),
            ("x=1; \ny=2 \n", "x = 1\ny = 2\n"),
            (
                "x, y, z, a, b, c = 123, 124, 125, 126, 127, 128",
                "(\n    x,\n    y,\n    z,\n    a,\n    b,\n    c,\n)"
                " = (\n    123,\n    124,\n    125,"
                "\n    126,\n    127,\n    128,\n)\n",
            ),
        ]
        for src, expected in testdata:
            self._assert_format(src, expected)

    def _assert_format(self, src: str, expected: str) -> None:
        new_block = blackutil.fix_code(src, self.environment.get_working_directory())
        self.assertEqual(new_block, expected)


class TestEnvironment:
    def __init__(self) -> None:
        self.directory = TemporaryDirectory()

    def get_working_directory(self) -> str:
        return self.directory.name

    def create_or_replace_pyproject_toml(self, content: str) -> None:
        path = Path(self.directory.name)
        toml_path = path / "pyproject.toml"
        toml_path.write_text(content)

    def clean(self) -> None:
        self.directory.cleanup()
