#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "griffe>=1.11.2",
#     "typing-extensions",
#     "typer"
# ]
# ///
from __future__ import annotations

import logging
import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

import typer
from rich.logging import RichHandler

logging.basicConfig(
    level="INFO", format="%(message)s", datefmt="[%X]", handlers=[RichHandler()]
)
logger = logging.getLogger(__name__)
app = typer.Typer(pretty_exceptions_show_locals=False, no_args_is_help=True)

PATH_ROOT = Path(__file__).parent.parent.resolve()

check_signature: Callable[[], None] | None = None
try:
    from check_signature import main as check_signature
except ImportError:
    logger.warning(
        "failed to import `griffe`. Command for signature checking will be "
        "unavailable."
    )
if check_signature is not None:
    app.command(name="check-signature")(check_signature)


@app.command()
def check() -> None:
    os.system("uv run --python 3.9 ruff check src tests")
    os.system("uv run --python 3.9 ruff format --check src tests")
    os.system(
        "uv run --python 3.9 mypy src tests docs/usage/scripts --exclude cli.py"
    )
    if check_signature is not None:
        check_signature()


@app.command()
def fix() -> None:
    os.system("uv run --python 3.9 ruff check src tests --fix")
    os.system("uv run --python 3.9 ruff format src tests")


@app.command()
def compile_proto() -> None:
    """Compile protobuf into `.py` and `.pyi` files."""
    result = subprocess.run(
        ["protoc", "--version"], capture_output=True, text=True, check=True
    )
    protoc_version = result.stdout.strip()
    expected_version = "libprotoc 28.2"
    if protoc_version != expected_version:
        logger.error(
            f"expected `protoc=={expected_version}`, got {protoc_version}"
        )
        sys.exit(1)

    path_mypy_protobuf = PATH_ROOT / ".venv" / "bin" / "protoc-gen-mypy"
    if not path_mypy_protobuf.exists():
        logger.error(f"expected `protoc-gen-mypy` at {path_mypy_protobuf}")
        sys.exit(1)
    path_proto = PATH_ROOT / "src" / "fr24" / "proto"
    proto_files = list(path_proto.glob("*.proto"))

    # NOTE: because protobuf does not support relative imports (https://github.com/protocolbuffers/protobuf/issues/1491)
    # we are forcing the exported package to be `fr24.proto.*`
    # workaround: https://grpc.io/docs/languages/python/basics/#generating-grpc-interfaces-with-custom-package-path
    cmd = [
        "protoc",
        f"--plugin={path_mypy_protobuf}",
        f"-Ifr24/proto={path_proto}",
        "--python_out=src",
        "--mypy_out=readable_stubs:src",
    ] + [str(f) for f in proto_files]
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    app()
