#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "fr24[cli]",
# ]
# [tool.uv.sources]
# fr24 = { path = "../", editable = true }
# ///
from __future__ import annotations

import io
import logging
import os
from collections.abc import Generator
from contextlib import redirect_stdout
from pathlib import Path

import click
from typer.main import get_command

from fr24.cli import app

logger = logging.getLogger(__name__)


def process_command(
    command: click.Command, parent_context: list[str]
) -> Generator[str, None, None]:
    command_path = " ".join(parent_context)
    logger.info(f"`{command_path} --help`")
    string_io = io.StringIO()
    with redirect_stdout(string_io):
        command.main(
            ["--help"],
            prog_name=parent_context[0],
            standalone_mode=False,
        )
    help_text = string_io.getvalue().strip().replace("\\[", "[")
    ident = command_path.replace(" ", "_")
    yield f"""--8<-- [start:{ident}]
$ {command_path} --help

{help_text}
--8<-- [end:{ident}]
"""
    if not isinstance(command, click.Group):
        return
    for subcommand_name, subcommand in command.commands.items():
        yield from process_command(
            subcommand, [*parent_context, subcommand_name]
        )


def main() -> None:
    os.environ["COLUMNS"] = "80"
    app.rich_markup_mode = None
    path_docs = Path(__file__).parent.parent / "docs"
    output_path = path_docs / "usage" / "cli_output.txt"
    with output_path.open("w") as f:
        f.writelines(process_command(get_command(app), ["fr24"]))


if __name__ == "__main__":
    main()
