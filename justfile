ruff_sources := "src tests scripts docs/usage/scripts"
ruff_format_sources := "src tests scripts docs"

check:
    uv run ruff check {{ruff_sources}}
    uv run ruff format --check {{ruff_format_sources}}
    uv run --script scripts/check_signature.py
    uv run --extra polars mypy src tests docs/usage/scripts --exclude 'cli.py'

fmt:
    uv run ruff check {{ruff_sources}} --fix
    uv run ruff format {{ruff_format_sources}}
    uv run --script scripts/check_signature.py

compile_proto:
    uv run --script scripts/compile_proto.py
