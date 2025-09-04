#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "griffe>=1.11.2",
#     "typing-extensions",
# ]
# ///
from __future__ import annotations

import ast
import logging
import sys
from pathlib import Path
from typing import Any, Generator

import griffe
from griffe._internal.extensions.dataclasses import _set_dataclass_init
from typing_extensions import TypeAlias

logger = griffe.get_logger(__name__)

DataclassPath: TypeAlias = str
"""The canonical path of a dataclass."""


class FR24CheckSignatureExtension(griffe.Extension):
    def __init__(
        self,
        decorator_path: str = "fr24.utils.static_check_signature",
    ) -> None:
        super().__init__()
        self.decorator_path = decorator_path
        self.methods_to_check: dict[griffe.Function, DataclassPath] = {}
        self.method_signature_issues = 0

    def on_function_instance(
        self,
        *,
        node: ast.AST | griffe.ObjectNode,
        func: griffe.Function,
        agent: griffe.Visitor | griffe.Inspector,
        **kwargs: Any,
    ) -> None:
        dataclass_path: DataclassPath | None = None
        for decorator in func.decorators:
            if decorator.callable_path == self.decorator_path:
                args = decorator.value
                assert isinstance(args, griffe.ExprCall)
                dataclass_name = args.arguments[0]
                assert (
                    isinstance(dataclass_name, griffe.ExprName)
                    and len(args.arguments) == 1
                )
                dataclass_path = dataclass_name.canonical_path
                break
        if dataclass_path is not None:
            self.methods_to_check[func] = dataclass_path

    def on_package_loaded(
        self, *, pkg: griffe.Module, loader: griffe.GriffeLoader, **kwargs: Any
    ) -> None:
        self.method_signature_issues = 0
        for func, dataclass_path in self.methods_to_check.items():
            self.method_signature_issues += len(
                collect_issues(loader.modules_collection, func, dataclass_path)
            )


def cleandoc(text: str) -> str:
    # similar to inspect.cleandoc, but more aggressive
    return " ".join(part.strip() for part in text.split("\n"))


def collect_issues(
    modules_collection: griffe.ModulesCollection,
    method: griffe.Function,
    dataclass_path: DataclassPath,
) -> list[str]:
    method_params = method.parameters
    spec_dataclass = modules_collection[dataclass_path]
    _set_dataclass_init(spec_dataclass)
    param_docs = {}
    if method.docstring:
        parsed_sections = method.docstring.parse(griffe.Parser.sphinx)
        for section in parsed_sections:
            if section.kind == griffe.DocstringSectionKind.parameters:
                for param in section.value:
                    param_docs[param.name] = cleandoc(param.description)
    issues = []
    klass_init: griffe.Function = spec_dataclass["__init__"]
    dataclass_params = klass_init.parameters._params
    for i, (method_arg, dataclass_field) in enumerate(
        zip(method_params, dataclass_params)
    ):
        if method_arg != dataclass_field:
            issues.append(
                f"argument {i} `{method_arg.name}`: name or kind mismatch\n"
                f"    expected `{dataclass_field}`\n"
                f"         got `{method_arg}`"
            )

        method_param_doc = param_docs.get(method_arg.name, None)
        dataclass_field_doc = (
            cleandoc(d.value) if (d := dataclass_field.docstring) else None
        )
        if method_param_doc != dataclass_field_doc:
            issues.append(
                f"argument {i} `{method_arg.name}`: docstring mismatch\n"
                f"    expected `{dataclass_field_doc}`\n"
                f"         got `{method_param_doc}`"
            )
    if issues:
        path = f"({method.relative_filepath}:{method.lineno})"
        s = "s" if len(issues) > 1 else ""
        err_str = (
            f"{len(issues)} issue{s} in `{method.canonical_path}` {path}:\n"
            + "\n".join(f"  - {issue}" for issue in issues)
            + "\n= help: update it to something like:\n```py\n"
            + "".join(gen_sphinx_signature(method, dataclass_params))
            + "\n```"
        )
        logger.warning(err_str)
    return issues


def gen_sphinx_signature(
    method: griffe.Function, dataclass_parameters: list[griffe.Parameter]
) -> Generator[str, None, None]:
    if "async" in method.labels:
        yield "async "
    yield f"def {method.path.split('.')[-1]}("
    n_args = len(dataclass_parameters)
    for i, field in enumerate(dataclass_parameters):
        yield field.name
        if field.annotation is not None:
            yield f": {field.annotation}"
        if field.default is not None:
            yield f" = {field.default}"
        if i < n_args - 1:
            yield ", "
    yield ")"
    if (return_annotation := method.returns) is not None:
        yield f" -> {return_annotation}"
    yield ":"

    doc_lines = []
    for param in dataclass_parameters:
        if param.docstring:
            doc_lines.append(f":param {param.name}: {param.docstring.value}")
    if doc_lines:
        yield '\n    """'
        for doc_line in doc_lines:
            yield f"\n    {doc_line}"
        yield '\n    """'


def main() -> None:
    """Check for signature issues in service methods."""
    checker = FR24CheckSignatureExtension()
    extensions = griffe.load_extensions(checker)
    griffe.load(
        "fr24",
        extensions=extensions,
        search_paths=[Path(__file__).parent.parent / "src"],
    )
    if err := checker.method_signature_issues:
        logger.error(f"found {err} signature issues{'s' if err > 1 else ''}")
        sys.exit(1)
    else:
        n_methods = len(checker.methods_to_check)
        logger.info(
            f"success: no signature issues found in {n_methods} methods."
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
