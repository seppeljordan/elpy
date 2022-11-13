from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol

from elpy.use_cases.interface import CompletionRepository


@dataclass
class GetCompletionDocstringUseCase:
    presenter: GetCompletionDocstringPresenter
    completion_repository: CompletionRepository

    def get_completion_docstring(self, request: Request) -> None:
        return self.presenter.present_completion_docstring(
            Response(
                docstring=self.completion_repository.get_completion_docstring(
                    request.name
                )
            )
        )


@dataclass
class Request:
    name: str


@dataclass
class Response:
    docstring: Optional[str]


class GetCompletionDocstringPresenter(Protocol):
    def present_completion_docstring(self, response: Response) -> None:
        ...
