import os
import shutil
import subprocess
import sys

import setuptools
from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext

__version__ = '1.3.6'

pcCommand = shutil.which("pkgconf")
if not pcCommand:
    pcCommand = shutil.which("pkg-config")
pcCommand = None


def runPkgConfig(arg, package):
    return subprocess.run([pcCommand, arg, package], capture_output=True).stdout.decode(
        "utf-8"
    )


def getInfoFromPkgConfig(arg, pkgName):
    res = str(runPkgConfig(arg, pkgName))[:-1].split(" ")
    if len(res) == 1 and not res[0]:
        return ()

    return res


def processPkgConfigLibDir(l):
    if l.startswith("-L"):
        l = l[2:]
        return l

    raise ValueError("Wrong lib dir flag", l)


def processPkgConfigIncludeDir(i):
    if i.startswith("-I"):
        i = i[2:]
        return i

    raise ValueError("Wrong include dir flag", i)


def processPkgConfigLib(l):
    if l.startswith("-l"):
        l = l[2:]
        if l.startswith(":"):
            l = l[1:]
        return l

    raise ValueError("Wrong lib flag", l)


def getPcInfo(pkgName):
    if pcCommand:
        extra_compile_args = getInfoFromPkgConfig("-cflags", pkgName)
        include_dirs = [
            processPkgConfigIncludeDir(l)
            for l in getInfoFromPkgConfig("--cflags-only-I", pkgName)
        ]
        libs_dirs = [
            processPkgConfigLibDir(l) for l in getInfoFromPkgConfig("--libs-only-L", pkgName)
        ]
        libraries = [processPkgConfigLib(l) for l in getInfoFromPkgConfig("--libs", pkgName)]
        extra_objects = getInfoFromPkgConfig("--static", pkgName)
    else:
        extra_compile_args = include_dirs = libs_dirs = libraries = extra_objects = ()

    return extra_compile_args, include_dirs, libs_dirs, libraries, extra_objects


extra_compile_args, include_dirs, libs_dirs, libraries, extra_objects = pkgConfigInfo = getPcInfo("fastpfor")

source_files = ["pyfastpfor.cc"]
requirements_list = ["pybind11>=2.4", "numpy"]


if any(pkgConfigInfo):
    pass
else:
    maindir = os.path.join(".", "fastpfor")
    library_file = os.path.join(maindir, "libFastPFor.a")
    extra_compile_args = ()

    extra_objects = []

    if os.path.exists(library_file):
        # if we have a prebuilt library file, use that.
        extra_objects.append(library_file)

    else:
        # Otherwise build all the files here directly (excluding test files)
        exclude_files = set("""unit.cpp codecs.cpp""".split())

        for root, subdirs, files in os.walk(os.path.join(maindir, "src")):
            source_files.extend(
                os.path.join(root, f)
                for f in files
                if (f.endswith(".cc") or f.endswith(".c") or f.endswith(".cpp"))
                and f not in exclude_files
            )
    include_dirs = [maindir, os.path.join(maindir, "headers")]

ext_modules = [
    Extension(
        'pyfastpfor',
        source_files,
        include_dirs=include_dirs,
        libraries=libraries,
        language='c++',
        extra_objects=extra_objects,
        extra_compile_args = extra_compile_args,
    ),
]

# As of Python 3.6, CCompiler has a `has_flag` method.
# cf http://bugs.python.org/issue26689
def has_flag(compiler, flagname):
    """Return a boolean indicating whether a flag name is supported on
    the specified compiler.
    """
    import tempfile
    with tempfile.NamedTemporaryFile('w', suffix='.cpp') as f:
        f.write('int main (int argc, char **argv) { return 0; }')
        try:
            compiler.compile([f.name], extra_postargs=[flagname])
        except setuptools.distutils.errors.CompileError:
            return False
    return True


def cpp_flag(compiler):
    """Return the -std=c++[11/14] compiler flag.

    #The c++14 is prefered over c++11 (when it is available).
    # This somehow can fail on a Mac with clang
    #"""
    #if has_flag(compiler, '-std=c++14'):
        #return '-std=c++14'
    #elif has_flag(compiler, '-std=c++11'):
    if has_flag(compiler, '-std=c++11'):
        return '-std=c++11'
    else:
        raise RuntimeError('Unsupported compiler -- at least C++11 support '
                           'is needed!')


class BuildExt(build_ext):
    """A custom build extension for adding compiler-specific options."""
    c_opts = {
        'msvc': ['/EHsc', '/openmp', '/O2'],
        'unix': ['-O3', '-march=native', '-std=c99'],
        #'unix': ['-O0', '-march=native', '-g'],
    }
    link_opts = {
        'unix': [],
        'msvc': [],
    }

    if sys.platform == 'darwin':
        c_opts['unix'] += ['-stdlib=libc++', '-mmacosx-version-min=10.7']
        link_opts['unix'] += ['-stdlib=libc++', '-mmacosx-version-min=10.7']
    else:
        c_opts['unix'].append("-fopenmp")
        link_opts['unix'].extend(['-fopenmp', '-pthread'])

    def build_extensions(self):
        ct = self.compiler.compiler_type
        opts = self.c_opts.get(ct, [])
        if ct == 'unix':
            opts.append('-DVERSION_INFO="%s"' % self.distribution.get_version())
            opts.append(cpp_flag(self.compiler))
            if has_flag(self.compiler, '-fvisibility=hidden'):
                opts.append('-fvisibility=hidden')
        elif ct == 'msvc':
            opts.append('/DVERSION_INFO=\\"%s\\"' % self.distribution.get_version())

        # extend include dirs here (don't assume numpy/pybind11 are installed when first run, since
        # pip could have installed them as part of executing this script
        import pybind11
        import numpy as np
        for ext in self.extensions:
            ext.extra_compile_args.extend(opts)
            ext.extra_link_args.extend(self.link_opts.get(ct, []))
            ext.include_dirs.extend([
                # Path to pybind11 headers
                pybind11.get_include(),
                pybind11.get_include(True),

                # Path to numpy headers
                np.get_include()
            ])

        build_ext.build_extensions(self)


setup(
    name='pyfastpfor',
    version=__version__,
    description='Python bindings for the FastPFor library (fast integer compression)',
    author='Lemire et al. for FastPFor',
    url='https://github.com/searchivarius/PyFastPFor',
    long_description="""Pythong bindings for FastPFor: A research library with integer compression schemes. FastPFor is broadly applicable to the compression of arrays of 32-bit integers where most integers are small. The library seeks to exploit SIMD instructions (SSE) whenever possible. This library can decode at least 4 billions of compressed integers per second on most desktop or laptop processors. That is, it can decompress data at a rate of 15 GB/s. This is significantly faster than generic codecs like gzip, LZO, Snappy or LZ4.""",
    ext_modules=ext_modules,
    install_requires=requirements_list,
    setup_requires=requirements_list,
    cmdclass={'build_ext': BuildExt},
    test_suite="tests",
    zip_safe=False,
)
