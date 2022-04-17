from dataclasses import dataclass
from typing import Optional, Protocol


@dataclass
class Completion:
    name: str
    docstring: str


class CompletionRepository(Protocol):
    def get_completion_docstring(self, name: str) -> Optional[str]:
        ...
