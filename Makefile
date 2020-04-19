ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

PY_VERSION ?= 3.7
PYTHON ?= $(ROOT_DIR)/venv/bin/python$(PY_VERSION)
PIP ?= $(ROOT_DIR)/venv/bin/pip

CSV_FILES := 1 2 3
CSV_FILES := $(addprefix E_B02_Sequenz_,$(CSV_FILES))
CSV_FILES := $(addsuffix .csv,$(CSV_FILES))
CSV_SOURCES := $(addprefix data/,$(CSV_FILES))
CSV_RESULTS := $(addprefix results/,$(CSV_FILES))

.PHONY: default res install test doc

default: res 
res: $(CSV_RESULTS)

results/%.csv: data/%.csv results/
	$(PYTHON) emotion.py $<

results/:
	mkdir -p $@

install: venv/
	$(PIP) install -r requirements.txt
	cd frontend && npm install

venv/:
	virtualenv -p $(PY_VERSION) venv

test:
	$(PYTHON) -m unittest discover --verbose

NOTEBOOKS := data_preparation/preprocessing.ipynb evaluation.ipynb
doc: 
	pydoc -w dempster_shafer.basic_measure
	pydoc -w emotion
	mv *.html doc/
	 
	for f in $(NOTEBOOKS); \
	do \
		jupyter nbconvert --to html $$f --output-dir=doc ; \
		jupyter nbconvert --to pdf $$f --output-dir=doc ; \
	done
