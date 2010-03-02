# Copyright (c) The PyAMF Project.
# See LICENSE.txt for details.

"""
Scripts for basic release building in the PyAMF project.
"""

import os, sys
import hashlib
import logging
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
             "README.txt"]

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

        # TODO: ticket 543 - replace release date in changelog
        # TODO: ticket 546 - remove the egg_info metadata from setup.cfg
        # RODO: ticket 665 - parse CHANGES.txt into a simple structure

        # build documentation
        docPath = self.rootDirectory.child("doc")
        self._buildDocumentation(docPath)

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
                self.tarball = self._createTarball(outputFile, ext[:3])

            self._addFiles()
            self.tarball.close()

    def _buildDocumentation(self, doc):
        """
        Build documentation.
        """
        logging.info("Building documentation..")


    def _addFiles(self):
        """
        Add documentation and other files to tarball.
        """
        root = self.rootDirectory

        try:
            writer = self.tarball.add
        except:
            writer = self.tarball.write

        for f in self.files:
            logging.debug("\t\t - " + f)
            writer(root.child(f).path, self.buildPath(f))
        
    def _createTarball(self, outputFile, compression):
        """
        Helper method to create a tarball file with things.

        :param outputFile: The location of the tar file to create.
        :type outputFile: `FilePath`
        :param compression: Compression type/file extension, eg. 'bz2'
        :type compression: `str`
        :return: `TarFile`
        """
        tarball = TarFile.open(outputFile.path, 'w:' + compression)
        
        return tarball

    def _createZip(self, outputFile):
        """
        Helper method to create a ZIP file with things.

        :param outputFile: The location of the zip file to create.
        :type outputFile: `FilePath`
        :return: `ZipFile`
        """
        zipfile = ZipFile(outputFile.path, 'w')
        
        return zipfile


class BuildTarballsScript(object):
    """
    A thing for building release tarballs. See `BuildAllTarballs`.
    """

    def main(self, args):
        """
        Build all release tarballs.

        @type args: list of str
        @param args: The command line arguments to process.  This must contain
            two strings: the checkout directory and the destination directory.
        """
        if len(args) != 2:
            sys.exit("Must specify two arguments: "
                     "checkout and destination path")

        self.buildAllTarballs(args[0], FilePath(args[1]))

    def buildAllTarballs(self, checkout, destination):
        """
        Build complete tarballs (including documentation) for PyAMF.

        :type checkout: `str`
        :param checkout: The SVN URL from which a pristine source tree
            will be exported.
        @type destination: L{FilePath}
        @param destination: The directory in which tarballs will be placed.
        """
        workPath = FilePath(mkdtemp())

        logging.basicConfig(level=logging.DEBUG,
               format='%(asctime)s %(levelname)-5.5s [%(name)s] %(message)s')
        logging.info("Starting tarball builder.")
        logging.info("Build directory:" + workPath.path)
        logging.info("Tarball export directory: " + destination.path)
        logging.info("SVN URL: " + checkout)
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

def build_api_docs(src_dir, doc_dir, options):
    # create .so files for epydoc
    build_ext(export_dir)

    # generate html doc from rst file
    args = ["rst2html.py", os.path.join(src_dir, "CHANGES.txt"),
            os.path.join(doc_dir, "changes.html")]

    cmd = subprocess.Popen(args)
    retcode = cmd.wait()

    # generate API documentation
    args = ["epydoc", "--config=" +
        os.path.join(src_dir, "setup.cfg"), "-v",
        "--graph=umlclasstree", "--dotpath=" + options.dotpath,
        "--help-file=" + os.path.join(doc_dir, "changes.html")]

    cmd = subprocess.Popen(args)
    retcode = cmd.wait()

    if retcode != 0:
        raise RuntimeError, "Error building API docs"

    # the --output override for epydoc doesn't work
    # so copy the files and get rid of the old default
    # output destination folder
    temp_doc = os.path.join(os.getcwd(), "docs")
    shutil.copytree(temp_doc, os.path.join(doc_dir, "api"))
    shutil.rmtree(temp_doc)


def build_docs(options):
    # create .so files for epydoc
    doc_url = 'https://svn.pyamf.org/doc/tags/release-%s' % (options.version)
    retcode, cmd, export_dir = export_svn(doc_url, options)

    args = ["make", "html"]

    if retcode != 0:
        raise RuntimeError, "Problem exporting repository"

    cmd = subprocess.Popen(args, cwd=export_dir)
    retcode = cmd.wait()

    if retcode != 0:
        raise RuntimeError, "Error building docs"

    doc_dir = tempfile.mkdtemp()
    shutil.rmtree(doc_dir)
    temp_doc = os.path.join(export_dir, "_build", 'html')
    shutil.copytree(temp_doc, doc_dir)

    return doc_dir

def clean_package_dir(package_dir):
    for files in os.walk(package_dir):
        for f in files[2]:
            if f.endswith('.pyc') or f.endswith('.so'):
                os.unlink(os.path.join(files[0], f))

def package_project(src_dir, doc_dir, options):
    """
    Builds tar.gz, tar.bz2, zip from the src_dir's
    """
    build_dir = tempfile.mkdtemp()
    package_dir = os.path.join(build_dir, '%s-%s' % (options.name, options.version))
    shutil.rmtree(os.path.join(src_dir, 'build'))
    shutil.rmtree(os.path.join(src_dir, '%s.egg-info' % options.name))
    shutil.copytree(src_dir, package_dir)
    shutil.copytree(doc_dir, os.path.join(package_dir, 'doc'))

    clean_package_dir(package_dir)

    return build_dir, build_zip(build_dir, options), \
        build_tar_gz(build_dir, options), build_tar_bz2(build_dir, options)

def md5(fileName, excludeLine="", includeLine=""):
    """
    Compute md5 hash of the specified file.
    """
    m = hashlib.md5()
    try:
        fd = open(fileName, "rb")
    except IOError:
        print "Unable to open the file:", filename
        return
    content = fd.readlines()
    fd.close()
    for eachLine in content:
        if excludeLine and eachLine.startswith(excludeLine):
            continue
        m.update(eachLine)
    m.update(includeLine)

    return m.hexdigest()

if __name__ == '__main__':
    options, args = parse_args()

    if options.baseurl is None:
        raise ValueError, "baseurl is required"
    if options.name is None:
        raise ValueError, "project name is required"
    if options.version is None:
        raise ValueError, "version is required"

    cwd = os.getcwd()
    export_dir = export_repo(options)
    sys.path.insert(0, export_dir)
    doc_dir = build_docs(options)
    build_api_docs(export_dir, doc_dir, options)

    build_dir = package_project(export_dir, doc_dir, options)
    archives = build_dir[1:]
    build_dir = build_dir[0]

    print '=' * 70
    for archive in archives:
        print '%s  ./%s' % (md5(archive), os.path.basename(archive))
        shutil.copy(os.path.join(build_dir, archive), cwd)
    print '=' * 70

    shutil.rmtree(export_dir)
    shutil.rmtree(build_dir)
    shutil.rmtree(os.path.dirname(api_dir))

    print '\n%s-%s ready.\n' % (options.name, options.version)
