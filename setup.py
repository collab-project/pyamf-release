# Copyright (c) 2009 The PyAMF Project.
# See LICENSE.txt for details.

from ez_setup import use_setuptools

use_setuptools()

import sys, os.path
from setuptools import setup, find_packages


def get_version():
    """
    Gets the version number. Pulls it from the source files rather than
    duplicating it.
    """
    # we read the file instead of importing it as root sometimes does not
    # have the cwd as part of the PYTHONPATH
    from pyamf import __version__ as version

    return '.'.join([str(x) for x in version])


setup(name = "PyAMF Release Scripts",
    version = get_version(),
    description = "Tools and scripts for the PyAMF release process",
    url = "http://pyamf.org",
    author = "The PyAMF Project",
    author_email = "users@pyamf.org",
    packages = find_packages(exclude=["*.tests"]),
    zip_safe = True,
    license = "MIT License",
    platforms = ["any"])
