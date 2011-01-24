Release tools for PyAMF
=======================

This is a collection of tools used to create a release of the PyAMF_ library.

.. contents:: :backlinks: entry


Overview
--------

- downloads and grabs a source tree tarball from Github (http://github.com/hydralabs/pyamf/tarball/release-0.6b2 for example)
- updates the release date in the changelog
- removes the `egg_info` metadata from setup.cfg
- builds the documentation and includes the examples
- exports packages: `.zip/.tar.gz/.tar.bz2/.egg`
- downloads the `MD5SUMS` file and appends the new MD5 entries for the tarballs

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

  export SOURCE=http://github.com/hydralabs/pyamf/tarball/release-0.6b2
  export DESTINATION=dist

  bin/build-tarballs $SOURCE $DESTINATION


Currently produces::

  Started tarballs builder...

  Output directory: /Users/thijstriemstra/Sites/projects/opensource/pyamf-release/dist
  Source tarball URL: http://github.com/hydralabs/pyamf/tarball/release-0.6b2

  Downloading source tarball...
  Extracting tarball...

  Building PyAMF 0.6b2...
  	Updating changelog...
  	Updating setup.cfg...
  	Building documentation...
  	Creating package(s)...
  	 - dist/PyAMF-0.6b2.tar.bz2
  	   Size: 5.8 MB
  	   MD5: b4510dad04a96fc7651f3ef26e8f8b9c
  	 - dist/PyAMF-0.6b2.tar.gz
  	   Size: 6.1 MB
  	   MD5: b86026b07a80cc6d159112344647479d
  	 - dist/PyAMF-0.6b2.zip
  	   Size: 11.7 MB
  	   MD5: 87b6d50d417abc9f2902c1cee650785d
  
  Distribution builder ready.


Egg
---

This creates a standalone Python Egg file, eg. `PyAMF-0.6b2-py2.6-macosx-10.5-fat3.egg`.

Start the tool with::

  export SOURCE=http://github.com/hydralabs/pyamf/tarball/release-0.6b2
  export DESTINATION=dist
  
  bin/build-egg $SOURCE $DESTINATION


Currently produces::

  Started egg builder...
  
  Output directory: /Users/thijstriemstra/Sites/projects/opensource/pyamf-release/dist
  Source tarball URL: http://github.com/hydralabs/pyamf/tarball/release-0.6b2
  
  Downloading source tarball...
  Extracting tarball...
  
  Building PyAMF 0.6b2...
  	Updating changelog...
  	Updating setup.cfg...
  	Creating package(s)...
  	Building egg...
  	 - dist/PyAMF-0.6b2-py2.6-macosx-10.5-fat3.egg
  	   Size: 441.8 KB
  	   MD5: ba2bef6863593085ed934fd29340a3b6
  
  Distribution builder ready.

Documentation
-------------

This generates 3 archives in the specified `DESTINATION` directory:

- PyAMF-x.x.x.tar.bz2
- PyAMF-x.x.x.tar.gz
- PyAMF-x.x.x.tar.zip

Start the tool with::
  
  export SOURCE=http://github.com/hydralabs/pyamf/tarball/release-0.6b2
  export DESTINATION=dist
  
  bin/build-doc $SOURCE $DESTINATION


Currently produces::

  Started documentation builder...
  
  Output directory: /Users/thijstriemstra/Sites/projects/opensource/pyamf-release/dist
  Source tarball URL: http://github.com/hydralabs/pyamf/tarball/release-0.6b2
  
  Downloading source tarball...
  Extracting tarball...
  
  Building PyAMF 0.6b2...
  	Updating changelog...
  	Updating setup.cfg...
  	Building documentation...
    Including examples...
  	Creating package(s)...
  	 - dist/PyAMF-0.6b2.tar.bz2
  	   Size: 5.6 MB
  	 - dist/PyAMF-0.6b2.tar.gz
  	   Size: 5.9 MB
  	 - dist/PyAMF-0.6b2.zip
  	   Size: 10.3 MB
  
  Distribution builder ready.


.. _PyAMF: http://pyamf.org
.. _Sphinx:   http://sphinx.pocoo.org
.. _sphinxcontrib.epydoc: http://packages.python.org/sphinxcontrib-epydoc/
.. _Beam:     http://github.com/collab-project/sphinx-themes/tree/master/source/themes/beam
.. _Twisted:  http://twistedmatrix.com
.. _Python:         http://python.org
.. _Git:      http://git-scm.com
