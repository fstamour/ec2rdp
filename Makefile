
VERSION := $(shell cat version.txt)
BDIST_DEP=dist/ec2rdp-$(VERSION)-py2.py3-none-any.whl

.PHONY: all required readme dist install-local install test uninstall clean

all: required readme dist install test

required:
	pip install --upgrade -r requirements/make.txt

README.html: required README.rst
readme: README.html
	rst2html.py README.rst README.html

dist: $(BDIST_DEP)
$(BDIST_DEP): readme
	python setup.py bdist_wheel --universal

install-local:
	pip install -e .

install: dist
	pip install --upgrade $(BDIST_DEP)
	ec2rdp -h

test: required install
	coverage run --source ec2rdp --omit=*test* --branch -m pytest ec2rdp/test
	coverage html --fail-under=100

uninstall:
	-pip uninstall -y ec2rdp

clean:
	-find . -type f -name *.pyc -delete
	-rm -rf .pytest_cache
	-rm -rf ec2rdp.egg-info
	-rm -rf build
	-rm -rf dist
	-rm -rf htmlcov
	-rm -rf .coverage
	-rm -rf README.html
