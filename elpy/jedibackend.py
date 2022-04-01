"""Elpy backend using the Jedi library.

This backend uses the Jedi library:

https://github.com/davidhalter/jedi

"""

import re
import sys
import traceback
from typing import Any, Dict, Iterable, List, Optional, Tuple

import jedi
from jedi import debug

from elpy import rpc
from elpy.rpc import Fault
from elpy.use_cases import get_completions_use_case, refactor_rename_use_case


class JediBackend:
    """The Jedi backend class.

    Implements the RPC calls we can pass on to Jedi.

    Documentation: http://jedi.jedidjah.ch/en/latest/docs/plugin-api.html

    """

    name = "jedi"

    def __init__(
        self, project_root: str, environment_binaries_path: Optional[str]
    ) -> None:
        self.environment = None
        if environment_binaries_path is not None:
            self.environment = jedi.create_environment(
                environment_binaries_path, safe=False
            )
        self.completions: Dict[Any, Any] = {}
        sys.path.append(project_root)

    def rpc_get_completions(
        self, filename: str, source: str, offset: int
    ) -> List[Dict[str, str]]:
        output_port = GetCompletionsOutputPort()
        use_case = get_completions_use_case.GetCompletionsUseCase(
            completer=self,
            presenter=output_port,
        )
        use_case.get_completions(
            get_completions_use_case.Request(
                file_name=filename,
                source=source,
                offset=offset,
            )
        )
        return output_port.render_completions()

    def rpc_get_completion_docstring(self, completion):
        proposal = self.completions.get(completion)
        if proposal is None:
            return None
        else:
            return proposal.docstring(fast=False)

    def rpc_get_completion_location(self, completion):
        proposal = self.completions.get(completion)
        if proposal is None:
            return None
        else:
            return (proposal.module_path, proposal.line)

    def rpc_get_docstring(self, filename, source, offset):
        line, column = pos_to_linecol(source, offset)
        locations = run_with_debug(
            jedi,
            "goto",
            code=source,
            path=filename,
            environment=self.environment,
            fun_kwargs={
                "line": line,
                "column": column,
                "follow_imports": True,
                "follow_builtin_imports": True,
            },
        )
        if not locations:
            return None
        # Filter uninteresting things
        if locations[-1].name in [
            "str",
            "int",
            "float",
            "bool",
            "tuple",
            "list",
            "dict",
        ]:
            return None
        if locations[-1].docstring():
            return (
                "Documentation for {0}:\n\n".format(locations[-1].full_name)
                + locations[-1].docstring()
            )
        else:
            return None

    def rpc_get_definition(self, filename, source, offset):
        line, column = pos_to_linecol(source, offset)
        locations = run_with_debug(
            jedi,
            "goto",
            code=source,
            path=filename,
            environment=self.environment,
            fun_kwargs={
                "line": line,
                "column": column,
                "follow_imports": True,
                "follow_builtin_imports": True,
            },
        )
        if not locations:
            return None
        # goto_definitions() can return silly stuff like __builtin__
        # for int variables, so we remove them. See issue #76.
        locations = [
            loc
            for loc in locations
            if (
                loc.module_path is not None
                and loc.module_name != "builtins"
                and loc.module_name != "__builtin__"
            )
        ]
        if len(locations) == 0:
            return None
        loc = locations[-1]
        try:
            if loc.module_path == filename:
                offset = linecol_to_pos(source, loc.line, loc.column)
            else:
                with open(loc.module_path) as f:
                    offset = linecol_to_pos(f.read(), loc.line, loc.column)
        except IOError:  # pragma: no cover
            return None
        return (loc.module_path, offset)

    def rpc_get_assignment(self, filename, source, offset):
        raise Fault("Obsolete since jedi 17.0. Please use 'get_definition'.")

    def rpc_get_calltip(self, filename, source, offset):
        line, column = pos_to_linecol(source, offset)
        calls = run_with_debug(
            jedi,
            "get_signatures",
            code=source,
            path=filename,
            environment=self.environment,
            fun_kwargs={"line": line, "column": column},
        )
        if not calls:
            return None
        params = [re.sub("^param ", "", param.description) for param in calls[0].params]
        return {"name": calls[0].name, "index": calls[0].index, "params": params}

    def rpc_get_calltip_or_oneline_docstring(self, filename, source, offset):
        """
        Return the current function calltip or its oneline docstring.

        Meant to be used with eldoc.
        """
        # Try to get a oneline docstring then
        docs = self.rpc_get_oneline_docstring(
            filename=filename, source=source, offset=offset
        )
        if docs is not None:
            if docs["doc"] != "No documentation":
                docs["kind"] = "oneline_doc"
                return docs
        # Try to get a calltip
        calltip = self.rpc_get_calltip(filename=filename, source=source, offset=offset)
        if calltip is not None:
            calltip["kind"] = "calltip"
            return calltip
        # Ok, no calltip, just display the function name
        if docs is not None:
            docs["kind"] = "oneline_doc"
            return docs
        # Giving up...
        return None

    def rpc_get_oneline_docstring(self, filename, source, offset):
        """Return a oneline docstring for the symbol at offset"""
        line, column = pos_to_linecol(source, offset)
        definitions = run_with_debug(
            jedi,
            "goto",
            code=source,
            path=filename,
            environment=self.environment,
            fun_kwargs={"line": line, "column": column},
        )
        if not definitions:
            return None
        # avoid unintersting stuff
        definitions = [
            defi
            for defi in definitions
            if defi.name not in ["str", "int", "float", "bool", "tuple", "list", "dict"]
        ]
        if len(definitions) == 0:
            return None
        definition = definitions[0]
        # Get name
        if definition.type in ["function", "class"]:
            raw_name = definition.name
            name = "{}()".format(raw_name)
            doc = definition.docstring().split("\n")
        elif definition.type in ["module"]:
            raw_name = definition.name
            name = "{} {}".format(raw_name, definition.type)
            doc = definition.docstring().split("\n")
        elif definition.type in ["instance"] and hasattr(definition, "name"):
            raw_name = definition.name
            name = raw_name
            doc = definition.docstring().split("\n")
        else:
            return None
        # Keep only the first paragraph that is not a function declaration
        lines = []
        call = "{}(".format(raw_name)
        # last line
        doc.append("")
        for i in range(len(doc)):
            if doc[i] == "" and len(lines) != 0:
                paragraph = " ".join(lines)
                lines = []
                if call != paragraph[0 : len(call)]:
                    break
                paragraph = ""
                continue
            lines.append(doc[i])
        # Keep only the first sentence
        onelinedoc = paragraph.split(". ", 1)
        if len(onelinedoc) == 2:
            onelinedoc = onelinedoc[0] + "."
        else:
            onelinedoc = onelinedoc[0]
        if onelinedoc == "":
            onelinedoc = "No documentation"
        return {"name": name, "doc": onelinedoc}

    def rpc_get_usages(self, filename, source, offset):
        """Return the uses of the symbol at offset.

        Returns a list of occurrences of the symbol, as dicts with the
        fields name, filename, and offset.

        """
        line, column = pos_to_linecol(source, offset)
        uses = run_with_debug(
            jedi,
            "get_references",
            code=source,
            path=filename,
            environment=self.environment,
            fun_kwargs={"line": line, "column": column},
        )
        if uses is None:
            return None
        result = []
        for use in uses:
            if use.module_path == filename:
                offset = linecol_to_pos(source, use.line, use.column)
            elif use.module_path is not None:
                with open(use.module_path) as f:
                    text = f.read()
                offset = linecol_to_pos(text, use.line, use.column)
            result.append(
                {"name": use.name, "filename": use.module_path, "offset": offset}
            )
        return result

    def rpc_get_names(self, filename, source, offset):
        """Return the list of possible names"""
        names = run_with_debug(
            jedi,
            "get_names",
            code=source,
            path=filename,
            environment=self.environment,
            fun_kwargs={"all_scopes": True, "definitions": True, "references": True},
        )
        result = []
        for name in names:
            if name.module_path == filename:
                offset = linecol_to_pos(source, name.line, name.column)
            elif name.module_path is not None:
                with open(name.module_path) as f:
                    text = f.read()
                offset = linecol_to_pos(text, name.line, name.column)
            result.append(
                {"name": name.name, "filename": name.module_path, "offset": offset}
            )
        return result

    def rpc_get_rename_diff(
        self, filename: str, source: str, offset: int, new_name: str
    ) -> Dict[str, Any]:
        """Get the diff resulting from renaming the thing at point"""
        output_port = RefactorRenameOutputPort()
        use_case = refactor_rename_use_case.RefactorRenameUseCase(
            presenter=output_port,
            refactorer=self,
        )
        use_case.create_rename_diff(
            request=refactor_rename_use_case.Request(
                source=source,
                offset=offset,
                new_name=new_name,
                file_name=filename,
            )
        )
        return output_port.get_response()

    def rpc_get_extract_variable_diff(
        self, filename, source, offset, new_name, line_beg, line_end, col_beg, col_end
    ):
        """Get the diff resulting from extracting the selected code"""
        if not hasattr(jedi.Script, "extract_variable"):  # pragma: no cover
            return {"success": "Not available"}
        ren = run_with_debug(
            jedi,
            "extract_variable",
            code=source,
            path=filename,
            environment=self.environment,
            fun_kwargs={
                "line": line_beg,
                "until_line": line_end,
                "column": col_beg,
                "until_column": col_end,
                "new_name": new_name,
            },
        )
        if ren is None:
            return {"success": False}
        else:
            return {
                "success": True,
                "project_path": ren._inference_state.project._path,
                "diff": ren.get_diff(),
                "changed_files": list(ren.get_changed_files().keys()),
            }

    def rpc_get_extract_function_diff(
        self, filename, source, offset, new_name, line_beg, line_end, col_beg, col_end
    ):
        """Get the diff resulting from extracting the selected code"""
        if not hasattr(jedi.Script, "extract_function"):  # pragma: no cover
            return {"success": "Not available"}
        ren = run_with_debug(
            jedi,
            "extract_function",
            code=source,
            path=filename,
            environment=self.environment,
            fun_kwargs={
                "line": line_beg,
                "until_line": line_end,
                "column": col_beg,
                "until_column": col_end,
                "new_name": new_name,
            },
        )
        if ren is None:
            return {"success": False}
        else:
            return {
                "success": True,
                "project_path": ren._inference_state.project._path,
                "diff": ren.get_diff(),
                "changed_files": list(ren.get_changed_files().keys()),
            }

    def rpc_get_inline_diff(self, filename, source, offset):
        """Get the diff resulting from inlining the selected variable"""
        if not hasattr(jedi.Script, "inline"):  # pragma: no cover
            return {"success": "Not available"}
        line, column = pos_to_linecol(source, offset)
        ren = run_with_debug(
            jedi,
            "inline",
            code=source,
            path=filename,
            environment=self.environment,
            fun_kwargs={"line": line, "column": column},
        )
        if ren is None:
            return {"success": False}
        else:
            return {
                "success": True,
                "project_path": ren._inference_state.project._path,
                "diff": ren.get_diff(),
                "changed_files": list(ren.get_changed_files().keys()),
            }

    def rename_identifier(
        self,
        source: str,
        offset: int,
        file_name: str,
        new_identifier_name: str,
    ) -> Optional[refactor_rename_use_case.Refactoring]:
        line, column = pos_to_linecol(source, offset)
        ren = run_with_debug(
            jedi,
            "rename",
            code=source,
            path=file_name,
            environment=self.environment,
            fun_kwargs={
                "line": line,
                "column": column,
                "new_name": new_identifier_name,
            },
        )
        if ren is None:
            return None
        return refactor_rename_use_case.Refactoring(
            changed_files=ren.get_changed_files().keys(),
            diff=ren.get_diff(),
            project_path=ren._inference_state.project._path,
        )

    def can_do_renaming(self) -> bool:
        return hasattr(jedi.Script, "rename")

    def get_completions(
        self, file_name: str, source: str, offset: int
    ) -> Iterable[get_completions_use_case.Completion]:
        line, column = pos_to_linecol(source, offset)
        proposals = run_with_debug(
            jedi,
            "complete",
            code=source,
            path=file_name,
            environment=self.environment,
            fun_kwargs={"line": line, "column": column},
        )
        self.completions = dict((proposal.name, proposal) for proposal in proposals)
        return [
            get_completions_use_case.Completion(
                name=proposal.name.rstrip("="),
                suffix=proposal.complete.rstrip("="),
                annotation=proposal.type,
                description=proposal.description,
            )
            for proposal in proposals
        ]


# From the Jedi documentation:
#
#   line is the current line you want to perform actions on (starting
#   with line #1 as the first line). column represents the current
#   column/indent of the cursor (starting with zero). source_path
#   should be the path of your file in the file system.


def pos_to_linecol(text: str, pos: int) -> Tuple[int, int]:
    """Return a tuple of line and column for offset pos in text.

    Lines are one-based, columns zero-based.

    This is how Jedi wants it. Don't ask me why.

    """
    line_start = text.rfind("\n", 0, pos) + 1
    line = text.count("\n", 0, line_start) + 1
    col = pos - line_start
    return line, col


def linecol_to_pos(text, line, col):
    """Return the offset of this line and column in text.

    Lines are one-based, columns zero-based.

    This is how Jedi wants it. Don't ask me why.

    """
    nth_newline_offset = 0
    for i in range(line - 1):
        new_offset = text.find("\n", nth_newline_offset)
        if new_offset < 0:
            raise ValueError("Text does not have {0} lines.".format(line))
        nth_newline_offset = new_offset + 1
    offset = nth_newline_offset + col
    if offset > len(text):
        raise ValueError("Line {0} column {1} is not within the text".format(line, col))
    return offset


def run_with_debug(jedi, name, fun_kwargs={}, *args, re_raise=(), **kwargs):
    try:
        script = jedi.Script(*args, **kwargs)
        return getattr(script, name)(**fun_kwargs)
    except Exception as e:
        if isinstance(e, re_raise):
            raise
        if isinstance(e, jedi.RefactoringError):
            return None

        debug_info = []

        def _debug(level, str_out):
            if level == debug.NOTICE:
                prefix = "[N]"
            elif level == debug.WARNING:
                prefix = "[W]"
            else:
                prefix = "[?]"
            debug_info.append("{0} {1}".format(prefix, str_out))

        jedi.set_debug_function(_debug, speed=False)
        try:
            script = jedi.Script(*args, **kwargs)
            return getattr(script, name)()
        except Exception as e:
            source = kwargs.get("source")
            sc_args = []
            sc_args.extend(repr(arg) for arg in args)
            sc_args.extend(
                "{0}={1}".format(k, "source" if k == "source" else repr(v))
                for (k, v) in kwargs.items()
            )

            data = {
                "traceback": traceback.format_exc(),
                "jedi_debug_info": {
                    "script_args": ", ".join(sc_args),
                    "source": source,
                    "method": name,
                    "debug_info": debug_info,
                },
            }
            raise rpc.Fault(message=str(e), code=500, data=data)
        finally:
            jedi.set_debug_function(None)


class RefactorRenameOutputPort:
    def __init__(self) -> None:
        self.response: Optional[refactor_rename_use_case.Response] = None

    def present_refactoring(self, response: refactor_rename_use_case.Response) -> None:
        self.response = response

    def get_response(self) -> Dict[str, Any]:
        assert self.response
        changes = self.response.changes
        if changes == refactor_rename_use_case.FailureReason.NOT_AVAILABLE:
            return {"success": "Not available"}
        elif changes == refactor_rename_use_case.FailureReason.NO_RESULT:
            return {"success": False}
        elif isinstance(changes, refactor_rename_use_case.Changes):
            return {
                "success": True,
                "project_path": changes.project_path,
                "diff": changes.diff,
                "changed_files": changes.changed_files,
            }
        else:
            raise Exception()


class GetCompletionsOutputPort:
    def __init__(self) -> None:
        self.response: Optional[get_completions_use_case.Response] = None

    def present_completion(self, response: get_completions_use_case.Response) -> None:
        self.response = response

    def render_completions(self) -> List[Dict[str, str]]:
        assert self.response
        return [
            {
                "name": proposal.name,
                "suffix": proposal.suffix,
                "annotation": proposal.annotation,
                "meta": proposal.description,
            }
            for proposal in self.response.proposals
        ]
