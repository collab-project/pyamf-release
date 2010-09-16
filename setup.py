# Copyright (c) The PyAMF Project.
# See LICENSE.txt for details.

from distribute_setup import use_setuptools

use_setuptools()

import sys, os.path
from setuptools import setup, find_packages

from pyamf import version

setup(name = "PyAMF Release Scripts",
    version = str(version),
    description = "Tools and scripts for the PyAMF release process",
    url = "http://pyamf.org",
    author = "The PyAMF Project",
    author_email = "users@pyamf.org",
    packages = find_packages(exclude=["*.tests"]),
    zip_safe = True,
    license = "MIT License",
    platforms = ["any"])
