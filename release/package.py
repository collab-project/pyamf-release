# Copyright (c) The PyAMF Project.
# See LICENSE.txt for details.

"""
Scripts for basic release building in the PyAMF project.
"""

import os, sys
import logging
from hashlib import md5
from tempfile import mkdtemp
from tarfile import TarFile
from zipfile import ZipFile

from twisted.python.filepath import FilePath
from twisted.python._release import runCommand
from twisted.python._release import Project as TwistedProject
from twisted.python._release import DistributionBuilder as TwistedDistributionBuilder

   
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
        version_file = self.directory.child("__init__.py")
        execfile(version_file.path, namespace)

        return namespace["version"]

    def updateVersion(self, version):
        """
        Replace the existing version numbers in files with the specified version.
        """
        oldVersion = self.getVersion()

        # TODO: ticket 543 - replace release date in changelog
        
        #update(self.directory.child("__init__.py"), version)
        #_changeVersionInFile(
        #    oldVersion, version,
        #    self.directory.child("topfiles").child("README").path)


class DistributionBuilder(TwistedDistributionBuilder):
    """
    A builder of PyAMF distributions.

    This knows how to build tarballs for PyAMF.
    """

    files = ["LICENSE.txt", "CHANGES.txt", "setup.py", "setup.cfg",
             "ez_setup.py", "pyamf", "cpyamf"]

    export_types = ["tar.bz2", "tar.gz", "zip"]

    def build(self, version):
        """
        Build the main PyAMF distribution in `PyAMF-<version>.<ext>`.

        :type version: `str`
        :param version: The version of PyAMF to build.

        :return: The tarball file.
        :rtype: :class:`twisted.python.filepath.FilePath`
        """
        releaseName = "PyAMF-%s" % (version,)
        self.buildPath = lambda *args: os.sep.join((releaseName,) + args)       

        # TODO: ticket 546 - remove the egg_info metadata from setup.cfg
        # TODO: ticket 665 - parse CHANGES.txt into a simple structure

        # build documentation
        docPath = self.rootDirectory.child("doc")
        self.html_docs = self._buildDocumentation(docPath)

        # clean up pycs
        self.clean()

        logging.info("")
        logging.info("Creating %s.|%s" % (releaseName, "|".join(self.export_types)))

        # create tarballs
        if self.outputDirectory.exists():
            self.outputDirectory.remove()

        logging.debug("Creating tarball export directory...")
        self.outputDirectory.createDirectory()
        
        for ext in self.export_types:
            outputFile = self.outputDirectory.child(".".join(
                [releaseName, ext]))
            logging.info(" - %s%s%s" % (os.path.basename(self.outputDirectory.path),
                                        os.sep, os.path.basename(outputFile.path)))

            if ext == "zip":
                self.tarball = self._createZip(outputFile)
            else:
                self.tarball = self._createTarball(outputFile)

            self._addFiles()                           
            self.tarball.close()

    def clean(self):
        """
        Clean .pyc and .so files.
        """
        for files in os.walk(self.rootDirectory.path):
            for f in files[2]:
                if f.endswith('.pyc') or f.endswith('.so'):
                    os.unlink(os.path.join(files[0], f))
                
    def _buildDocumentation(self, doc):
        """
        Build documentation.
        """
        logging.info("Building documentation...")

        sphinx_build = ["sphinx-build", "-b", "html", doc.path,
                   doc.child("_build").child("html").path]
        logging.debug(" ".join(sphinx_build))
        runCommand(sphinx_build)
        
        html = doc.child("_build").child('html')

        return html

    def _addFiles(self):
        """
        Add documentation and other files to tarball.
        """
        src = self.rootDirectory

        # add compiled documentation
        self.tarball.add(self.html_docs.path, self.buildPath("doc"))
        logging.debug("\t\t - doc")

        # add root files
        for f in self.files:        
            logging.debug("\t\t - " + f)
            self.tarball.add(src.child(f).path, self.buildPath(f))       

    def _createTarball(self, outputFile):
        """
        Helper method to create a tarball file.

        :param outputFile: The location to use for the new tar file.
        :type outputFile: `FilePath`
        :return: compressed `TarFile`
        """
        comp = outputFile.path[-3:]
        
        if comp == ".gz":
            comp = "gz"
        
        tarball = TarFile.open(outputFile.path, mode='w:' + comp)
        
        return tarball

    def _createZip(self, outputFile):
        """
        Helper method to create a ZIP file.

        :param outputFile: The location of the zip file to create.
        :type outputFile: `FilePath`
        :return: `ZipFile`
        """
        def zip_writer(dirpath, zippath):
            basedir = os.path.dirname(dirpath) + '/'
            if os.path.isdir(dirpath):
                for root, dirs, files in os.walk(dirpath):
                    if os.path.basename(root)[0] == '.':
                        continue # skip hidden directories
                    dirname = root.replace(basedir, '')
                    for f in files:
                        if f[-1] == '~' or f[0] == '.':
                            # skip backup files and all hidden files
                            continue

                        self.tarball.write(root + '/' + f, dirname + '/' + f)
            else:
                self.tarball.write(dirpath, os.path.basename(zippath))

        zipfile = ZipFile(outputFile.path, 'w')
        zipfile.add = zip_writer

        return zipfile

    def _createMD5(self, fileName, excludeLine="", includeLine=""):
        """
        Compute MD5 hash of the specified file.

        :rtype: `str`
        """
        m = md5()
        try:
            fd = open(fileName, "rb")
        except IOError:
            logging.error("Unable to open the file:" + filename)
            return

        content = fd.readlines()
        fd.close()
        for eachLine in content:
            if excludeLine and eachLine.startswith(excludeLine):
                continue
            m.update(eachLine)
        m.update(includeLine)

        return m.hexdigest()


class BuildTarballsScript(object):
    """
    A thing for building release tarballs. See `BuildAllTarballs`.
    """

    def main(self, args):
        """
        Build all release tarballs.

        :type args: list of str
        :param args: The command line arguments to process.  This must contain
            two strings: the checkout URL and the path to the destination directory.
        """
        if len(args) != 2:
            sys.exit("Must specify two arguments: "
                     "checkout URL and destination path")

        self.buildAllTarballs(args[0], FilePath(args[1]))

    def buildAllTarballs(self, checkout, destination):
        """
        Build complete tarballs (including documentation) for PyAMF.

        :type checkout: `str`
        :param checkout: The SVN URL from which a pristine source tree
            will be exported.
        :type destination: `FilePath`
        :param destination: The directory in which tarballs will be placed.
        """
        workPath = FilePath(mkdtemp())
        
        logging.basicConfig(level=logging.DEBUG,
               format='%(asctime)s %(levelname)-5.5s [%(name)s] %(message)s')
        logging.info("Started distribution builder...")
        logging.info('')
        logging.info("Build directory: %s" % workPath.path)
        logging.info("Tarball export directory: %s" % destination.path)
        logging.info("SVN URL: %s" % checkout)
        logging.info('')

        export = workPath.child("export")
        svn_export = ["svn", "export", checkout, export.path]
        logging.info("Exporting SVN directory...")
        logging.debug(" ".join(svn_export))
        runCommand(svn_export)
        logging.info('')

        sourcePath = export.child("pyamf")
        project = Project(sourcePath)
        version = project.getVersion()
        logging.info("Building PyAMF %s..." % str(version))
        project.updateVersion(version)

        db = DistributionBuilder(export, destination)
        db.build(version)

        workPath.remove()


__all__ = ["BuildTarballsScript"]


# OLD

def build_ext(src_dir):
    cwd = os.getcwd()
    os.chdir(src_dir)

    args = ["python", "setup.py", "develop"]

    cmd = subprocess.Popen(args)
    retcode = cmd.wait()

    if retcode != 0:
        raise RuntimeError, "Error building extension"

    os.chdir(cwd)

def package_project(src_dir, doc_dir, options):
    """
    Builds tar.gz, tar.bz2, zip from the src_dir's
    """
    shutil.rmtree(os.path.join(src_dir, 'build'))
    shutil.rmtree(os.path.join(src_dir, '%s.egg-info' % options.name))

