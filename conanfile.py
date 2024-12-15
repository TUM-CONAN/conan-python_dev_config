#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conan import ConanFile
from conan.errors import ConanException
from conan.tools.files import save, copy
import os

# pylint: disable=W0201
class PythonDevConfigConan(ConanFile):
    python_requires = "camp_common/[>=0.1]@camposs/stable"
    python_requires_extend = "camp_common.CampPythonBase"

    name = "python_dev_config"
    upstream_version = '1.1'
    package_revision = ''
    version = "{0}{1}".format(upstream_version, package_revision)

    license = "MIT"
    exports = ["LICENSE.md"]
    description = "Configuration of Python interpreter for use as a development dependency."
    url = "https://github.com/ulricheck/conan-python_dev_config"
    author = "Ulrich Eck <ulrich.eck@tum.de"

    settings = "os", "arch"

    options = { 
        "python": ["ANY"],
        "python_version": ["ANY"],
        "with_system_python": [True, False],
    }

    default_options = {
        "python": "python3",
        "python_version": "3.12",
        "with_system_python": False,
    }

    def requirements(self):
        if not self.options.with_system_python:
            self.requires("cpython/[~{}]".format(self.options.python_version), run=True, transitive_headers=True, transitive_libs=True)
            self.requires("python-pip/24.3.1@camposs/stable", run=True)
            self.requires("python-setuptools/75.6.0@camposs/stable", run=True)
            self.requires("cython/3.0.11-1@camposs/stable", run=True)
            self.requires("python-numpy/2.2.0@camposs/stable", run=True)

    def package_id(self):
        self.info.clear()

    def package(self):
        copy(self, "LICENSE.md", self.source_folder, self.package_folder)


    def package_info(self):
        if not self.have_python_dev:
            raise RuntimeError("Python development environment not correctly setup.")

        if self.options.with_system_python:
            self.cpp_info.includedirs = [self._python_include_dir]
            self.cpp_info.libdirs = [os.path.dirname(self._python_lib)]
            self.cpp_info.libs = [self._python_lib_ldname]
            self.cpp_info.bindirs = [os.path.dirname(self._python_lib), os.path.dirname(self._python_exec)]

            python_home = self._python_prefix
            self.buildenv_info.append_path("PYTHONPATH", os.path.join(python_home, "lib", "python%s" % self._python_version))
            self.buildenv_info.define("PYTHONHOME", python_home)
            self.buildenv_info.append_path("PATH", os.path.dirname(self._python_lib))
            self.buildenv_info.append_path("PATH", os.path.dirname(self._python_exec))
            self.buildenv_info.append_path("LD_LIBRARY_PATH", os.path.join(self._python_lib))
        else:
            cpy_dep = self.dependencies["cpython"]
            self.cpp_info.includedirs = cpy_dep.cpp_info.includedirs
            self.cpp_info.libdirs = cpy_dep.cpp_info.libdirs
            self.cpp_info.libs = cpy_dep.cpp_info.libs
            self.cpp_info.bindirs = cpy_dep.cpp_info.bindirs

            self.buildenv_info.append_path("PTYONHOME", cpy_dep.package_folder)
            self.runenv_info.append_path("PTYONHOME", cpy_dep.package_folder)



        self.conf_info.define("tools.python_dev_config:python_version", self._python_version)
        self.conf_info.define_path("tools.python_dev_config:python", self._python_exec)
        self.conf_info.define_path("tools.python_dev_config:python_exec", self._python_exec)
        self.conf_info.define_path("tools.python_dev_config:python_include_dir", self._python_include_dir)
        self.conf_info.define_path("tools.python_dev_config:python_lib_dir", os.path.dirname(self._python_lib))

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
