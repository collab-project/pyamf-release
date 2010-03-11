# Copyright (c) The PyAMF Project.
# See LICENSE.txt for details.

"""
Scripts for basic release building in the PyAMF project.
"""

import logging

from release import package
from release.package import BuildScript


class BuildTarballsScript(BuildScript):
    """
    A thing for building release tarballs (.zip/.tar.gz/.tar.bz2 files).
    """

    def __init__(self):
        self.builder = package.TarballsBuilder
        logging.info("Started tarballs builder...")


class BuildEggScript(BuildScript):
    """
    A thing for building Python eggs (.egg files).
    """

    def __init__(self):
        self.builder = package.EggBuilder
        logging.info("Started egg builder...")


class BuildDocumentationScript(BuildScript):
    """
    A thing for building the Sphinx documentation (.zip/.tar.gz/.tar.bz2/.pdf) files).
    """

    def __init__(self):
        self.builder = package.DocumentationBuilder
        logging.info("Started documentation builder...")


__all__ = ["BuildTarballsScript", "BuildEggScript", "BuildDocumentationScript"]
