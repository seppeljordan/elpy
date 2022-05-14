from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from elpy.use_cases.completion_repository import CompletionRepository


@dataclass
class GetCompletionLocationInteractor:
    @dataclass
    class Request:
        name: str

    @dataclass
    class Response:
        module_path: Optional[str]
        line: Optional[int]

    completion_repository: CompletionRepository

    def get_completion_location(self, request: Request) -> Response:
        if (
            location := self.completion_repository.get_completion_location(request.name)
        ) is not None:
            return self.Response(module_path=location.module_path, line=location.line)
        return self.Response(module_path=None, line=None)
