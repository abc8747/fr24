fmt:
    uv run --python 3.9 ruff check src tests
    uv run --python 3.9 ruff format --check src tests
    uv run --python 3.9 mypy src tests docs/usage/scripts

check:
    uv run --python 3.9 ruff check src tests --fix
    uv run --python 3.9 ruff format src tests
    uv run --script scripts/check_signature.py

compile_proto:
    uv run --script scripts/compile_proto.py