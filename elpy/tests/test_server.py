# coding: utf-8

"""Tests for the elpy.server module"""

import os
import tempfile
import unittest
from unittest import mock

from elpy import server
from elpy.tests.support import BackendTestCase


class ServerTestCase(unittest.TestCase):
    def setUp(self):
        self.srv = server.ElpyRPCServer()


class BackendCallTestCase(ServerTestCase):
    def assert_calls_backend(self, method, add_args=[], add_kwargs={}):
        with mock.patch("elpy.server.get_source") as get_source:
            with mock.patch.object(self.srv, "backend") as backend:
                get_source.return_value = "transformed source"

                getattr(self.srv, method)(
                    "filename", "source", "offset", *add_args, **add_kwargs
                )

                get_source.assert_called_with("source")
                getattr(backend, method).assert_called_with(
                    "filename", "transformed source", "offset", *add_args, **add_kwargs
                )


class TestInit(ServerTestCase):
    def test_should_not_select_a_backend_by_default(self):
        self.assertIsNone(self.srv.backend)


class TestRPCEcho(ServerTestCase):
    def test_should_return_arguments(self):
        self.assertEqual(("hello", "world"), self.srv.rpc_echo("hello", "world"))


class TestRPCInit(ServerTestCase):
    @mock.patch("elpy.jedibackend.JediBackend")
    def test_should_set_project_root(self, JediBackend):
        self.srv.rpc_init(
            {"project_root": "/project/root", "environment": "/project/env"}
        )

        self.assertEqual("/project/root", self.srv.project_root)

    @mock.patch("jedi.create_environment")
    def test_should_set_project_env(self, create_environment):
        self.srv.rpc_init(
            {"project_root": "/project/root", "environment": "/project/env"}
        )

        create_environment.assert_called_with("/project/env", safe=False)

    @mock.patch("elpy.jedibackend.JediBackend")
    def test_should_initialize_jedi(self, JediBackend):
        self.srv.rpc_init(
            {"project_root": "/project/root", "environment": "/project/env"}
        )

        JediBackend.assert_called_with("/project/root", "/project/env")

    @mock.patch("elpy.jedibackend.JediBackend")
    def test_should_use_jedi_if_available(self, JediBackend):
        JediBackend.return_value.name = "jedi"

        self.srv.rpc_init(
            {"project_root": "/project/root", "environment": "/project/env"}
        )

        self.assertEqual("jedi", self.srv.backend.name)

    @mock.patch("elpy.jedibackend.JediBackend")
    def test_should_use_none_if_nothing_available(self, JediBackend):
        JediBackend.return_value.name = "jedi"
        old_jedi = server.jedibackend
        server.jedibackend = None

        try:
            self.srv.rpc_init(
                {"project_root": "/project/root", "environment": "/project/env"}
            )
        finally:
            server.jedibackend = old_jedi

        self.assertIsNone(self.srv.backend)


class TestRPCGetCalltip(BackendCallTestCase):
    def test_should_call_backend(self):
        self.assert_calls_backend("rpc_get_calltip")

    def test_should_handle_no_backend(self):
        self.srv.backend = None
        self.assertIsNone(self.srv.rpc_get_calltip("filname", "source", "offset"))


class TestRPCGetCompletions(BackendCallTestCase):
    def test_should_call_backend(self):
        self.assert_calls_backend("rpc_get_completions")

    def test_should_handle_no_backend(self):
        self.srv.backend = None
        self.assertEqual(
            [], self.srv.rpc_get_completions("filname", "source", "offset")
        )

    def test_should_sort_results(self):
        with mock.patch.object(self.srv, "backend") as backend:
            backend.rpc_get_completions.return_value = [
                {"name": "_e"},
                {"name": "__d"},
                {"name": "c"},
                {"name": "B"},
                {"name": "a"},
            ]
            expected = list(reversed(backend.rpc_get_completions.return_value))

            actual = self.srv.rpc_get_completions("filename", "source", "offset")

            self.assertEqual(expected, actual)

    def test_should_uniquify_results(self):
        with mock.patch.object(self.srv, "backend") as backend:
            backend.rpc_get_completions.return_value = [
                {"name": "a"},
                {"name": "a"},
            ]
            expected = [{"name": "a"}]

            actual = self.srv.rpc_get_completions("filename", "source", "offset")

            self.assertEqual(expected, actual)


class TestRPCGetCompletionDocs(ServerTestCase):
    def test_should_call_backend(self):
        with mock.patch.object(self.srv, "backend") as backend:
            self.srv.rpc_get_completion_docstring("completion")

            (backend.rpc_get_completion_docstring.assert_called_with("completion"))

    def test_should_handle_no_backend(self):
        self.srv.backend = None
        self.assertIsNone(self.srv.rpc_get_completion_docstring("foo"))


class TestRPCGetCompletionLocation(ServerTestCase):
    def test_should_call_backend(self):
        with mock.patch.object(self.srv, "backend") as backend:
            self.srv.rpc_get_completion_location("completion")

            (backend.rpc_get_completion_location.assert_called_with("completion"))

    def test_should_handle_no_backend(self):
        self.srv.backend = None
        self.assertIsNone(self.srv.rpc_get_completion_location("foo"))


class TestRPCGetDefinition(BackendCallTestCase):
    def test_should_call_backend(self):
        self.assert_calls_backend("rpc_get_definition")

    def test_should_handle_no_backend(self):
        self.srv.backend = None
        self.assertIsNone(self.srv.rpc_get_definition("filname", "source", "offset"))


class TestRPCGetDocstring(BackendCallTestCase):
    def test_should_call_backend(self):
        self.assert_calls_backend("rpc_get_docstring")

    def test_should_handle_no_backend(self):
        self.srv.backend = None
        self.assertIsNone(self.srv.rpc_get_docstring("filname", "source", "offset"))


class TestRPCGetOnelineDocstring(BackendCallTestCase):
    def test_should_call_backend(self):
        self.assert_calls_backend("rpc_get_oneline_docstring")

    def test_should_handle_no_backend(self):
        self.srv.backend = None
        self.assertIsNone(
            self.srv.rpc_get_oneline_docstring("filname", "source", "offset")
        )


class TestRPCGetCalltipOrOnelineDocstring(BackendCallTestCase):
    def test_should_call_backend(self):
        self.assert_calls_backend("rpc_get_calltip_or_oneline_docstring")

    def test_should_handle_no_backend(self):
        self.srv.backend = None
        self.assertIsNone(
            self.srv.rpc_get_calltip_or_oneline_docstring("filname", "source", "offset")
        )


class TestRPCGetRenameDiff(BackendCallTestCase):
    def test_should_call_backend(self):
        self.assert_calls_backend("rpc_get_rename_diff", add_args=["new_name"])

    def test_should_handle_no_backend(self):
        self.srv.backend = None
        self.assertIsNone(
            self.srv.rpc_get_rename_diff("filname", "source", "offset", "new_name")
        )


class TestRPCGetExtract_VariableDiff(BackendCallTestCase):
    def test_should_call_backend(self):
        self.assert_calls_backend(
            "rpc_get_extract_variable_diff", add_args=["name", 12, 13, 3, 5]
        )

    def test_should_handle_no_backend(self):
        self.srv.backend = None
        self.assertIsNone(
            self.srv.rpc_get_extract_variable_diff(
                "filname", "source", "offset", "new_name", 1, 1, 0, 3
            )
        )


class TestRPCGetExtract_FunctionDiff(BackendCallTestCase):
    def test_should_call_backend(self):
        self.assert_calls_backend(
            "rpc_get_extract_function_diff", add_args=["name", 12, 13, 3, 5]
        )

    def test_should_handle_no_backend(self):
        self.srv.backend = None
        self.assertIsNone(
            self.srv.rpc_get_extract_function_diff(
                "filname", "source", "offset", "new_name", 1, 1, 0, 4
            )
        )


class TestRPCGetInlineDiff(BackendCallTestCase):
    def test_should_call_backend(self):
        self.assert_calls_backend("rpc_get_inline_diff")

    def test_should_handle_no_backend(self):
        self.srv.backend = None
        self.assertIsNone(self.srv.rpc_get_inline_diff("filname", "source", "offset"))


class TestRPCGetPydocCompletions(ServerTestCase):
    @mock.patch.object(server, "get_pydoc_completions")
    def test_should_call_pydoc_completions(self, get_pydoc_completions):
        srv = server.ElpyRPCServer()
        srv.rpc_get_pydoc_completions()
        get_pydoc_completions.assert_called_with(None)
        srv.rpc_get_pydoc_completions("foo")
        get_pydoc_completions.assert_called_with("foo")


class TestGetPydocDocumentation(ServerTestCase):
    @mock.patch("pydoc.render_doc")
    def test_should_find_documentation(self, render_doc):
        render_doc.return_value = "expected"

        actual = self.srv.rpc_get_pydoc_documentation("open")

        render_doc.assert_called_with("open", "Elpy Pydoc Documentation for %s", False)
        self.assertEqual("expected", actual)

    def test_should_return_none_for_unknown_module(self):
        actual = self.srv.rpc_get_pydoc_documentation("frob.open")

        self.assertIsNone(actual)

    def test_should_return_valid_unicode(self):
        import json

        docstring = self.srv.rpc_get_pydoc_documentation("tarfile")

        json.dumps(docstring)


class TestRPCGetUsages(BackendCallTestCase):
    def test_should_call_backend(self):
        self.assert_calls_backend("rpc_get_usages")

    def test_should_handle_no_backend(self):
        self.srv.backend = None
        self.assertIsNone(self.srv.rpc_get_usages("filname", "source", "offset"))


class TestRPCGetNames(BackendCallTestCase):
    def test_should_call_backend(self):
        self.assert_calls_backend("rpc_get_names")

    def test_should_handle_no_backend(self):
        self.srv.backend = None
        self.assertIsNone(self.srv.rpc_get_names("filname", "source", 0))


class TestGetSource(unittest.TestCase):
    def test_should_return_string_by_default(self):
        self.assertEqual(server.get_source("foo"), "foo")

    def test_should_return_file_contents(self):
        fd, filename = tempfile.mkstemp(prefix="elpy-test-")
        self.addCleanup(os.remove, filename)
        with open(filename, "w") as f:
            f.write("file contents")

        fileobj = {"filename": filename}

        self.assertEqual(server.get_source(fileobj), "file contents")

    def test_should_clean_up_tempfile(self):
        fd, filename = tempfile.mkstemp(prefix="elpy-test-")
        with open(filename, "w") as f:
            f.write("file contents")

        fileobj = {"filename": filename, "delete_after_use": True}

        self.assertEqual(server.get_source(fileobj), "file contents")
        self.assertFalse(os.path.exists(filename))

    def test_should_support_utf8(self):
        fd, filename = tempfile.mkstemp(prefix="elpy-test-")
        self.addCleanup(os.remove, filename)
        with open(filename, "wb") as f:
            f.write("möp".encode("utf-8"))

        source = server.get_source({"filename": filename})

        self.assertEqual(source, "möp")


class TestPysymbolKey(BackendTestCase):
    def keyLess(self, a, b):
        self.assertLess(b, a)
        self.assertLess(server._pysymbol_key(a), server._pysymbol_key(b))

    def test_should_be_case_insensitive(self):
        self.keyLess("bar", "Foo")

    def test_should_sort_private_symbols_after_public_symbols(self):
        self.keyLess("foo", "_bar")

    def test_should_sort_private_symbols_after_dunder_symbols(self):
        self.assertLess(server._pysymbol_key("__foo__"), server._pysymbol_key("_bar"))

    def test_should_sort_dunder_symbols_after_public_symbols(self):
        self.keyLess("bar", "__foo")


class Autopep8TestCase(ServerTestCase):
    def test_rpc_fix_code_should_return_formatted_string(self):
        code_block = "x=       123\n"
        new_block = self.srv.rpc_fix_code(code_block, os.getcwd())
        self.assertEqual(new_block, "x = 123\n")
