#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile
try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO
import os
import re


# pylint: disable=W0201
class PythonDevConfigConan(ConanFile):
    name = "python_dev_config"
    version = "0.5"
    license = "MIT"
    export = ["LICENSE.md"]
    description = "Configuration of Python interpreter for use as a development dependency."
    url = "https://github.com/bincrafters/conan-python_dev_config"
    author = "Bincrafters <bincrafters@gmail.com>"
    options = { "python": "ANY" }
    default_options = "python=python"
    settings = "os", "arch"
    build_policy = "missing"

    def package_id(self):
        self.info.header_only()
        self.info.options.python_version = self.python_version

    def package_info(self):
        if self.have_python_dev:
            self.cpp_info.includedirs = [self.python_include]
            self.cpp_info.libdirs = [os.path.dirname(self.python_lib)]
            self.cpp_info.libs = [self.python_lib_ldname]
            self.cpp_info.bindirs = [os.path.dirname(self.python_lib), os.path.dirname(self.python_exec)]
            self.user_info.python_version = self.python_version
            self.user_info.python_exec = self.python_exec
            self.user_info.python_include_dir = self.python_include
            self.user_info.python_lib_dir = os.path.dirname(self.python_lib)
            self.env_info.path.append(os.path.dirname(self.python_lib))
            self.env_info.path.append(os.path.dirname(self.python_exec))

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
            try:
                pyexec = str(self.options.python)
                output = StringIO()
                self.run('{0} -c "import sys; print(sys.executable)"'.format(pyexec), output=output)
                self._py_exec = output.getvalue().strip()
            except:
                raise Exception("Error running python at path provided: %s" % str(self.options.python))
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
            self.run('"{0}" -c "{1}"'.format(pyexec, cmd), output=output)
            result = output.getvalue().strip()
        else:
            result = ""
        return result if result and result != "" else None
