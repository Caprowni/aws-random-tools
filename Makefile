.PHONY: test
test:
	@echo "====TEST===="
	mkdir ./test

python_install:
	@echo "===PYTHON CHECK==="
	pip install --upgrade setuptools wheel
	pip install --upgrade pycodestyle pyflakes

python_run:
	@echo "===PYTHON TESTS==="
	pytest -v tests/*
