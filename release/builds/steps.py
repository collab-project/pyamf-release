# Copyright (c) 2007-2009 The PyAMF Project.
# See LICENSE.txt for details.


import os

from release.builds import Builder
from release.builds import ShellCommand


def evaluateCommand(cmd):
    r = Test.evaluateCommand(self, cmd)

    if r is FAILURE:
        return r

    lines = self.getLog('stdio').readlines()

    re_test_result = re.compile("FAILED \((failures=(\d*), )?(errors=(\d*), )?successes=(\d*)\)")

    mos = map(lambda line: re_test_result.search(line), lines)
    test_result_lines = [mo.groups() for mo in mos if mo]

    if not test_result_lines:
        return cmd.rc

    results = test_result_lines[0]

    failures = errors = passed = 0

    if results[1] is not None:
        failures = int(results[1])

    if results[3] is not None:
        errors = int(results[3])

    passed = int(results[4])

    if [failures, errors] == [0, 0]:
        rc = SUCCESS
    else:
        rc = FAILURE

    self.setTestResults(total=failures + errors + passed, failed=failures + errors, passed=passed)

    return rc


class GAECompile(ShellCommand):
    """
    Google App Engine buildstep.
    """

    def __init__(self, slaveScript=None, **kwargs):
        """
        @param slaveScript: Location of the buildslave script.
        @type slaveScript: C{str}
        """
        self.slaveScript = slaveScript

        ShellCommand.__init__(self, **kwargs)

        self.addFactoryArguments(slaveScript=slaveScript)

    def start(self):
        command = ['python2.5', self.slaveScript]

        if self.getProperty('branch') is not None:
            command.append(WithProperties('--branch=%(branch)s'))

        self.setCommand(command)
        ShellCommand.start(self)


class AppBuilder(Builder):
    """
    Python builder for PyAMF.
    """

    def __init__(self, name, slaveName, scm, destFolder, webFolder,
                 dumps='dumps.tar.gz', **kwargs):
        """
        @param name: Name of the builder.
        @type name: C{str}
        @param slaveName: Name of the buildslave.
        @type slaveName: C{str}
        @param scm: Source control buildstep.
        @type scm: L{buildbot.steps.source.*}
        @param destFolder: Destination folder on buildmaster for .egg file.
        @type destFolder: C{str}
        @param webFolder: Destination folder on buildmaster for nightly file.
        @type webFolder: C{str}
        @param dumps: Name of AMF dumps gzipped tarball.
        @type dumps: C{str}
        """
        self.name = name
        self.slaveName = slaveName
        self.scm = scm
        self.destFolder = destFolder
        self.webFolder = webFolder
        self.dumps = dumps
        
        Builder.__init__(self, name, slaveName, scm, name, **kwargs)
        

    def start(self, **kwargs):
        """
        Run the builder.
        
        @return: Add the buildsteps and return the builder dict.
        """
        # Name of gzipped tarball that contains the compiled egg that gets
        # uploaded from the slave to the master
        eggTarball = 'pyamf-egg-%s.tar.gz' % (self.name)

        # Checkout source code
        self.checkout()

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
        self.compress_egg('./build/dist', eggTarball)
        self.upload(eggTarball, egg_path)
        self.master(['mv ' + egg_path + ' ' + self.webFolder])

        return Builder.start(self, **kwargs)


    def compress_egg(self, src, dest, **buildstep_kwargs):
        """
        Compresses the .egg file into a tarball for transfer to the buildmaster.
        
        @param src: Contents of the tarball.
        @type src: C{str}
        @param dest: Name of the tarball.
        @type dest: C{str}
        """
        self.stepName = 'Compress .egg file'
        self.descriptionDone = 'Compressed .egg file'

        return self.compress(src, dest, **buildstep_kwargs)


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


class GAEBuilder(Builder):
    """
    Google App Engine builder.
    """

    def __init__(self, name, slaveName, src, **kwargs):
        """
        @param name: Name of the builder.
        @type name: C{str}
        @param slaveName: Name of the buildslave.
        @type slaveName: C{str}
        @param src: Location of the buildslave script.
        @type src: C{str}
        """
        self.name = name
        self.slaveName = slaveName
        self.src = src

        Builder.__init__(self, name, slaveName, None, 'unix', **kwargs)


    def start(self, **kwargs):
        """
        Create and return the builder.
        
        @return: The Google App Engine builder dict
        @rtype: C{dict}
        """
        # Setup buildsteps
        self.run_gae(self.src)

        return Builder.start(self, **kwargs)


    def run_gae(self, src, **buildstep_kwargs):
        """
        Run the gae buildslave script.
        """
        self.type = GAECompile
        self.stepName = 'google-app-engine'
        self.descriptionDone = 'google-app-engine punit'

        return self.python(src, **buildstep_kwargs)
