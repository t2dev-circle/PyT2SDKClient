from distutils.core import setup, Extension
from Cython.Build import cythonize

ext = Extension(name="_py_t2sdk_api",
                libraries=["t2sdk"],
                sources=["python_api_wrap.cxx", "t2api.cpp"],
                language="c++")

setup(name="py_t2sdk_api",
      version="1.0",
      description="python wrapper of t2sdk",
      py_modules="py_t2sdk_api",
      ext_modules=cythonize(ext))
