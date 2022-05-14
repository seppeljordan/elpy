from dataclasses import dataclass
from typing import Optional, Protocol


@dataclass
class Location:
    module_path: str
    line: int


class CompletionRepository(Protocol):
    def get_completion_docstring(self, name: str) -> Optional[str]:
        ...

    def get_completion_location(self, name: str) -> Optional[Location]:
        ...
