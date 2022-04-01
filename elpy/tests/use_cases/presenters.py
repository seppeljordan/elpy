from typing import List, Optional

from elpy.use_cases import get_completions_use_case, refactor_rename_use_case


class GetCompletionsPresenterTestImpl:
    def __init__(self) -> None:
        self.output: Optional[get_completions_use_case.Response] = None

    def present_completion(self, response: get_completions_use_case.Response) -> None:
        assert not self.output
        self.output = response


class RefactorRenamePresenterTestImpl:
    def __init__(self) -> None:
        self.responses: List[refactor_rename_use_case.Response] = []

    def present_refactoring(self, response: refactor_rename_use_case.Response) -> None:
        self.responses.append(response)
