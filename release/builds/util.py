# Copyright (c) 2007-2009 The PyAMF Project.
# See LICENSE for details.

"""
Buildbot util.
"""

import re
import os

try:
    from buildbot.process.factory import BuildFactory
    from buildbot.process.properties import WithProperties
    from buildbot.status.builder import SUCCESS, FAILURE
    from buildbot.steps.shell import Compile, Test, ShellCommand
    from buildbot.steps.master import MasterShellCommand
    from buildbot.steps.transfer import FileDownload, FileUpload
    from buildbot.steps.python import PyFlakes
except ImportError:
    raise ImportError('This script requires Buildbot 0.7.11 or newer')


def getInterpreter(os='unix', version='2.5'):
    """
    Get Python or Jython interpreter string.
    
    @param os: Builder name containing the operating system name.
    @type os: C{str}
    @param version: Version number of interpreter, ie. '2.5'.
    @type version: C{str}
    """
    # unix
    interpreter = 'python' + version 
        
    if re.search('win', os) is not None:
        # windows-only command
        interpreter = 'C:\Python%s%s\Python.exe' % (version[0], version[2])

    elif re.search('jython', os) is not None:
        # Jython
        interpreter = 'jython'

    return [interpreter]


class Builder(object):
    """
    """

    def __init__(self, name, slaveName, scm_step, os):
        """
        @param name: Name of the builder.
        @type name: C{str}
        @param slaveName: Name of the buildslave.
        @type slaveName: C{str}
        @param scm_step: Source control buildstep.
        @type scm_step: L{buildbot.steps.source.*}
        @param os: String containing the operating system name.
        @type os: C{str}
        """
        self.name = name
        self.slaveName = slaveName
        self.scm_step = scm_step
        self.version = '%s.%s' % (name[-2], name[-1])
        self.os = os
        self.command = []
        self.factory = BuildFactory()


    def start(self):
        """
        Create and return builder.
        """
        b = {'name': self.name,
             'slavename': self.slaveName,
             'builddir': self.name,
             'factory': self.factory,
        }
        
        return b


    def slave_step(self, **buildstep_kwargs):
        """
        Create slave buildstep.
        
        @return: The step.
        """
        step = self.type(name=self.name, descriptionDone=self.descriptionDone,
                         command=self.command, **buildstep_kwargs)
        
        self.factory.addStep(step)


    def master_step(self, **buildstep_kwargs):
        """
        Create master buildstep.
        
        @return: The step.
        """
        step = MasterShellCommand(name=self.name, command=self.command,
				  **buildstep_kwargs)
        
        self.factory.addStep(step)


    def setup_step(self, action, **buildstep_kwargs):
        """
        Create Python setuptools step.

        @param action: One of: build, install, test
        @type action: C{str}
        """
        self.name = 'python%s-%s' % (self.version, action)
        self.descriptionDone = 'python%s %s' % (self.version, action)
        self.command = getInterpreter(self.os, self.version) + ['./setup.py', action, self.command]

        if self.ext is not True:
            self.command.append('--disable-ext')

        return self.slave_step(**buildstep_kwargs)


    def decompress(self, file, **buildstep_kwargs):
        """
        Decompress a tar file.

        @param file: Name of the tarball file.
        @type file: C{str}

        @return: A slave step.
        """
        self.type = ShellCommand
        self.name = 'Decompressing %s' % file
        self.descriptionDone = 'Decompressed %s' % file
        self.command = ['tar', 'xvf', file]
        
        return self.slave_step(**buildstep_kwargs)


    def compress(self, file, **buildstep_kwargs):
        """
        Compress a tar file with gzip encoding.

        @param file: Name of the output tarball.
        @type file: C{str}

        @return: A slave step.
        """
        self.type = ShellCommand
        self.name = 'Compressing %s' % file
        self.descriptionDone = 'Compressed %s' % file
        self.command = ['tar', 'zcvf', file]
        
        return self.slave_step(**buildstep_kwargs)


    def compile(self, ext=False, **buildstep_kwargs):
        """
        Build the code.
        
        @param ext: Enable C-extension build.
        @type ext: C{bool}
        """
        self.type = Compile
        self.ext = ext
        self.name = 'Compiling code'
        self.descriptionDone = 'Compiled code'

        return self.setup_step('build', **buildstep_kwargs)


    def test(self, ext=False, **buildstep_kwargs):
        """
        Test the code.
        
        @param ext: Enable C-extension build.
        @type ext: C{bool}
        """
        self.type = Test
        self.ext = ext
        self.name = 'Running unit tests'
        self.descriptionDone = 'Completed unit tests'
        #step.evaluateCommand = evaluateCommand

        return self.setup_step('test', **buildstep_kwargs)


    def install(self, dest, ext=False, **buildstep_kwargs):
        """
        Install the code.

        @param dest: Destination folder for installed files.
        @type dest: C{str}
        @param ext: Enable C-extension build.
        @type ext: C{bool}
        """
        self.type = Compile
        self.ext = ext
        self.name = 'Installing code to %s' % dest
        self.descriptionDone = 'Installed code to %s' % dest
        self.command = ['--root=' + dest]
        
        return self.setup_step('install', **buildstep_kwargs)


    def dist(self, dest, ext=True, **buildstep_kwargs):
        """
        Build platform-specific .egg file.

        @param dest: Destination folder for compiled files.
        @type dest: C{str}
        @param ext: Enable C-extension build.
        @type ext: C{bool}
        """
        self.type = ShellCommand
        self.ext = ext
        self.name = 'Building .egg in %s' % dest
        self.descriptionDone = 'Created .egg in %s' % dest
        self.command = ['--dist-dir=' + dest]
        
        return self.setup_step('bdist_egg', **buildstep_kwargs)


    def master(self, command, **buildstep_kwargs):
        """
        Run a command on the buildmaster.

        @param command: Command to run on the master.
        @type command: L{}
        """
        self.name = 'Publish .egg to web'
        self.descriptionDone = 'Published .egg to web'
        self.command = command

        return self.master_step(**buildstep_kwargs)


    def python(self, script, args=[], **buildstep_kwargs):
        """
        Execute a Python script.
        
        @param script: Location of the Python script.
        @type script: C{str}
        @param args: Arguments passed to the Python script.
        @type args: C{list}
        """
        self.type = ShellCommand
        self.command = [getInterpreter(self.os, self.version),
                        script] + args

        return self.slave_step(**buildstep_kwargs)


    def upload(self, src, dest, **buildstep_kwargs):
        """
        Transfer a file from the buildslave to the buildmaster.
        
        @param src: Location of the file
        @type src: C{str}
        @param dest: Target folder on the buildmaster.
        @type dest: C{str}
        """
        self.factory.addStep(FileUpload(slavesrc=src, masterdest=dest, **buildstep_kwargs))


    def download(self, src, dest, **buildstep_kwargs):
        """
        Download a file from the buildmaster to the buildslave.
        
        @param src: Location of the file on the master.
        @type src: C{str}
        @param dest: Target folder on the slave.
        @type dest: C{str}
        """
        self.factory.addStep(FileDownload(mastersrc=src, slavedest=dest, **buildstep_kwargs))


    def pyflakes(self, src, **buildstep_kwargs):
        """
        Run pyflakes on a Python package or module.
        
        @param src: Location of Python module to be checked.
        @type src: C{str}
        """
        self.type = PyFlakes
        self.name = 'PyFlakes'
        self.descriptionDone = 'PyFlakes'
        self.command = ['pyflakes', src]

        return self.slave_step(**buildstep_kwargs)


    def checkout(self, **buildstep_kwargs):
        """
        Checkout the code.
        """
        self.factory.addStep(self.scm)


class GAECompile(ShellCommand):
    """
    Google App Engine buildstep.
    """

    def __init__(self, slaveScript=None, **kwargs):
        """
        @param slaveScript: Location of the buildslave script.
        @type slaveScript: C{str}
        """
        self.name = 'google-app-engine'
        self.descriptionDone = 'google-app-engine punit'
        self.slaveScript = slaveScript

        ShellCommand.__init__(self, **kwargs)

        self.addFactoryArguments(slaveScript=slaveScript)

    def start(self):
        command = ['python2.5', self.slaveScript]

        if self.getProperty('branch') is not None:
            command.append(WithProperties('--branch=%(branch)s'))

        self.setCommand(command)
        ShellCommand.start(self)


class GAEBuilder(object):
    """
    Google App Engine build factory.
    """

    def __init__(self, builder, slave, src):
        """
        @param builder: Builder name.
        @type builder: C{str}
        @param slave: Slave name.
        @type slave: C{str}
        @param src: Location of the buildslave script.
        @type src: C{str}
        """
        self.builder = builder
        self.slave = slave
        self.script = src


    def createBuilder(self):
        """
        Create and return the builder.
        
        @return: The Google App Engine builder.
        @rtype: L{BuildFactory}
        """
        compile = GAECompile(slaveScript=self.script)

        f = BuildFactory()
        f.addStep(compile)

        b = {'name': self.builder,
             'slavename': self.slave,
             'builddir': self.builder,
             'factory': f,
        }

        return b


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
