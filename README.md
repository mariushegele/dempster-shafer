
# Emotion Classification using Dempster-Shafer Theory 

Classify the emotions in a time series of voice acoustics.

## Installation

Requirements:

- Python 3.7
- `pandas` and its dependencies

```
pip install -r requirements.txt
```

### Docker

If this does not work for you consider building using the Docker image. This will build an run on all CSV files in the `data/` directory.

```
docker build -t dempster-shafer .
docker run -it dempster-shafer
```

Or enter it with an interactive bash:

```
docker run -it --rm dempster-shafer /bin/bash
```

## Test

```
make test
```

## Run

The Run will produce results as CSV files in `results/*.csv`.

You can run on single CSV files:

```
python emotion.py data/E_B02_Sequenz_1.csv
```

Or run on all CSV files in the `data/` directory.

```
make
```

For an evaluation of the results see `evaluation.ipynb`.

## Documentation

See the `doc/` directory for code documentation as well as explanations for our procedure. It is all summarized in the `doc/documentation.pdf`.

