[![PyPI version](https://img.shields.io/pypi/v/pyfastpfor.svg)](https://pypi.python.org/pypi/pyfastpfor/)
[![Build Status](https://travis-ci.org/searchivarius/PyFastPFor.svg?branch=master)](https://travis-ci.org/searchivarius/PyFastPFor)
# PyFastPFor
Python bindings for the fast integer compression library [FastPFor](https://github.com/lemire/FastPFor). Can be installed locally:
```
cd python_bindings
sudo setup.py build install
```
or via pip:
```
pip install pyfastpfor
```
Due to some compilation quirks this currently seem to work with GCC only. I will fix it in some not so distant future.

# Documentation
The library supports all the codes as the original [FastPFor](https://github.com/lemire/FastPFor) library as well as two types of data differencing approaches. The library compresses well only small integers. A common trick to deal with large numbers is to sort them and subsequently to encode the differences. Examples of three common use scenarios are outlined in [this Python notebook](python_bindings/examples.ipynb).
