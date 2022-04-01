from typing import Optional

from elpy.use_cases.refactor_rename_use_case import Refactoring


class TestingRefactorer:
    def __init__(self) -> None:
        self._can_do_renaming = True
        self._refactoring: Optional[Refactoring] = None

    def disable_renaming(self) -> None:
        self._can_do_renaming = False

    def enable_renaming(self) -> None:
        self._can_do_renaming = True

    def can_do_renaming(self) -> bool:
        return self._can_do_renaming

    def set_refactoring_result(self, refactoring: Optional[Refactoring]) -> None:
        self._refactoring = refactoring

    def rename_identifier(
        self,
        source: str,
        offset: int,
        file_name: str,
        new_identifier_name: str,
    ) -> Optional[Refactoring]:
        return self._refactoring
