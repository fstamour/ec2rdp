
VERSION := $(shell cat version.txt)
BDIST_DEP=dist/ec2rdp-$(VERSION)-py2.py3-none-any.whl

.PHONY: all local build install uninstall clean test deploy \
		pytest

all: build install test deploy

local:
	pip install -e .

build: $(BDIST_DEP)
$(BDIST_DEP):
	python setup.py bdist_wheel --universal
	-rm -rf build

install: build
	cd dist && pip install --upgrade ec2rdp-$(VERSION)-py2.py3-none-any.whl

deploy: build

test: install
	pip install pytest pytest-mock coverage
	coverage run --source ec2rdp --omit=*test* --branch -m pytest ec2rdp/test
	coverage html --fail-under=100

uninstall:
	-pip uninstall -y ec2rdp

clean: uninstall
	-find . -type f -name *.pyc -delete
	-rm -rf .pytest_cache
	-rm -rf ec2rdp.egg-info
	-rm -rf build
	-rm -rf dist
	-rm -rf htmlcov
	-rm -rf .coverage
