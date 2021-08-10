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
    name = "python_dev_config"
    version = "0.6"
    license = "MIT"
    exports = ["LICENSE.md"]
    description = "Configuration of Python interpreter for use as a development dependency."
    url = "https://github.com/ulricheck/conan-python_dev_config"
    author = "Bincrafters <bincrafters@gmail.com>"

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

    # def package_id(self):
    #     del self.info.settings.arch

    def package_info(self):
        if not self.have_python_dev:
            raise Exception("Python development environment not correctly setup.")

        self.cpp_info.includedirs = [self.python_include]
        self.cpp_info.libdirs = [os.path.dirname(self.python_lib)]
        self.cpp_info.libs = [self.python_lib_ldname]
        self.cpp_info.bindirs = [os.path.dirname(self.python_lib), os.path.dirname(self.python_exec)]

        self.user_info.PYTHON_VERSION = self.python_version
        self.user_info.PYTHON = self.python_exec
        majmin_ver = ".".join(self.version.split(".")[:2])
        python_home = os.path.dirname(os.path.dirname(self.python_exec))
        self.env_info.PYTHONPATH.append(os.path.join(python_home, "lib", "python%s" % majmin_ver))
        self.env_info.PYTHONHOME = python_home
        self.env_info.PATH.append(os.path.dirname(self.python_lib))
        self.env_info.PATH.append(os.path.dirname(self.python_exec))
        self.env_info.LD_LIBRARY_PATH.append(os.path.join(self.python_lib))

        self.user_info.PYTHON_EXEC = self.python_exec
        self.user_info.PYTHON_INCLUDE_DIR = self.python_include
        self.user_info.PYTHON_LIB_DIR = os.path.dirname(self.python_lib)

    @property
    def have_python_dev(self):
        if not self.python_exec:
            return False
        if not self.python_include:
            return False
        if not self.python_lib:
            return False
        if not os.path.exists(os.path.join(self.python_include, 'Python.h')):
            return False
        return True

    @property
    def python_exec(self):
        if not hasattr(self, '_py_exec'):
            pyexec = str(self.options.python)
            if not self.options.with_system_python:
                pyexec = self.deps_env_info["python"].PYTHON

            output = StringIO()
            try:
                self.run('{0} -c "import sys; print(sys.executable)"'.format(pyexec), output=output, run_environment=True)
                self._py_exec = output.getvalue().strip()
            except:
                self.output.error(output.getvalue())
                raise Exception("Error running python at path provided: %s" % (str(self.options.python)))

        return self._py_exec

    @property
    def python_version(self):
        if not hasattr(self, '_py_version'):
            cmd = "from sys import *; print('{0}.{1}'.format(version_info[0],version_info[1]))"
            self._py_version = self.run_python_command(cmd)
        return self._py_version

    @property
    def python_version_nodot(self):
        if not hasattr(self, '_py_version_nodot'):
            cmd = "from sys import *; print('{0}{1}'.format(version_info[0],version_info[1]))"
            self._py_version_nodot = self.run_python_command(cmd)
        return self._py_version_nodot

    @property
    def python_lib(self):
        if not hasattr(self, '_py_lib'):
            if self.settings.os == "Windows" and not self.settings.os.subsystem:
                self._py_lib = self.get_python_path("stdlib")
                if self._py_lib:
                    self._py_lib = os.path.join(os.path.dirname(self._py_lib), "libs", "python" + self.python_version_nodot + ".lib")
            elif self.settings.os == "Macos":
                self._py_lib = os.path.join(self.get_python_var('LIBDIR'), self.get_python_var('LIBRARY'))
            else:
                self._py_lib = os.path.join(self.get_python_var('LIBDIR'), self.get_python_var('LDLIBRARY'))
        return self._py_lib
    
    @property
    def python_lib_ldname(self):
        if not hasattr(self, '_py_lib_ldname'):
            if self.settings.os == "Windows" and not self.settings.os.subsystem:
                self._py_lib_ldname = os.path.basename(self.python_lib)
            else:
                self._py_lib_ldname = re.sub(r'lib', '', os.path.splitext(os.path.basename(self.python_lib))[0])
        return self._py_lib_ldname

    @property
    def python_bindir(self):
        if not hasattr(self, '_py_bindir'):
            self._py_bindir = self.get_python_var('BINDIR')
        return self._py_bindir

    @property
    def python_include(self):
        if not hasattr(self, '_py_include'):
            self._py_include = None
            for py_include in [self.get_python_path("include"), self.get_python_var('INCLUDEPY')]:
                if not self._py_include and py_include:
                    if os.path.exists(os.path.join(py_include, 'pyconfig.h')):
                        self._py_include = py_include
        return self._py_include

    def get_python_var(self, var_name):
        cmd = "import sysconfig; print(sysconfig.get_config_var('{0}'))".format(var_name)
        return self.run_python_command(cmd)

    def get_python_path(self, dir_name):
        cmd = "import sysconfig; print(sysconfig.get_path('{0}'))".format(dir_name)
        return self.run_python_command(cmd)

    def run_python_command(self, cmd):
        pyexec = self.python_exec
        if pyexec:
            output = StringIO()
            self.output.info('running command: "{0}" -c "{1}"'.format(pyexec, cmd))
            self.run('"{0}" -c "{1}"'.format(pyexec, cmd), output=output, run_environment=True)
            result = output.getvalue().strip()
        else:
            result = ""
        return result if result and result != "" else None
