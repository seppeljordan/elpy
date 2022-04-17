from functools import lru_cache

from elpy.tests.use_cases.completer import Completer
from elpy.tests.use_cases.completion_repository import CompletionRepositoryTestImpl
from elpy.tests.use_cases.presenters import (
    GetCompletionDocstringPresenterTestImpl,
    GetCompletionsPresenterTestImpl,
    RefactorRenamePresenterTestImpl,
)
from elpy.tests.use_cases.refactorer import TestingRefactorer
from elpy.use_cases.get_completion_docstring_use_case import (
    GetCompletionDocstringUseCase,
)
from elpy.use_cases.get_completions_use_case import GetCompletionsUseCase
from elpy.use_cases.refactor_rename_use_case import RefactorRenameUseCase

singleton = lru_cache()


class DependencyInjector:
    def get_refactor_rename_use_case(self) -> RefactorRenameUseCase:
        return RefactorRenameUseCase(
            refactorer=self.get_refactorer(),
            presenter=self.get_refactor_rename_presenter(),
        )

    @singleton
    def get_refactorer(self) -> TestingRefactorer:
        return TestingRefactorer()

    @singleton
    def get_refactor_rename_presenter(self) -> RefactorRenamePresenterTestImpl:
        return RefactorRenamePresenterTestImpl()

    def get_completions_use_case(self) -> GetCompletionsUseCase:
        return GetCompletionsUseCase(
            completer=self.get_completer(),
            presenter=self.get_completions_presenter(),
        )

    def get_completion_docstring_use_case(self) -> GetCompletionDocstringUseCase:
        return GetCompletionDocstringUseCase(
            presenter=self.get_completion_docstring_presenter(),
            completion_repository=self.get_completion_repository(),
        )

    @singleton
    def get_completer(self) -> Completer:
        return Completer()

    @singleton
    def get_completions_presenter(self) -> GetCompletionsPresenterTestImpl:
        return GetCompletionsPresenterTestImpl()

    @singleton
    def get_completion_docstring_presenter(
        self,
    ) -> GetCompletionDocstringPresenterTestImpl:
        return GetCompletionDocstringPresenterTestImpl()

    @singleton
    def get_completion_repository(self) -> CompletionRepositoryTestImpl:
        return CompletionRepositoryTestImpl()
