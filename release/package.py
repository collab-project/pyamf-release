# Copyright (c) The PyAMF Project.
# See LICENSE.txt for details.

"""
Scripts for basic release building in the PyAMF project.
"""

import os, sys
import logging
import urllib2
from hashlib import md5
from tempfile import mkdtemp
from tarfile import TarFile
from zipfile import ZipFile
from ConfigParser import RawConfigParser

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
        version_file = self.directory.child("pyamf").child("__init__.py")
        execfile(version_file.path, namespace)

        return namespace["version"]

    def updateVersion(self, version):
        """
        Replace the existing version numbers in files with the specified version.
        """
        oldVersion = self.getVersion()

        # TODO: ticket 543 - replace release date in changelog
        
        # remove the egg_info metadata from setup.cfg
        logging.info("Updating setup.cfg...")
        setup_cfg = self.directory.child("setup.cfg")
        config = RawConfigParser()
        config.read(setup_cfg.path)
        config.remove_section('egg_info')

        # save updated configuration file
        with open(setup_cfg.path, 'wb') as configfile:
            config.write(configfile)


class DistributionBuilder(TwistedDistributionBuilder):
    """
    A builder of PyAMF distributions.

    This knows how to build tarballs for PyAMF.
    """

    files = ["LICENSE.txt", "CHANGES.txt", "setup.py", "setup.cfg",
             "ez_setup.py", "pyamf", "cpyamf"]

    export_types = ["tar.bz2", "tar.gz", "zip"]

    def build(self, title, version):
        """
        Build the main distributions in `<title>-<version>.|targ.gz|tar.bz2|zip`.

        :type title: `str`
        :param title: The title of the distribution.
        :type version: `str`
        :param version: The version of PyAMF to build.

        :return: The tarball file.
        :rtype: :class:`twisted.python.filepath.FilePath`
        """
        self.releaseName = "%s-%s" % (title, version)
        self.buildPath = lambda *args: os.sep.join((self.releaseName,) + args)

        # build documentation
        self.docPath = self.rootDirectory.child("doc")
        self.html_docs = self._buildDocumentation()

        # clean up pycs
        self.clean()

        # create tarballs
        checksums = self._buildTarballs(version)

        # update md5 checksums file
        md5sums_file = self._updateChecksums(checksums)

    def clean(self):
        """
        Clean .pyc and .so files.
        """
        # todo: use glob instead?
        for files in os.walk(self.rootDirectory.path):
            for f in files[2]:
                if f.endswith('.pyc') or f.endswith('.so'):
                    os.unlink(os.path.join(files[0], f))
                
    def _buildDocumentation(self):
        """
        Build documentation.

        :rtype: `FilePath`
        :return: File path for HTML build output directory.
        """
        logging.info("Building documentation...")

        html_output = self.docPath.child("_build").child('html')
        sphinx_build = ["sphinx-build", "-b", "html", self.docPath.path,
                        html_output.path]

        logging.debug(" ".join(sphinx_build))
        runCommand(sphinx_build)

        return html_output

    def _buildTarballs(self, version):
        """
        Build .zip/.tar.gz/.tar.bz2 files.

        :param version: Distribution version nr.
        :type version: `str`

        :rtype: `list`
        :return: tarball checksums
        """
        checksums = []

        if self.outputDirectory.exists():
            self.outputDirectory.remove()

        logging.info("")
        logging.debug("Creating tarball export directory...")
        self.outputDirectory.createDirectory()

        logging.info("Creating %s.|%s" % (self.releaseName, "|".join(self.export_types)))

        for ext in self.export_types:
            outputFile = self.outputDirectory.child(".".join([self.releaseName, ext]))
            logging.info("")
            logging.info(" - %s%s%s" % (os.path.basename(self.outputDirectory.path),
                                        os.sep, os.path.basename(outputFile.path)))

            # create tarball
            if ext == "zip":
                self.tarball = self._createZip(outputFile)
            else:
                self.tarball = self._createTarball(outputFile)

            self._addFiles()                           
            self.tarball.close()

            # get md5
            md5 = self._createMD5(outputFile.path)
            checksum_entry = "%s  ./%s/%s\n" % (md5, version,
                                                os.path.basename(outputFile.path))
            checksums.append(checksum_entry)
            logging.debug("\t\t - MD5: " + md5)

        return checksums

    def _updateChecksums(self, checksums):
        """
        Update the `MD5SUMS` file.

        :rtype: `FilePath`
        :return: Location of `MD5SUMS` file
        """
        logging.info("")
        logging.info("Updating MD5SUMS...")

        # download the file
        original = urllib2.urlopen('http://download.pyamf.org/MD5SUMS')
        data = original.read().strip() + "\n"

        # create updated file in dist
        md5sums = self.outputDirectory.child("MD5SUMS")
        outputFile = open(md5sums.path, "w")
        outputFile.writelines(data)
        outputFile.writelines(checksums)

        logging.debug("Created: %s" % md5sums.path)

        return md5sums

    def _addFiles(self):
        """
        Add documentation and other files to tarball.
        """
        src = self.rootDirectory

        # add compiled documentation
        self.tarball.add(self.html_docs.path, self.buildPath("doc"))
        self.tarball.add(self.docPath.child("tutorials").child("examples").path,
                         self.buildPath("doc/tutorials/examples"))
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

        title = "PyAMF"
        sourcePath = export.child("pyamf")
        project = Project(export)
        version = project.getVersion()
        logging.info("Building %s %s..." % (title, str(version)))
        project.updateVersion(version)

        db = DistributionBuilder(export, destination)
        db.build(title, version)

        logging.debug("")
        logging.debug("Removing build directory...")
        workPath.remove()

        logging.info("")
        logging.info("Distribution builder ready.")


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

