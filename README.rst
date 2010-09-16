Release tools for PyAMF_
========================

This is a collection of tools used to release PyAMF.

Features:

- downloads and grabs a source tree tarball from Github (http://github.com/hydralabs/pyamf/tarball/release-0.6b2 for example)
- updates the release date in the changelog
- removes the egg_info metadata from setup.cfg
- builds the documentation and includes the examples
- exports packages: .zip/.tar.gz/.tar.bz2/.egg
- downloads the MD5SUMS file and appends the new MD5 entries for the tarballs


build-tarballs
--------------

Start it with::

  export SOURCE=http://github.com/hydralabs/pyamf/tarball/release-0.6b2
  export DESTINATION=dist

  bin/build-tarballs $SOURCE $DESTINATION


Currently produces::

  Started tarballs builder...

  Output directory: /Users/thijstriemstra/Sites/projects/opensource/pyamf-release/dist
  Source URL: http://github.com/hydralabs/pyamf/tarball/release-0.6b2

  Downloading source tree tarball...
  Extracting source tree tarball...

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
  
  	Updating MD5SUMS...
  
  Distribution builder ready.


build-egg
---------

Start it with::

  export SOURCE=http://github.com/hydralabs/pyamf/tarball/release-0.6b2
  export DESTINATION=dist
  
  bin/build-egg $SOURCE $DESTINATION


Currently produces::

  Started egg builder...
  
  Output directory: /Users/thijstriemstra/Sites/projects/opensource/pyamf-release/dist
  Source URL: http://github.com/hydralabs/pyamf/tarball/release-0.6b2
  
  Downloading source tree tarball...
  Extracting source tree tarball...
  
  Building PyAMF 0.6b2...
  	Updating changelog...
  	Updating setup.cfg...
  	Creating package(s)...
  	Building egg...
  	 - dist/PyAMF-0.6b2-py2.6-macosx-10.5-fat3.egg
  	   Size: 441.8 KB
  	   MD5: ba2bef6863593085ed934fd29340a3b6
  
  	Updating MD5SUMS...
  
  Distribution builder ready.

build-doc
---------

Start it with::
  
  export SOURCE=http://github.com/hydralabs/pyamf/tarball/release-0.6b2
  export DESTINATION=dist
  
  bin/build-doc $SOURCE $DESTINATION


Currently produces::

  Started documentation builder...
  
  Output directory: /Users/thijstriemstra/Sites/projects/opensource/pyamf-release/dist
  Source URL: http://github.com/hydralabs/pyamf/tarball/release-0.6b2
  
  Downloading source tree tarball...
  Extracting source tree tarball...
  
  Building PyAMF 0.6b2...
  	Updating changelog...
  	Updating setup.cfg...
  	Building documentation...
  	Creating package(s)...
  	 - dist/PyAMF-0.6b2.tar.bz2
  	   Size: 5.6 MB
  	 - dist/PyAMF-0.6b2.tar.gz
  	   Size: 5.9 MB
  	 - dist/PyAMF-0.6b2.zip
  	   Size: 10.3 MB
  
  Distribution builder ready.


.. _PyAMF: http://pyamf.org
