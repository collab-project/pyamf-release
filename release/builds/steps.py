# Copyright (c) 2007-2009 The PyAMF Project.
# See LICENSE for details.

from release.builds.util import ShellCommand


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
