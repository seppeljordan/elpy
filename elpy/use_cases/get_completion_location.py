from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol

from elpy.use_cases.interface import CompletionRepository


@dataclass
class GetCompletionLocationInteractor:
    @dataclass
    class Request:
        name: str

    @dataclass
    class Response:
        module_path: Optional[str]
        line: Optional[int]

    class Presenter(Protocol):
        def present_completion_location(
            self, response: GetCompletionLocationInteractor.Response
        ) -> None:
            ...

    completion_repository: CompletionRepository
    presenter: Presenter

    def get_completion_location(self, request: Request) -> None:
        if (
            location := self.completion_repository.get_completion_location(request.name)
        ) is not None:
            self.presenter.present_completion_location(
                self.Response(module_path=location.module_path, line=location.line)
            )
        else:
            self.presenter.present_completion_location(
                self.Response(module_path=None, line=None)
            )
