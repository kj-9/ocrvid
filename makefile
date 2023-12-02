.PHONY: install
install:
	pip install -e '.[test,dev]'

.PHONY: pre-commit
pre-commit:
	pre-commit run -a

.PHONY: pre-commit-update
pre-commit-update:
	pre-commit autoupdate

.PHONY: test
test:
	pytest --log-cli-level=INFO --capture=tee-sys
