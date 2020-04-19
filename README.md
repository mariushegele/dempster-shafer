
# Emotion Classification using Dempster-Shafer Theory 

Classify the emotions in a time series of voice acoustics.

## Installation

Requirements:
	
- `virtualenv`
- `pandas` and its dependencies

The notebooks we produced for analysis might have some further optional requirements, that are not required to run.

The following target will create a virtual environment and install all requirements into it.
This will probably not work on a Windows machine.

```
make install
```

## Test

```
make test
```

## Run

The Run will produce results as CSV files in `results/*.csv`.

```
venv/bin/python emotion.py data/E_B02_Sequenz_1.csv
```

Run on all CSV files in the `data/` directory.

```
make
```

For an evaluation of the results see `evaluation.ipynb`.

## Documentation

See the `doc/` directory for code documentation as well as explanations for our procedure. It is all summarized in the `doc/documentation.pdf`.

