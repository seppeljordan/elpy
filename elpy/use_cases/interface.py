from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional, Protocol


@dataclass
class Location:
    module_path: str
    line: int


class CompletionRepository(Protocol):
    def get_completion_docstring(self, name: str) -> Optional[str]:
        ...

    def get_completion_location(self, name: str) -> Optional[Location]:
        ...


class Refactorer(Protocol):
    def rename_identifier(
        self,
        source: str,
        offset: int,
        file_name: str,
        new_identifier_name: str,
    ) -> Optional[Refactoring]:
        ...

    def can_do_renaming(self) -> bool:
        ...


@dataclass
class Refactoring:
    changed_files: Iterable[str]
    diff: str
    project_path: str
