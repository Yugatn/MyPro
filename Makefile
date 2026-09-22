.PHONY: install test demo lint typecheck clean
install:
	pip install -e ".[dev]"
test:
	pytest -q
demo:
	python demo.py /tmp/mypro-demo
lint:
	ruff check core tests cli.py demo.py
typecheck:
	mypy core --ignore-missing-imports
clean:
	rm -rf /tmp/mypro-demo
