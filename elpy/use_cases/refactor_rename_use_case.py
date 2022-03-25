from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Iterable, List, Optional, Protocol, Union


@dataclass
class RefactorRenameUseCase:
    refactorer: Refactorer
    presenter: RefactorRenamePresenter

    def create_rename_diff(self, request: Request):
        if not self.refactorer.can_do_renaming():
            self.presenter.present_refactoring(
                Response(changes=FailureReason.NOT_AVAILABLE)
            )
            return
        refactoring = self.refactorer.rename_identifier(
            source=request.source,
            offset=request.offset,
            file_name=request.file_name,
            new_identifier_name=request.new_name,
        )
        if refactoring is None:
            self.presenter.present_refactoring(
                Response(changes=FailureReason.NO_RESULT)
            )
            return
        self.presenter.present_refactoring(
            Response(
                changes=Changes(
                    project_path=refactoring.project_path,
                    diff=refactoring.diff,
                    changed_files=list(refactoring.changed_files),
                )
            )
        )


@dataclass
class Request:
    source: str
    offset: int
    new_name: str
    file_name: str


@dataclass
class Response:
    changes: Union[Changes, FailureReason]


class RefactorRenamePresenter(Protocol):
    def present_refactoring(self, response: Response) -> None:
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
class Coordinates:
    line: int
    column: int


@dataclass
class Refactoring:
    changed_files: Iterable[str]
    diff: str
    project_path: str


class FailureReason(enum.Enum):
    NOT_AVAILABLE = enum.auto()
    NO_RESULT = enum.auto()


@dataclass
class Changes:
    project_path: str
    diff: str
    changed_files: List[str]
