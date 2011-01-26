Release tools for PyAMF
=======================

This is a collection of tools used to create a release of the PyAMF_ library.

.. contents:: :backlinks: entry


Overview
--------

- downloads and grabs a source tree tarball from Github (http://github.com/hydralabs/pyamf/tarball/release-0.6 for example)
- updates the release date in the changelog
- removes the `egg_info` metadata from setup.cfg
- builds the main documentation and optionally include the examples
- builds the API documentation
- exports packages: `.zip/.tar.gz/.tar.bz2/.egg`

Optional (disabled by default):
- download the `MD5SUMS` file and appends the new MD5 entries for the tarballs


Dependencies
------------

To use this tool you'll need the following software pre-installed on your system:

===========================  ========
Name                         Version
===========================  ========
Python_                      2.5
Twisted_                     8.0
===========================  ========

To build the documentation you need the following software:

===========================  ========
Name                         Version
===========================  ========
Sphinx_                      1.0
`sphinxcontrib.epydoc`_      any
===========================  ========


Installation
------------

#. This tool uses Git_ for source control. Grab the source::

    git clone git://github.com/collab-project/pyamf-release.git

#. Install the package::

    sudo python setup.py develop


Build
=====

There are scripts to build a set of archives, a standalone egg file and the documentation.

Archives
--------

This generates 3 archives in the specified `DESTINATION` directory:

- PyAMF-x.x.x.tar.bz2
- PyAMF-x.x.x.tar.gz
- PyAMF-x.x.x.tar.zip

Start the tool with::

  export SOURCE=http://github.com/hydralabs/pyamf/tarball/release-0.6
  export DESTINATION=dist

  bin/build-tarballs $SOURCE $DESTINATION


Currently produces::

  Started tarballs builder...

  Output directory: /Users/thijstriemstra/Sites/projects/opensource/pyamf-release/dist
  Source tarball URL: http://github.com/hydralabs/pyamf/tarball/release-0.6

  Downloading source tarball...
  Extracting tarball...

  Building PyAMF 0.6...
	Updating changelog...
	Updating setup.cfg...
	Building theme...
	Building main documentation...
	Building API documentation...
	Creating package(s)...
	 - dist/PyAMF-0.6.tar.bz2
	   Size: 1.3 MB
	   MD5: 3729a41e78637d6aa8583113960c70cb
	 - dist/PyAMF-0.6.tar.gz
	   Size: 1.5 MB
	   MD5: ac499d9d2faf11c5df0199559a949985
	 - dist/PyAMF-0.6.zip
	   Size: 1.4 MB
	   MD5: 1c367882e965bab831babd4d43742a1d

  
  Builder ready.


Egg
---

This creates a standalone Python Egg file, eg. `PyAMF-0.6-py2.7-linux-x86_64.egg`.

Start the tool with::

  export SOURCE=http://github.com/hydralabs/pyamf/tarball/release-0.6
  export DESTINATION=dist
  
  bin/build-egg $SOURCE $DESTINATION


Currently produces::

  Started egg builder...
  
  Output directory: /Users/thijstriemstra/Sites/projects/opensource/pyamf-release/dist
  Source tarball URL: http://github.com/hydralabs/pyamf/tarball/release-0.6
  
  Downloading source tarball...
  Extracting tarball...
  
  Building PyAMF 0.6...
  	Updating changelog...
  	Updating setup.cfg...
  	Creating package(s)...
  	Building egg...
  	 - dist/PyAMF-0.6-py2.7-linux-x86_64.egg
  	   Size: 745.9 KB
  	   MD5: 50f14645ef99069b9257b2dbc7ae3028
  
  Builder ready.

Documentation
-------------

This generates 3 archives in the specified `DESTINATION` directory:

- PyAMF-x.x.x.tar.bz2
- PyAMF-x.x.x.tar.gz
- PyAMF-x.x.x.tar.zip

Start the tool with::
  
  export SOURCE=http://github.com/hydralabs/pyamf/tarball/release-0.6
  export DESTINATION=dist
  
  bin/build-doc $SOURCE $DESTINATION


Currently produces::

  Started documentation builder...
  
  Output directory: /Users/thijstriemstra/Sites/projects/opensource/pyamf-release/dist
  Source tarball URL: http://github.com/hydralabs/pyamf/tarball/release-0.6
  
  Downloading source tarball...
  Extracting tarball...
  
  Building PyAMF 0.6...
	Updating changelog...
	Updating setup.cfg...
	Building theme...
	Building main documentation...
	Including examples...
	Building API documentation...
	Creating package(s)...
	 - dist/PyAMF-0.6.tar.bz2
	   Size: 5.3 MB
	 - dist/PyAMF-0.6.tar.gz
	   Size: 5.5 MB
	 - dist/PyAMF-0.6.zip
	   Size: 5.5 MB

  
  Builder ready.


.. _PyAMF: http://pyamf.org
.. _Sphinx:   http://sphinx.pocoo.org
.. _sphinxcontrib.epydoc: http://packages.python.org/sphinxcontrib-epydoc/
.. _Beam:     http://github.com/collab-project/sphinx-themes/tree/master/source/themes/beam
.. _Twisted:  http://twistedmatrix.com
.. _Python:         http://python.org
.. _Git:      http://git-scm.com
