from dataclasses import dataclass
from typing import Dict, Optional

from elpy.use_cases.interface import Location


@dataclass
class Completion:
    name: str
    docstring: str
    module_path: str
    line: int

    def _get_location(self) -> Location:
        return Location(
            module_path=self.module_path,
            line=self.line,
        )


class CompletionRepositoryTestImpl:
    def __init__(self) -> None:
        self.completions: Dict[str, Completion] = {}

    def add_completion(self, completion: Completion) -> None:
        self.completions[completion.name] = completion

    def get_completion_docstring(self, name: str) -> Optional[str]:
        completion = self.completions.get(name)
        if completion:
            return completion.docstring
        else:
            return None

    def get_completion_location(self, name: str) -> Optional[Location]:
        if completion := self.completions.get(name):
            return completion._get_location()
        return None
