# Copyright (c) 2009 The PyAMF Project.
# See LICENSE.txt for details.


from release.builds import BuildFarm, Library

from buildbot.steps.source import SVN 


# SCM
svn_rep = "http://svn.pyamf.org/pyamf/"
svn_step = SVN(name="svn-update", baseURL=svn_rep, defaultBranch="trunk", mode="export")


# SOURCE FOLDERS
distFolder = '/home/buildbot/dist/pyamf'
webFolder = '/home/buildbot/web/pyamf'
libFolder = '/home/buildbot/thirdparty/'
amf_dumps = 'dumps.tar.gz'


# SLAVES
slaves = [
        'ubuntu-py23',
        'ubuntu-py24',
        'ubuntu-py25',
        'ubuntu-py26',
        'x86-macosx-py25',
        'winxp32-py24',
        'winxp32-py25',
        'winxp32-py26',
        'debian64-py23',
        'debian64-py24',
        'debian64-py25',
        'debian64-py26',
        'google-appengine-py25',
        'jython25'
]


# LIBRARIES
sqlalchemy = Library('SQLAlchemy', True, libFolder + 'sqlalchemy-%s.tar.gz',
                     ['0.4.8', '0.5.6'],
                     ['ubuntu-py23', 'winxp32-py24'])

twisted = Library('Twisted', True, libFolder + 'twisted-%s.tar.gz',
                  ['2.5.0', '8.1.0', '8.2.0'],
                  ['ubuntu-py23', 'winxp32-py24'])

django = Library('Django', True, libFolder + 'django-%s.tar.gz',
                  ['0.9.7', '1.0.1'],
                  ['ubuntu-py23', 'winxp32-py24'])


# BUILD FARM
libraries = [sqlalchemy, twisted, django]
farm = BuildFarm('PyAMF Buildfarm', libraries, svn_step, distFolder, webFolder, libFolder)
builders = farm.run()

# THIS IS IMPORTED IN THE BUILDBOT MASTER CONFIG FILE
# from pyamf import builders
# c['builders'] = builders