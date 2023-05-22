#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conan import ConanFile
from conan.errors import ConanException
from conan.tools.files import save, copy

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO
import os
import re


# pylint: disable=W0201
class PythonDevConfigConan(ConanFile):
    python_requires = "camp_common/0.5@camposs/stable"
    python_requires_extend = "camp_common.CampPythonBase"

    name = "python_dev_config"
    version = "0.6"
    package_type = "shared-library"

    license = "MIT"
    exports = ["LICENSE.md"]
    description = "Configuration of Python interpreter for use as a development dependency."
    url = "https://github.com/ulricheck/conan-python_dev_config"

    settings = "os", "arch"

    options = { 
        "python": ["ANY"],
        "with_system_python": [True, False],
    }

    default_options = {
        "with_system_python": True,
        "python": "python3",
    }

    def build_requirements(self):
        if not self.options.with_system_python:
            self.requires("cpython/3.10.0")

    def requirements(self):
        if not self.options.with_system_python:
            self.requires("python-setuptools/41.2.0@camposs/stable")
            self.requires("python-pip/[>=19.2.3]@camposs/stable")
            self.requires("cython/0.29.16@camposs/stable")
            self.requires("python-numpy/1.18.4@camposs/stable")

    def package_id(self):
        self.info.clear()

    def package(self):
        copy(self, "LICENSE.md", self.source_folder, self.package_folder)

    def package_info(self):
        if not self.have_python_dev:
            raise Exception("Python development environment not correctly setup.")

        self.output.info("Set IncludeDir: %s" % self._python_include_dir)
        self.cpp_info.includedirs = [self._python_include_dir]
        self.output.info("Set LibDir: %s" % self._python_lib)
        self.cpp_info.libdirs = [os.path.dirname(self._python_lib)]
        self.output.info("Set Lib: %s" % self._python_lib)
        self.cpp_info.libs = [self._python_lib_ldname]
        self.cpp_info.bindirs = [os.path.dirname(self._python_lib), os.path.dirname(self._python_exec)]

        self.output.info("Set Env PYTHON_VERSION: %s" % self._python_version)
        self.user_info.PYTHON_VERSION = self._python_version
        self.output.info("Set Env PYTHON: %s" % self._python_exec)
        self.user_info.PYTHON = self._python_exec

        self.output.info("Append Env PYTHONPATH: %s" % self._python_stdlib)
        self.env_info.PYTHONPATH.append(self._python_stdlib)
        self.output.info("Set Env PYTHONHOME: %s" % self._python_prefix)
        self.env_info.PYTHONHOME = self._python_prefix
        

        self.output.info("Append Env PATH: %s" % os.path.dirname(self._python_lib))
        self.env_info.PATH.append(os.path.dirname(self._python_lib))
        self.output.info("Append Env PATH: %s" % os.path.dirname(self._python_exec))
        self.env_info.PATH.append(os.path.dirname(self._python_exec))
        self.output.info("Append Env LD_LIBRARY_PATH: %s" % os.path.dirname(self._python_lib))
        self.env_info.LD_LIBRARY_PATH.append(os.path.join(self._python_lib))

        self.user_info.PYTHON_EXEC = self._python_exec
        self.user_info.PYTHON_INCLUDE_DIR = self._python_include_dir
        self.user_info.PYTHON_LIB_DIR = os.path.dirname(self._python_lib)

    @property
    def have_python_dev(self):
        if not self._python_exec:
            return False
        if not self._python_include_dir:
            return False
        if not self._python_lib:
            return False
        if not os.path.exists(os.path.join(self._python_include_dir, 'Python.h')):
            return False
        return True
