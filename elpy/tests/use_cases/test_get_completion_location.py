from typing import Callable, Optional, cast
from unittest import TestCase

from elpy.tests.use_cases.completion_repository import (
    Completion,
    CompletionRepositoryTestImpl,
)
from elpy.use_cases.get_completion_location import GetCompletionLocationInteractor


class InteractorTests(TestCase):
    def setUp(self) -> None:
        self.completion_repository = CompletionRepositoryTestImpl()
        self.presenter = Presenter()
        self.interactor = GetCompletionLocationInteractor(
            completion_repository=self.completion_repository,
            presenter=self.presenter,
        )

    def test_that_module_path_is_none_when_no_completion_is_present(self) -> None:
        self.interactor.get_completion_location(request=self.get_request(name="x"))
        self.assertResponse(lambda r: r.module_path is None)

    def test_that_line_is_none_when_no_completion_is_present(self) -> None:
        self.interactor.get_completion_location(request=self.get_request(name="x"))
        self.assertResponse(lambda r: r.line is None)

    def test_that_expected_module_path_is_retrieved_from_repo(self) -> None:
        expected_name = "test_completion"
        expected_module_path = "test.path"
        self.create_completion(name=expected_name, module_path=expected_module_path)
        self.interactor.get_completion_location(
            request=self.get_request(name=expected_name)
        )
        self.assertResponse(lambda r: r.module_path == expected_module_path)

    def test_that_expected_line_is_retrieved_from_repo(self) -> None:
        expected_name = "test_completion"
        expected_line = 1234
        self.create_completion(name=expected_name, line=expected_line)
        self.interactor.get_completion_location(
            request=self.get_request(name=expected_name)
        )
        self.assertResponse(lambda r: r.line == expected_line)

    def get_request(self, name: str) -> GetCompletionLocationInteractor.Request:
        return GetCompletionLocationInteractor.Request(name=name)

    def assertResponse(
        self, condition: Callable[[GetCompletionLocationInteractor.Response], bool]
    ) -> None:
        self.assertTrue(self.presenter.response)
        self.assertTrue(
            condition(
                cast(
                    GetCompletionLocationInteractor.Response,
                    self.presenter.response,
                )
            )
        )

    def create_completion(
        self, name: str, module_path: str = "test.module_path", line: int = 3
    ) -> None:
        self.completion_repository.add_completion(
            Completion(
                name=name,
                docstring="",
                module_path=module_path,
                line=line,
            )
        )


class Presenter:
    def __init__(self) -> None:
        self.response: Optional[GetCompletionLocationInteractor.Response] = None

    def present_completion_location(
        self, response: GetCompletionLocationInteractor.Response
    ) -> None:
        assert not self.response
        self.response = response
