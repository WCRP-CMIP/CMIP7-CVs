# Makefile to help automate key steps

.DEFAULT_GOAL := help
# Will likely fail on Windows, but Makefiles are in general not Windows
# compatible so we're not too worried
TEMP_FILE := $(shell mktemp)

# A helper script to get short descriptions of each target in the Makefile
define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([\$$\(\)a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-30s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT


help:  ## print short description of each target
	@python3 -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)


.PHONY: pre-commit
pre-commit:  ## run pre-commit on all files in the repository
	uv run pre-commit run --all-files

.PHONY: tests
tests:  ## run the test suite
	uv run pytest

.PHONY: virtual-environment
virtual-environment:  ## update virtual environment, create a new one if it doesn't already exist
	uv sync
	uv run pre-commit install
