from __future__ import annotations

from typing import List
from unittest import TestCase

from elpy.use_cases.completion_repository import Completion
from elpy.use_cases.get_completion_docstring_use_case import Request, Response

from .dependency_injection import DependencyInjector


class UseCaseTests(TestCase):
    def setUp(self) -> None:
        self.injector = DependencyInjector()
        self.use_case = self.injector.get_completion_docstring_use_case()
        self.presenter = self.injector.get_completion_docstring_presenter()
        self.completion_repository = self.injector.get_completion_repository()

    def test_with_no_prior_completion_requested_there_is_no_docstring_available(
        self,
    ) -> None:
        self.use_case.get_completion_docstring(self.get_request())
        self.assertIsNone(self.get_response().docstring)

    def test_with_a_prior_completion_dont_return_none(self) -> None:
        self.get_completion(
            completions=[Completion(name="x", docstring="test docstring")]
        )
        self.use_case.get_completion_docstring(self.get_request())
        self.assertIsNotNone(self.get_response().docstring)

    def get_request(self) -> Request:
        return Request(
            name="x",
        )

    def get_response(self) -> Response:
        response = self.presenter.pop_response()
        self.assertIsNotNone(response)
        assert response
        return response

    def get_completion(self, completions: List[Completion]) -> None:
        for completion in completions:
            self.completion_repository.add_completion(completion)
