#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, tools
try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO
import os
import re


# pylint: disable=W0201
class PythonDevConfigConan(ConanFile):
    python_requires = "camp_common/0.1@camposs/stable"
    python_requires_extend = "camp_common.CampPythonBase"

    name = "python_dev_config"
    upstream_version = '1.0'
    package_revision = ''
    version = "{0}{1}".format(upstream_version, package_revision)

    license = "MIT"
    exports = ["LICENSE.md"]
    description = "Configuration of Python interpreter for use as a development dependency."
    url = "https://github.com/ulricheck/conan-python_dev_config"
    author = "Ulrich Eck <ulrich.eck@tum.de"

    settings = "os", "arch"

    options = { 
        "python": "ANY",
        "with_system_python": [True, False],
    }

    default_options = {
        "with_system_python": True,
        "python": "python.exe" if tools.os_info.is_windows else "python3",
    }

    def build_requirements(self):
        if not self.options.with_system_python:
            self.requires("python/3.8.11@camposs/stable")

    def requirements(self):
        if not self.options.with_system_python:
            # self.requires("python/3.8.11@camposs/stable")
            self.requires("python-setuptools/41.2.0@camposs/stable")
            self.requires("python-pip/[>=19.2.3]@camposs/stable")
            self.requires("cython/0.29.16@camposs/stable")
            self.requires("python-numpy/1.18.4@camposs/stable")

    def package(self):
        self.copy("LICENSE.md", dst="doc")


    def package_info(self):
        if not self.have_python_dev:
            raise RuntimeError("Python development environment not correctly setup.")

        self.cpp_info.includedirs = [self._python_include_dir]
        self.cpp_info.libdirs = [os.path.dirname(self._python_lib)]
        self.cpp_info.libs = [self._python_lib_ldname]
        self.cpp_info.bindirs = [os.path.dirname(self._python_lib), os.path.dirname(self._python_exec)]

        self.user_info.PYTHON_VERSION = self._python_version
        self.user_info.PYTHON = self._python_exec
        python_home = self._python_prefix
        self.env_info.PYTHONPATH.append(os.path.join(python_home, "lib", "python%s" % self._python_version))
        self.env_info.PYTHONHOME = python_home
        self.env_info.PATH.append(os.path.dirname(self._python_lib))
        self.env_info.PATH.append(os.path.dirname(self._python_exec))
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
