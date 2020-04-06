ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

PY_VERSION ?= 3.7
PYTHON ?= $(ROOT_DIR)/venv/bin/python$(PY_VERSION)
PIP ?= $(ROOT_DIR)/venv/bin/pip

default: test

.PHONY: install test

install: venv/
	$(PIP) install -r requirements.txt
	cd frontend && npm install

venv/:
	virtualenv -p $(PY_VERSION) venv

test:
	$(PYTHON) -m unittest discover
