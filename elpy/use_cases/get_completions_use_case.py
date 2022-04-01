from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Protocol


@dataclass
class GetCompletionsUseCase:
    completer: Completer
    presenter: GetCompletionsPresenter

    def get_completions(self, request: Request) -> None:
        response = Response(
            proposals=[
                Proposal(
                    name=completion.name,
                    suffix=completion.suffix,
                    annotation=completion.annotation,
                    description=completion.description,
                )
                for completion in self.completer.get_completions(
                    file_name=request.file_name,
                    source=request.source,
                    offset=request.offset,
                )
            ]
        )
        self.presenter.present_completion(response)


@dataclass
class Request:
    file_name: str
    source: str
    offset: int


@dataclass
class Response:
    proposals: List[Proposal]


@dataclass
class Proposal:
    name: str
    suffix: str
    annotation: str
    description: str


@dataclass
class Completion:
    name: str
    suffix: str
    annotation: str
    description: str


class Completer(Protocol):
    def get_completions(
        self, file_name: str, source: str, offset: int
    ) -> Iterable[Completion]:
        ...


class GetCompletionsPresenter(Protocol):
    def present_completion(self, response: Response) -> None:
        ...
