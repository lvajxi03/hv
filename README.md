# hv

Simple image viewer, written in Python.

## Installation

To install `hv`, type the following:

```sh
python -m pip install hv
```

## Running

To run `hv`, type the following:

```sh
python -m hv
```

## Custom build

To build `hv`, you need to install `build`, `wheel` and `setuptools`

Then, type the following:

```sh
python -m build -n
```

After successful build you will have `*.whl` file in `dist` subdirectory.

Then you will install this with:

```sh
python -m pip install dist/*.whl
```

## Custom run

To run `hv` without building, you need to have following dependencies installed:

* PySide6
* tomli_w

To run, type the following:

```sh
export PYTHONPATH=pysrc
python -m hv
```
