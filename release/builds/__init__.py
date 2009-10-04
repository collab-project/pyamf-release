# Copyright (c) 2007-2009 The PyAMF Project.
# See LICENSE for details.

"""
Buildsteps for the PyAMF buildmaster.

Requires installation of setuptools and buildbot >= 0.7.11.
"""


import os
import glob

from release.builds.util import Builder


class AppBuilder(Builder):
    """
    Builder for PyAMF.
    """

    def __init__(self, name, slaveName, scm, destFolder, webFolder,
                 saFolder, sa04='0.4.8', sa05='0.5.0', dumps='dumps.tar.gz',
                 **kwargs):
        """
        @param name: Name of the builder.
        @type name: C{str}
        @param slaveName: Name of the buildslave.
        @type slaveName: C{str}
        @param scm: Source control buildstep.
        @type scm: L{buildbot.steps.source.*}
        @param os: String containing the operating system name.
        @type os: C{str}
        @param destFolder: Destination folder on buildmaster for .egg file.
        @type destFolder: C{str}
        @param webFolder: Destination folder on buildmaster for nightly file.
        @type webFolder: C{str}
        @param saFolder: Source folder on buildmaster with SQLAlchemy tarballs.
        @type saFolder: C{str}
        @param sa04: SQLAlchemy 0.4.x version number, ie. '0.4.8'.
        @type sa04: C{str}
        @param sa05: SQLAlchemy 0.5.x version number, ie. '0.5.0'.
        @type sa05: C{str}
        @param dumps: Name of AMF dumps gzipped tarball.
        @type dumps: C{str}
        """
        self.name = name
        self.slaveName = slaveName
        self.scm = scm
        self.destFolder = destFolder
        self.webFolder = webFolder
        self.saFolder = saFolder
        self.sa04 = sa04
        self.sa05 = sa05
        self.dumps = dumps
        
        Builder.__init__(self, name, slaveName, scm, name, **kwargs)
        

    def start(self):
        """
        Run the builder.
        """
        # Name of gzipped tarball that contains the compiled egg that gets
        # uploaded from the slave to the master
        eggTarball = 'pyamf-egg-%s.tar.gz' % (self.name)

        # Checkout source code
        self.checkout()
        
        # Download source to slave for SQLAlchemy 0.4.x and 0.5.x
        sa_tarball = 'sqlalchemy-%s.tar.gz'
        sa_path = os.path.join(self.saFolder, sa_tarball)
        
        self.download(sa_path % self.sa04, sa_tarball % self.sa04)
        self.download(sa_path % self.sa05, sa_tarball % self.sa05)
        self.unpack_sqlalchemy(sa_tarball, self.sa04)
        self.unpack_sqlalchemy(sa_tarball, self.sa05)
        
        # Setup build steps
        self.compile()
        self.test()
        self.install('./install')
        self.compile(True)
        self.test(True)
        self.install('./install', True)
        self.dist('./build/dist')
        self.pyflakes('pyamf')

        # Download AMF dumps gzipped tarball to slaves
        self.download('~/'+self.dumps, self.dumps)

        # Run parser script on AMF dumps
        self.unpack_dumps(self.dumps)
        self.parse_dumps()

        # Build .egg file for trunk and upload to the master
        egg_path = os.path.join(self.destFolder, eggTarball)
        self.compress_egg(eggTarball)
        self.upload(eggTarball, egg_path)
        self.master(['mv ' + egg_path + ' ' + self.webFolder])
        
        Builder.start(self)


    def unpack_sqlalchemy(self, src, version, **buildstep_kwargs):
        """
        Put SQLAlchemy source files in place on the buildslave.

        @param src: Location of the compressed dumps tarball.
        @type src: C{src}
        @param version: SQLAlchemy version number, ie. '0.4.8'.
        @type version: C{str}
        """
        if version is None:
            return

        self.stepName = 'unpack-sqlalchemy-' + version
        self.descriptionDone = 'Unpacked SQLAlchemy ' + version

        src = src % version

        return self.decompress(src, **buildstep_kwargs)


    def compress_egg(self, src, **buildstep_kwargs):
        """
        Compresses the .egg file into a tarball for transfer to the buildmaster.
        
        @param src: Location of the tarball.
        @type src: C{str}
        """
        self.stepName = 'Compress .egg file'
        self.descriptionDone = 'Compressed .egg file'
        self.command = ['./build/dist']

        return self.compress(src, **buildstep_kwargs)


    def unpack_dumps(self, src, **buildstep_kwargs):
        """
        Decompresses the tarball's .amf* dump files.
        
        @param src: Location of the dumps tarball.
        @type src: C{str}
        """
        self.stepName = 'Decompress AMF dump files'
        self.descriptionDone = 'Decompressed AMF dump files'

        return self.decompress(src, **buildstep_kwargs)


    def parse_dumps(self, **buildstep_kwargs):
        """
        Run the parse_dump script on the AMF dump files.
        """
        self.stepName = 'Parsing AMF dumps'
        self.descriptionDone = 'Parsed AMF dumps'
        script = './build/parse_dump.py'
        args = ['./build/dumps/*']

        return self.python(script, args, **buildstep_kwargs)

