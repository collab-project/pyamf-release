#!/usr/local/bin/python

# Copyright (c) 2007-2009 The PyAMF Project.
# See LICENSE for details.

"""
A basic release builder.

Example usage:
  python package.py --version=0.3 --name=PyAMF --baseurl=http://svn.pyamf.org/pyamf/tags --branch=release-0.3

For more help try:
  python package.py --help
"""

import os, os.path, sys, shutil
import subprocess, tempfile
import hashlib

def export_svn(url, options):
    print
    print 'Checking out: %s\n' % url

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

    if options.repository == 'svn':
        retcode, cmd, export_dir = export_svn(repo_url, options)
    else:
        raise ValueError, "Unknown repository type %s" % options.repository

    if retcode != 0:
        raise RuntimeError, "Problem exporting repository"

    return export_dir

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

def parse_args():
    def parse_targets(option, opt, value, parser):
        print value

    from optparse import OptionParser

    parser = OptionParser()

    parser.add_option('--baseurl', dest='baseurl',
                      help='Root URL of the source control system')
    parser.add_option('--branch', dest='branch', default='trunk',
                      help='Name of the target folder in the source control system [default: %default]')
    parser.add_option('--version', dest='version',
                      help='The version number of the project')
    parser.add_option('--name', dest='name', help='The name of the project')
    parser.add_option('--username', dest='username', default=None,
                                    help='Username to access the repository')
    parser.add_option('--password', dest='password', default=None,
                                    help='Password to access the repository')
    parser.add_option('--repository', dest='repository', default='svn',
                       help='Source control system type [default: %default]')
    parser.add_option('--dotpath', dest='dotpath', default='/usr/bin/dot',
                      help="Location of the Graphviz 'dot' executable [default: %default]")

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
        raise RuntimeError, "Error creating tar.gz"

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
        raise RuntimeError, "Error creating tar.bz2"

    os.chdir(cwd)

    return os.path.join(build_dir, '%s.tar.bz2' % nandv)

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
