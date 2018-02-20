[![PyPI version](https://img.shields.io/pypi/v/pyfastpfor.svg)](https://pypi.python.org/pypi/pyfastpfor/)
[![Build Status](https://travis-ci.org/searchivarius/PyFastPFor.svg?branch=master)](https://travis-ci.org/searchivarius/PyFastPFor)
# PyFastPFor
Python bindings for the fast integer compression library [FastPFor](https://github.com/lemire/FastPFor): A research library with integer compression schemes. FastPFor is broadly applicable to the compression of arrays of 32-bit integers where most integers are small. The library seeks to exploit SIMD instructions (SSE) whenever possible. This library can decode at least 4 billions of compressed integers per second on most desktop or laptop processors. That is, it can decompress data at a rate of 15 GB/s. This is significantly faster than generic codecs like gzip, LZO, Snappy or LZ4.

# Authors

Daniel Lemire, Leonid Boytsov, Owen Kaser, Maxime Caron, Louis Dionne, Michel Lemay, Erik Kruus, Andrea Bedini, Matthias Petri, Robson Braga Araujo, Patrick Damme. Bindings are created by Leonid Boytsov.

# Installation

Bindings can be installed locally:
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

The library supports all the codecs implemented in the original [FastPFor](https://github.com/lemire/FastPFor) library by Feb 2018) as well as two types of data differencing approaches. The library compresses well only small integers. A common trick to deal with large numbers is to sort them and subsequently to encode the differences. Examples of three common use scenarios (no differencing, coarse and fine deltas) are outlined in [this Python notebook](python_bindings/examples.ipynb). To get a list of codecs, use the function ``getCodecList``.
