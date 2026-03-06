check:
    uv run ruff check src tests
    uv run ruff format --check src tests
    uv run --extra polars mypy src tests docs/usage/scripts

fmt:
    uv run ruff check src tests --fix
    uv run ruff format src tests
    uv run --script scripts/check_signature.py

compile_proto:
    uv run --script scripts/compile_proto.py