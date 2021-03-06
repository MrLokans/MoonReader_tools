
.PHONY: docs

init:
	pip install -r requirements.txt

format:
	black .

test:
	# This runs all of the tests. To run an individual test, run py.test with
	# the -k flag, like "py.test -k test_path_is_not_double_encoded"
	py.test tests

coverage:
	py.test --verbose --cov-report term --cov=moonreader_tools tests

ci: init
	py.test --junitxml=junit.xml


publish:
	rm -rf build dist
	@python setup.py sdist bdist_wheel
	@twine upload dist/*
	rm -rf build dist .egg moonreader_tools.egg-info
