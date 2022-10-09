
.PHONY: docs

init:
	pip install -r requirements.txt

format:
	poetry run black .

test:
	# This runs all of the tests. To run an individual test, run py.test with
	# the -k flag, like "py.test -k test_path_is_not_double_encoded"
	poetry run pytest tests

lint:
	poetry run flake8 moonreader_tools

coverage:
	poetry run pytest --verbose --cov-report term --cov=moonreader_tools tests

publish:
	rm -rf build dist
	poetry run build && poetry run publish
