# Copyright (c) The PyAMF Project.
# See LICENSE.txt for details.

"""
Scripts for basic release building in the PyAMF project.
"""

import os, sys
import logging
from glob import glob
from hashlib import md5
from zipfile import ZipFile
from tempfile import mkdtemp
from urllib2 import urlopen, HTTPError
from tarfile import TarFile, CompressionError, open as opentar

from release import Project
from release import sizeof_fmt

from twisted.python.filepath import FilePath
from twisted.python._release import runCommand, CommandFailed
from twisted.python._release import DistributionBuilder as TwistedDistributionBuilder


logging.basicConfig(level=logging.INFO,
               format='%(message)s')


class DistributionBuilder(TwistedDistributionBuilder):
    """
    A builder of PyAMF distributions.

    This knows how to build:
    
    - tarballs
    - eggs
    - documentation
    """

    documentation = True
    examples = False
    source = True
    checksums = False
    export_types = []
    checksums_url = 'http://download.pyamf.org/MD5SUMS'
    theme_url = 'https://github.com/collab-project/sphinx-themes/tarball/master'
    files = ["LICENSE.txt", "CHANGES.txt", "setup.py", "setup.cfg",
             "ez_setup.py", "pyamf", "cpyamf"]


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

        if self.documentation:
            # build documentation
            self.docPath = self.rootDirectory.child("doc")
            self.html_docs = self._buildMainDocumentation()
            self.api_docs = self._buildAPIDocumentation()

            # clean up pycs
            self._clean()

        # create package(s)
        packages = self._buildPackages(version)

        if self.source and self.checksums:
            # update md5 checksums file
            self._updateChecksums(packages)


    def _clean(self):
        """
        Clean .pyc and .so files.
        """
        for files in os.walk(self.rootDirectory.path):
            for f in files[2]:
                if f.endswith('.pyc') or f.endswith('.so'):
                    os.unlink(os.path.join(files[0], f))


    def _buildPackages(self, version):
        """
        Build packages(s).

        :param version: Distribution version nr.
        :type version: `str`

        :rtype: `list`
        :return: file checksum(s)
        """
        checksums = []

        if self.outputDirectory.exists():
            self.outputDirectory.remove()

        logging.debug("\tCreating output directory...")
        self.outputDirectory.createDirectory()

        logging.info("\tCreating package(s)...")

        for ext in self.export_types:
            outputFile = self.outputDirectory.child(".".join([self.releaseName, ext]))

            # create tarball or zip
            if ext == "zip":
                self.package = self._createZip(outputFile)
            elif ext != "egg":
                self.package = self._createTarball(outputFile)

            if ext != "egg" and self.package != None:
                self._addFiles()                           
                self.package.close()

            # create egg
            if ext == "egg":
                self.package = outputFile = self._createEgg()

            if outputFile.exists():
                # filename
                logging.info("\t - %s%s%s" % (os.path.basename(self.outputDirectory.path),
                                              os.sep, os.path.basename(outputFile.path)))

                # size
                size = sizeof_fmt(os.path.getsize(outputFile.path))
                logging.info("\t   Size: %s" % size)

                if self.source:
                    # md5
                    checksum = self._getMD5(outputFile.path)
                    checksum_entry = "%s  ./%s/%s\n" % (checksum, version,
                                                os.path.basename(outputFile.path))
                    checksums.append(checksum_entry)
                    logging.info("\t   MD5: " + checksum)

        return checksums


    def _updateChecksums(self, checksums):
        """
        Update the `MD5SUMS` file.

        :rtype: `FilePath`
        :return: Location of `MD5SUMS` file
        """
        md5sums = self.outputDirectory.child("MD5SUMS")

        if len(checksums) > 0:
            logging.info("\n\tUpdating MD5SUMS...")

            try:
                # download the file
                original = urlopen(self.checksums_url)
            except HTTPError:
                return

            data = original.read().strip() + "\n"

            # create updated file in dist
            outputFile = open(md5sums.path, "w")
            outputFile.writelines(data)
            outputFile.writelines(checksums)

            logging.debug("Created: %s" % md5sums.path)

        return md5sums


    def _buildMainDocumentation(self):
        """
        Build main documentation with Sphinx.

        :rtype: `FilePath`
        :return: File path for HTML build output directory.
        """
        self._setupTheme()

        logging.info("\tBuilding main documentation...")

        if self.examples:
            logging.info("\tIncluding examples...")

        html_output = self.docPath.child("_build").child('html')
        sphinx_build = ["sphinx-build", "-b", "html", self.docPath.path,
                        html_output.path]

        logging.debug(" ".join(sphinx_build))
        
        try:
            runCommand(sphinx_build)
        except CommandFailed, e:
            logging.info("")
            raise Exception("Error building main documentation with Sphinx:\n\n%s" % e[2])

        return html_output


    def _setupTheme(self):
        """
        Download and setup the theme.
        """
        logging.info("\tBuilding theme...")
        
        try:
            tarball = urlopen(self.theme_url).read()
        except HTTPError:
            raise Exception("Error downloading theme from %s" % self.theme_url)

        workPath = FilePath(mkdtemp())
        sourceFile = workPath.child("theme.tar.gz")

        # change dir to fix issue with sphinx & themes
        os.chdir(self.docPath.path)

        o = open(sourceFile.path , "w")
        o.write(tarball)
        o.close()
        tar = opentar(sourceFile.path, mode='r:*')
        tar.extractall(workPath.path)

        theme = None
        for d in workPath.listdir():
            theme = workPath.child(d)
            if theme.isdir():
                theme = theme.child("source").child("themes")
                dest = self.docPath.child("themes")
                theme.moveTo(dest)
                break


    def _buildAPIDocumentation(self):
        """
        Build API documentation with Epydoc.

        :rtype: `FilePath`
        :return: File path for HTML build output directory.
        """

        logging.info("\tBuilding API documentation...")
        
        html_output = self.docPath.child("_build").child('html').child('api')
        os.chdir(self.rootDirectory.path)
        epydoc_build = ["epydoc", "--config", "setup.cfg", "--debug",
                        "--output", html_output.path, "--simple-term"]

        logging.debug(" ".join(epydoc_build))
        
        try:
            runCommand(epydoc_build)
        except CommandFailed, e:
            print("\nError building API documentation with Epydoc:\n\n%s" % e[2])
            logging.error("\tError building API documentation, check Epydoc output. Skipping...")
            logging.error("")

        return html_output


    def _addFiles(self):
        """
        Add files to package.
        """
        src = self.rootDirectory
        files = []
        doc_output = self.buildPath()

        if self.source:
            files = self.files
            doc_output = self.buildPath("doc")
            logging.debug("\t\t - doc")

        # add compiled documentation
        self.package.add(self.html_docs.path, doc_output)

        if self.examples:
            # add examples
            self.package.add(self.docPath.child("tutorials").child("examples").path,
                             doc_output + "/tutorials/examples")

        # add source files
        for f in files:        
            logging.debug("\t\t - " + f)
            self.package.add(src.child(f).path, self.buildPath(f))       


    def _createTarball(self, outputFile):
        """
        Helper method to create a tarball file.

        :param outputFile: The location to use for the new tar file.
        :type outputFile: `FilePath`
        :return: compressed `TarFile`
        """
        comp = outputFile.path[-3:]
        
        if comp == ".gz": comp = "gz"

        try:
            tarball = TarFile.open(outputFile.path, mode='w:' + comp)
        except CompressionError:
            logging.error("\t - Warning! Ignoring unsupported export filetype: ." + str(comp))
            return

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
                        # skip hidden directories
                        continue
                    dirname = root.replace(basedir, '')
                    for f in files:
                        if f[-1] == '~' or f[0] == '.':
                            # skip backup files and all hidden files
                            continue

                        self.package.write(root + '/' + f, dirname + '/' + f)
            else:
                self.package.write(dirpath, os.path.basename(zippath))

        zipfile = ZipFile(outputFile.path, 'w')
        zipfile.add = zip_writer

        return zipfile


    def _createEgg(self):
        """
        Helper method to create a Python .egg file.
        """
        logging.info("\tBuilding egg...")

        build_dir = self.rootDirectory.child("build")
        build_dir.createDirectory()

        os.chdir(self.rootDirectory.path)

        egg_build = ["python", "setup.py", "bdist_egg", "--dist-dir",
                     self.outputDirectory.path]
        logging.debug("\t\t" + " ".join(egg_build))
        runCommand(egg_build)

        eggs = glob(os.path.join(self.outputDirectory.path, '*.egg'))
        egg = FilePath(eggs[0])

        return egg


    def _getMD5(self, fileName, excludeLine="", includeLine=""):
        """
        Compute MD5 hash of the specified file.

        :rtype: `str`
        """
        m = md5()
        try:
            fd = open(fileName, "rb")
        except IOError:
            logging.error("Unable to open the file:" + fileName)
            return

        content = fd.readlines()
        fd.close()
        for eachLine in content:
            if excludeLine and eachLine.startswith(excludeLine):
                continue
            m.update(eachLine)
        m.update(includeLine)

        return m.hexdigest()


class BuildScript(object):
    """
    PyAMF build script.
    """

    title = "PyAMF"       

    def main(self, args):
        """
        :type args: list of str
        :param args: The command line arguments to process.  This must contain
            two strings: the source URL and the path to the destination directory.
        """
        if len(args) != 2:
            sys.exit("Must specify two arguments: "
                     "source URL and destination path")

        try:
            self.build(args[0], FilePath(args[1]))
        except (KeyboardInterrupt):
            pass


    def build(self, checkout, destination):
        """
        Download source tree tarball from Github and update the version nr for PyAMF.

        :type checkout: `str`
        :param checkout: The source URL from which a pristine source tree
            tarball will be downloaded.
        :type destination: `FilePath`
        :param destination: The directory where the output files will be placed.
        """
        self.workPath = FilePath(mkdtemp())
        
        logging.info('')
        logging.debug("Build directory: %s" % self.workPath.path)
        logging.info("Output directory: %s" % destination.path)
        logging.info("Source tarball URL: %s" % checkout)
        logging.info('')

        logging.info("Downloading source tarball...")
        sourceFile = self.workPath.child("source.tar.gz")
        tarball = urlopen(checkout).read()
        o = open(sourceFile.path , "w")
        o.write(tarball)
        o.close()

        logging.info("Extracting tarball...")
        sourceDir = self.workPath.child("source")
        self.export = self.workPath.child("export")
        tar = opentar(sourceFile.path, mode='r:*')
        tar.extractall(sourceDir.path)
        dest = sourceDir.child(sourceDir.listdir()[0])
        dest.moveTo(self.export)
        logging.info('')
        
        project = Project(self.export)
        self.version = project.getVersion()

        logging.info("Building %s %s..." % (self.title, str(self.version)))
        project.updateVersion(self.version)

        self.db = self.builder(self.export, destination)
        self.db.build(self.title, self.version)

        logging.debug("")
        logging.debug("Removing build directory...")
        self.workPath.remove()

        logging.info("")
        logging.info("Builder ready.")


class TarballsBuilder(DistributionBuilder):
    """
    This knows how to build eggs for PyAMF.
    """

    export_types = ["tar.bz2", "tar.gz", "zip"]


class EggBuilder(DistributionBuilder):
    """
    This knows how to build eggs for PyAMF.
    """

    export_types = ["egg"]

    documentation = False


class DocumentationBuilder(DistributionBuilder):
    """
    This knows how to build documentation for PyAMF.
    """

    export_types = ["tar.bz2", "tar.gz", "zip"]

    source = False
    examples = True


__all__ = ["TarballsBuilder", "EggBuilder", "DocumentationBuilder", "BuildScript"]
