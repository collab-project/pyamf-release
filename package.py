# Copyright (c) 2007-2008 The PyAMF Project.
# See LICENSE for details.

"""
A basic release builder.

Example usage:
  python package.py --version=0.3 --name=PyAMF --package=pyamf --baseurl=http://svn.pyamf.org/pyamf/tags --branch=release-0.3

@author: U{Nick Joyce<mailto:nick@boxdesign.co.uk>}
"""

import os, os.path, sys, shutil
import subprocess, tempfile

def export_svn(url, options):
    args = ['svn', 'export']

    args.append(url)

    if options.username is not None:
        args.append('--username %s' % options.username)

    if options.password is not None:
        args.append('--password %s' % options.password)

    args.append('--force')
    export_dir = tempfile.mkdtemp()
    args.append(export_dir)

    cmd = subprocess.Popen(args)
    retcode = cmd.wait()

    return retcode, cmd, export_dir

def export_repo(options):
    repo_url = '%s/%s' % (options.baseurl, options.branch)

    if options.repo == 'svn':
        retcode, cmd, export_dir = export_svn(repo_url, options)
    else:
        raise ValueError, "Unknown repo type %s" % options.repo

    if retcode != 0:
        raise RuntimeError, "problem exporting repo"

    return export_dir

def build_api_docs(src_dir, options):
    api_dir = tempfile.mkdtemp()
    args = ["epydoc", "--output=%s" % api_dir, "--simple-term",
        "--show-imports", "--graph=umlclasstree", "--dotpath=/usr/local/bin/dot",
        "--name=%s API Documentation" % options.name, "--exclude=tests*",
        os.path.join(src_dir, options.package)]

    cmd = subprocess.Popen(args)
    retcode = cmd.wait()

    if retcode != 0:
        raise RuntimeError, "Error building API docs"

    return api_dir

def parse_args():
    def parse_targets(option, opt, value, parser):
        print value

    from optparse import OptionParser

    parser = OptionParser()

    parser.add_option('--baseurl', dest='baseurl')
    parser.add_option('--branch', dest='branch', default='trunk')
    parser.add_option('--version', dest='version')
    parser.add_option('--name', dest='name', help='The name of the project')
    parser.add_option('--package', dest='package', help='The name of the package')
    parser.add_option('--username', dest='username', default=None, help='Username to access the repo')
    parser.add_option('--password', dest='password', default=None, help='Password to access the repo')
    parser.add_option('--repo', dest='repo', default='svn')

    return parser.parse_args()

def build_zip(build_dir, options):
    cwd = os.getcwd()
    nandv = '%s-%s' % (options.name, options.version)

    os.chdir(build_dir)

    args = ['zip', '-9r', '%s.zip' % nandv, nandv]
    cmd = subprocess.Popen(args)
    retcode = cmd.wait()

    if retcode != 0:
        raise RuntimeError, "Error creating zip"

    os.chdir(cwd)

    return os.path.join(build_dir, '%s.zip' % nandv)

def build_tar_gz(build_dir, options):
    cwd = os.getcwd()
    nandv = '%s-%s' % (options.name, options.version)

    os.chdir(build_dir)

    args = ['tar', '-cvzf', '%s.tar.gz' % nandv, nandv]
    cmd = subprocess.Popen(args)
    retcode = cmd.wait()

    if retcode != 0:
        raise RuntimeError, "Error creating zip"

    os.chdir(cwd)

    return os.path.join(build_dir, '%s.tar.gz' % nandv)

def build_tar_bz2(build_dir, options):
    cwd = os.getcwd()
    nandv = '%s-%s' % (options.name, options.version)

    os.chdir(build_dir)

    args = ['tar', '-cvjf', '%s.tar.bz2' % nandv, nandv]
    cmd = subprocess.Popen(args)
    retcode = cmd.wait()

    if retcode != 0:
        raise RuntimeError, "Error creating zip"

    os.chdir(cwd)

    return os.path.join(build_dir, '%s.tar.bz2' % nandv)

def clean_package_dir(package_dir):
    for files in os.walk(package_dir):
        for f in files[2]:
            if f.endswith('.pyc'):
                os.unlink(os.path.join(files[0], f))

def package_project(src_dir, api_dir, options):
    """
    Builds tar.gz, tar.bz2, zip from the src_dir's
    """
    build_dir = tempfile.mkdtemp()
    package_dir = os.path.join(build_dir, '%s-%s' % (options.name, options.version))
    shutil.copytree(src_dir, package_dir)
    shutil.copytree(api_dir, os.path.join(package_dir, 'doc', 'api'))

    clean_package_dir(package_dir)

    return build_dir, build_zip(build_dir, options), \
        build_tar_gz(build_dir, options), build_tar_bz2(build_dir, options)

if __name__ == '__main__':
    options, args = parse_args()

    if options.baseurl is None:
        raise ValueError, "baseurl arg is required"
    if options.name is None:
        raise ValueError, "project name is required"
    if options.package is None:
        raise ValueError, "package name is required"
    if options.version is None:
        raise ValueError, "version is required"

    export_dir = export_repo(options)
    sys.path.insert(0, export_dir)
    api_dir = build_api_docs(export_dir, options)

    build_dir = package_project(export_dir, api_dir, options)
    archives = build_dir[1:]
    build_dir = build_dir[0]

    for archive in archives:
        shutil.copy(archive, os.getcwd())

    shutil.rmtree(export_dir)
    shutil.rmtree(api_dir)
    shutil.rmtree(build_dir)
