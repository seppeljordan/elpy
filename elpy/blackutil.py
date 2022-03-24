"""Glue for the "black" library.

"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import toml

from elpy.rpc import Fault


class BlackCodeFormatter:
    @dataclass
    class Config:
        line_length: int
        skip_string_normalization: bool

    def __init__(self) -> None:
        self.black = load_black()
        if not self.black:
            raise Fault("black not installed", code=400)
        self.find_pyproject_toml = self.black.files.find_pyproject_toml

    def format_code(self, code: str, directory: Path) -> str:
        config = self._get_black_configuration(directory)
        return self._run_black(code, config)

    def _run_black(self, code: str, configuration: Config) -> str:
        try:
            fm = self.black.FileMode(
                line_length=configuration.line_length,
                string_normalization=not configuration.skip_string_normalization,
            )
            reformatted_source = self.black.format_file_contents(
                src_contents=code, fast=False, mode=fm
            )
            return reformatted_source
        except self.black.NothingChanged:
            return code
        except Exception as e:
            raise Fault("Error during formatting: {}".format(e), code=400)

    def _get_black_configuration(self, directory: Path) -> Config:
        line_length = self.black.DEFAULT_LINE_LENGTH
        string_normalization = True
        pyproject_path = self.find_pyproject_toml((str(directory),))
        if pyproject_path and os.path.exists(pyproject_path):
            pyproject_config = toml.load(pyproject_path)
            black_config = pyproject_config.get("tool", {}).get("black", {})
            if "line-length" in black_config:
                line_length = black_config["line-length"]
            if "skip-string-normalization" in black_config:
                string_normalization = not black_config["skip-string-normalization"]
        return self.Config(
            line_length=line_length,
            skip_string_normalization=not string_normalization,
        )


def fix_code(code: str, directory: str) -> str:
    """Formats Python code to conform to the PEP 8 style guide."""
    formatter = BlackCodeFormatter()
    return formatter.format_code(code, Path(directory))


def load_black() -> Any:
    try:
        import black
    except ImportError:
        return None
    return black
