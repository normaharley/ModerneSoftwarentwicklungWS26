.PHONY: check fix

# Führt alle Prüfungen aus, die auch die CI-Pipeline ausführt
check:
	uv run ruff check .
	uv run ruff format --check .
	uv run pytest

# Behebt Lint-Fehler automatisch und formatiert den Code
fix:
	uv run ruff check --fix .
	uv run ruff format .
