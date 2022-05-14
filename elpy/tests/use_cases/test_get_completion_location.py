from unittest import TestCase

from elpy.tests.use_cases.completion_repository import (
    Completion,
    CompletionRepositoryTestImpl,
)
from elpy.use_cases.get_completion_location import GetCompletionLocationInteractor


class InteractorTests(TestCase):
    def setUp(self) -> None:
        self.completion_repository = CompletionRepositoryTestImpl()
        self.interactor = GetCompletionLocationInteractor(
            completion_repository=self.completion_repository
        )

    def test_that_module_path_is_none_when_no_completion_is_present(self) -> None:
        response = self.interactor.get_completion_location(
            request=self.get_request(name="x")
        )
        self.assertIsNone(response.module_path)

    def test_that_line_is_none_when_no_completion_is_present(self) -> None:
        response = self.interactor.get_completion_location(
            request=self.get_request(name="x")
        )
        self.assertIsNone(response.line)

    def test_that_expected_module_path_is_retrieved_from_repo(self) -> None:
        expected_name = "test_completion"
        expected_module_path = "test.path"
        self.create_completion(name=expected_name, module_path=expected_module_path)
        response = self.interactor.get_completion_location(
            request=self.get_request(name=expected_name)
        )
        self.assertEqual(response.module_path, expected_module_path)

    def test_that_expected_line_is_retrieved_from_repo(self) -> None:
        expected_name = "test_completion"
        expected_line = 1234
        self.create_completion(name=expected_name, line=expected_line)
        response = self.interactor.get_completion_location(
            request=self.get_request(name=expected_name)
        )
        self.assertEqual(response.line, expected_line)

    def get_request(self, name: str) -> GetCompletionLocationInteractor.Request:
        return GetCompletionLocationInteractor.Request(name=name)

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
