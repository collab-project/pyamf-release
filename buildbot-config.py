# Copyright (c) The PyAMF Project.
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
        'debian64-py26'
        #'google-appengine-py25',
        #'jython25'
]


# LIBRARIES
sqlalchemy = Library(name='SQLAlchemy',
                     src=libFolder + 'sqlalchemy-%s.tar.gz',
                     versions=['0.4.8', '0.5.6'],
                     slaves=slaves)

twisted = Library(name='Twisted',
                  src=libFolder + 'twisted-%s.tar.gz',
                  versions=['2.5.0', '8.2.0', '9.0.0'],
                  slaves=slaves)

django = Library('Django',
                 src=libFolder + 'django-%s.tar.gz',
                 versions=['0.9.7', '1.1'],
                 slaves=slaves)


# BUILD FARM
libraries = [sqlalchemy, twisted, django]
farm = BuildFarm(name='PyAMF Buildfarm', libraries=libraries,
                 scm=svn_step, distFolder=distFolder,
                 webFolder=webFolder, libFolder=libFolder)
builders = farm.run()

# THIS IS IMPORTED IN THE BUILDBOT MASTER CONFIG FILE
# from pyamf import builders
# c['builders'] = builders
