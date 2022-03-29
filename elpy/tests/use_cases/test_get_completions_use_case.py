from typing import Callable, Iterable, List, Optional, cast
from unittest import TestCase

from elpy.tests.use_cases.dependency_injection import singleton
from elpy.use_cases.get_completions_use_case import (
    Completion,
    GetCompletionsUseCase,
    Request,
    Response,
)


class Tests(TestCase):
    def setUp(self) -> None:
        self.injector = DependencyInjector()
        self.presenter = self.injector.get_presenter()
        self.completer = self.injector.get_completer()
        self.use_case = self.injector.get_use_case()

    def test_return_no_proposals_when_completer_does_not_find_completions(self) -> None:
        self.completer.set_completions([])
        self.use_case.get_completions(self.get_request())
        self.assertResponse(lambda r: not r.proposals)

    def test_return_one_proposal_when_completer_finds_one_completion(self) -> None:
        self.completer.set_completions(
            [
                Completion(
                    name="xyz",
                    suffix="yz",
                    annotation="test_annotation",
                    description="description of integer",
                )
            ]
        )
        self.use_case.get_completions(self.get_request())
        self.assertResponse(lambda r: len(r.proposals) == 1)

    def test_return_correct_identifier_name(self) -> None:
        expected_name = "xyz"
        self.completer.set_completions(
            [
                Completion(
                    name=expected_name,
                    suffix="yz",
                    annotation="test_annotation",
                    description="description of integer",
                )
            ]
        )
        self.use_case.get_completions(self.get_request())
        self.assertResponse(
            lambda response: response.proposals[0].name == expected_name
        )

    def test_return_correct_suffix(self) -> None:
        expected_suffix = "yz"
        self.completer.set_completions(
            [
                Completion(
                    name="xyz",
                    suffix=expected_suffix,
                    annotation="test_annotation",
                    description="description of integer",
                )
            ]
        )
        self.use_case.get_completions(self.get_request())
        self.assertResponse(
            lambda response: response.proposals[0].suffix == expected_suffix
        )

    def test_return_correct_annotation(self) -> None:
        expected_annotation = "annotation test"
        self.completer.set_completions(
            [
                Completion(
                    name="xyz",
                    suffix="yz",
                    annotation=expected_annotation,
                    description="description of integer",
                )
            ]
        )
        self.use_case.get_completions(self.get_request())
        self.assertResponse(
            lambda response: response.proposals[0].annotation == expected_annotation
        )

    def test_return_correct_description(self) -> None:
        expected_description = "description test"
        self.completer.set_completions(
            [
                Completion(
                    name="xyz",
                    suffix="yz",
                    annotation="test annotation",
                    description=expected_description,
                )
            ]
        )
        self.use_case.get_completions(self.get_request())
        self.assertResponse(
            lambda response: response.proposals[0].description == expected_description
        )

    def get_request(self) -> Request:
        return Request(
            file_name="testfile.py",
            source="x = 1",
            offset=1,
        )

    def assertResponse(
        self, condition: Optional[Callable[[Response], bool]] = None
    ) -> None:
        output = self.presenter.output
        self.assertIsInstance(output, Response)
        if condition:
            response = cast(Response, output)
            self.assertTrue(condition(response))


class Completer:
    def __init__(self) -> None:
        self.completions: List[Completion] = []

    def set_completions(self, completions: List[Completion]) -> None:
        self.completions = completions

    def get_completions(
        self, file_name: str, source: str, offset: int
    ) -> Iterable[Completion]:
        return self.completions


class Presenter:
    def __init__(self) -> None:
        self.output: Optional[Response] = None

    def present_completion(self, response: Response) -> None:
        assert not self.output
        self.output = response


class DependencyInjector:
    def get_use_case(self) -> GetCompletionsUseCase:
        return GetCompletionsUseCase(
            completer=self.get_completer(),
            presenter=self.get_presenter(),
        )

    @singleton
    def get_completer(self) -> Completer:
        return Completer()

    @singleton
    def get_presenter(self) -> Presenter:
        return Presenter()
