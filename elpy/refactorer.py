from dataclasses import dataclass
from typing import Iterable, Optional, Protocol


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

    def get_completion_docstring(self, name: str) -> Optional[str]:
        ...
