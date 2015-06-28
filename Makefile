# Some simple testing tasks (sorry, UNIX only).

PYTHON ?= python
FLAKE=pyflakes
PEP=pep8


doc:
	make -C docs html
	echo "open file://`pwd`/docs/_build/html/index.html"

clean:
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
	rm -f `find . -type f -name '*~' `
	rm -f `find . -type f -name '.*~' `
	rm -f `find . -type f -name '@*' `
	rm -f `find . -type f -name '#*#' `
	rm -f `find . -type f -name '*.orig' `
	rm -f `find . -type f -name '*.rej' `
	rm -f .coverage
	rm -rf coverage

check_readme:
	rst2html.py --strict README.rst > /dev/null
	rst2html.py --strict CHANGELOG.rst > /dev/null

publish:
	python setup.py register
	python setup.py sdist upload
	python setup.py bdist_wheel upload
#	python setup.py upload_docs

.PHONY: all doc clean
