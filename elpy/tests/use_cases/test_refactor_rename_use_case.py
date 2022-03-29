from typing import Callable, List, Optional
from unittest import TestCase

from elpy.tests.use_cases.dependency_injection import singleton
from elpy.use_cases.refactor_rename_use_case import (
    Changes,
    FailureReason,
    Refactoring,
    RefactorRenameUseCase,
    Request,
    Response,
)


class DisabledCapabilitiesTests(TestCase):
    def setUp(self) -> None:
        self.injector = DependencyInjector()
        self.refactorer = self.injector.get_refactorer()
        self.presenter = self.injector.get_presenter()
        self.use_case = self.injector.get_use_case()
        self.refactorer.disable_renaming()

    def test_with_disabled_renaming_capabilities_a_response_is_rendered(self) -> None:
        self.use_case.create_rename_diff(request=self.create_request())
        self.assertTrue(self.presenter.responses)

    def test_with_disabled_renaming_capabilities_there_is_exactly_one_response_rendered(
        self,
    ) -> None:
        self.use_case.create_rename_diff(request=self.create_request())
        self.assertEqual(len(self.presenter.responses), 1)

    def test_that_failure_reason_is_correctly_given(self) -> None:
        self.use_case.create_rename_diff(request=self.create_request())
        response = self.presenter.responses[0]
        self.assertEqual(response.changes, FailureReason.NOT_AVAILABLE)

    def create_request(self) -> Request:
        return Request(source="x = 1", offset=0, new_name="y", file_name="test.py")


class EnabledCapabilitiesWithFailingRefactoringTests(TestCase):
    def setUp(self) -> None:
        self.injector = DependencyInjector()
        self.refactorer = self.injector.get_refactorer()
        self.presenter = self.injector.get_presenter()
        self.use_case = self.injector.get_use_case()
        self.refactorer.enable_renaming()
        self.refactorer.set_refactoring_result(None)

    def test_that_failure_reason_is_correctly_given(
        self,
    ) -> None:
        self.use_case.create_rename_diff(request=self.create_request())
        response = self.presenter.responses[0]
        self.assertEqual(response.changes, FailureReason.NO_RESULT)

    def create_request(self) -> Request:
        return Request(source="x = 1", offset=0, new_name="y", file_name="test.py")


class EnabledCapabilitiesWithSucceedingRefactoring(TestCase):
    def setUp(self) -> None:
        self.injector = DependencyInjector()
        self.refactorer = self.injector.get_refactorer()
        self.presenter = self.injector.get_presenter()
        self.use_case = self.injector.get_use_case()
        self.refactorer.enable_renaming()
        self.expected_diff = "test diff"
        self.refactorer.set_refactoring_result(
            Refactoring(
                changed_files=["test.py"],
                diff=self.expected_diff,
                project_path="test/path",
            )
        )

    def test_that_expected_file_names_are_changed(self) -> None:
        self.use_case.create_rename_diff(request=self.create_request())
        changes = self.presenter.responses[0].changes
        self.assertChanges(
            changes,
            lambda c: c.changed_files == ["test.py"],
        )

    def test_that_expected_diff_is_rendered(self) -> None:
        self.use_case.create_rename_diff(request=self.create_request())
        changes = self.presenter.responses[0].changes
        self.assertChanges(
            changes,
            lambda c: c.diff == self.expected_diff,
        )

    def test_that_correct_project_path_is_returned(self) -> None:
        self.use_case.create_rename_diff(request=self.create_request())
        changes = self.presenter.responses[0].changes
        self.assertChanges(
            changes,
            lambda c: c.project_path == "test/path",
        )

    def assertChanges(
        self, candidate: object, condition: Callable[[Changes], bool]
    ) -> None:
        assert isinstance(candidate, Changes)
        self.assertTrue(condition(candidate))

    def create_request(self) -> Request:
        return Request(source="x = 1", offset=0, new_name="y", file_name="test.py")


class TestingRefactorer:
    def __init__(self) -> None:
        self._can_do_renaming = True
        self._refactoring: Optional[Refactoring] = None

    def disable_renaming(self) -> None:
        self._can_do_renaming = False

    def enable_renaming(self) -> None:
        self._can_do_renaming = True

    def can_do_renaming(self) -> bool:
        return self._can_do_renaming

    def set_refactoring_result(self, refactoring: Optional[Refactoring]) -> None:
        self._refactoring = refactoring

    def rename_identifier(
        self,
        source: str,
        offset: int,
        file_name: str,
        new_identifier_name: str,
    ) -> Optional[Refactoring]:
        return self._refactoring


class TestingPresenter:
    def __init__(self) -> None:
        self.responses: List[Response] = []

    def present_refactoring(self, response: Response) -> None:
        self.responses.append(response)


class DependencyInjector:
    def get_use_case(self) -> RefactorRenameUseCase:
        return RefactorRenameUseCase(
            refactorer=self.get_refactorer(),
            presenter=self.get_presenter(),
        )

    @singleton
    def get_refactorer(self) -> TestingRefactorer:
        return TestingRefactorer()

    @singleton
    def get_presenter(self) -> TestingPresenter:
        return TestingPresenter()
