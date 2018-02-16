/**
 * PyFastPFOR
 *
 * Python bindings for the FastPFOR library:
 * https://github.com/lemire/FastPFor 
 *
 * This code is released under the
 * Apache License Version 2.0 http://www.apache.org/licenses/.
 *
 */

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>

namespace py = pybind11;

const char * module_name = "pyfastpfor";

/* 
 * PYBIND11_MODULE is a replacement for PYBIND11_PLUGIN 
 * introduced in Pybind 2.2. However, we don't require
 * Pybind to be >= 2.0 so we attempt to support older 
 * Pybind versions as well.
 */
#ifdef PYBIND11_MODULE
PYBIND11_MODULE(nmslib, m) {
  m.doc() = "Python Bindings for FastPFor library (fast integer compression).";
#else
PYBIND11_PLUGIN(nmslib) {
  py::module m(module_name, "Python Bindings for FastPFor library (fast integer compression).");
#endif

#ifdef VERSION_INFO
    m.attr("__version__") = VERSION_INFO;
#else
    m.attr("__version__") = "dev";
#endif

#ifndef PYBIND11_MODULE
  return m.ptr();
#endif
}

