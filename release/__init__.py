# Copyright (c) The PyAMF Project.
# See LICENSE.txt for details.

import logging
from datetime import datetime
from ConfigParser import RawConfigParser

from twisted.python._release import Project as TwistedProject


__all__ = ["sizeof_fmt", "Project"]


def sizeof_fmt(num):
    """
    get human-readable filesize.
    """
    for x in ['bytes','KB','MB','GB','TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0


class Project(TwistedProject):
    """
    A representation of a PyAMF project that has a version.

    :ivar directory: A :class`twisted.python.filepath.FilePath` pointing to the base
        directory of a PyAMF-style Python package. The package should contain
        a `__init__.py` file, and the root directory contains the LICENSE.txt etc
        files.
    """

    def getVersion(self):
        """
        :return: :class`pyamf.version.Version` specifying the version number of the project
                 based on live python modules.
        """
        namespace = {}
        version_file = self.directory.child("pyamf").child("__init__.py")
        execfile(version_file.path, namespace)

        return namespace["version"]

    def updateVersion(self, version):
        """
        Replace the existing version numbers in files with the specified version.
        """
        # replace release date in changelog
        logging.info("\tUpdating changelog...")

        # open change log file
        change_log = self.directory.child("CHANGES.txt")
        changelog = open(change_log.path, "r")
        now = datetime.now().isoformat()[:10]
        old_date = "(unreleased)"
        new_date = "(%s)" % now
        newlines = []
        found = 0

        for line in changelog:
            if found > 0:
                line = "%s\n" % ("-" * found)
                found = 0

            if line.find(old_date) > -1:
                line = line.replace(old_date, new_date)
                found = len(line) - 1

            newlines.append(line)

        # create updated change log file
        outputFile = open(change_log.path, "wb")
        outputFile.writelines(newlines)

        # remove the egg_info metadata from setup.cfg
        logging.info("\tUpdating setup.cfg...")
        setup_cfg = self.directory.child("setup.cfg")
        config = RawConfigParser()
        config.read(setup_cfg.path)
        config.remove_section('egg_info')

        # save updated configuration file
        with open(setup_cfg.path, 'wb') as configfile:
            config.write(configfile)
