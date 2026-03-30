SHELL := /bin/bash
PY := .venv/bin/python

.PHONY: help
help:
	@echo "Targets:"
	@echo "  test        - run pytest (quiet)"
	@echo "  test-verbose- run pytest (verbose)"
	@echo "  pytest-ver  - show pytest version"
	@echo "  land        - run PetCare land pack"
	@echo "  audit-verify- run audit verification script"

.PHONY: pytest-ver
pytest-ver:
	@$(PY) -m pytest --version

.PHONY: test
test:
	@$(PY) -m pytest -q

.PHONY: test-verbose
test-verbose:
	@$(PY) -m pytest

.PHONY: land
land:
	@bash scripts/petcare_land_pack.sh

.PHONY: audit-verify
audit-verify:
	@$(PY) scripts/petcare_audit_verify.py
