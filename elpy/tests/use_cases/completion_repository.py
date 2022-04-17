from typing import Dict, Optional

from elpy.use_cases.completion_repository import Completion


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
