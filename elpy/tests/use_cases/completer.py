from typing import Iterable, List

from elpy.use_cases.get_completions_use_case import Completion


class Completer:
    def __init__(self) -> None:
        self.completions: List[Completion] = []

    def set_completions(self, completions: List[Completion]) -> None:
        self.completions = completions

    def get_completions(
        self, file_name: str, source: str, offset: int
    ) -> Iterable[Completion]:
        return self.completions
