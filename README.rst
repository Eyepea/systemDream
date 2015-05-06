===========
systemDream
===========

| |docs| |travis| |appveyor| |coveralls| |landscape| |scrutinizer|
| |version| |downloads| |wheel| |supported-versions| |supported-implementations|

.. |docs| image:: https://readthedocs.org/projects/systemDream/badge/?style=flat
    :target: https://readthedocs.org/projects/systemDream
    :alt: Documentation Status

.. |travis| image:: http://img.shields.io/travis/Eyepea/systemDream/master.png?style=flat
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/Eyepea/systemDream

.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/github/Eyepea/systemDream?branch=master
    :alt: AppVeyor Build Status
    :target: https://ci.appveyor.com/project/Eyepea/systemDream

.. |coveralls| image:: http://img.shields.io/coveralls/Eyepea/systemDream/master.png?style=flat
    :alt: Coverage Status
    :target: https://coveralls.io/r/Eyepea/systemDream

.. |landscape| image:: https://landscape.io/github/Eyepea/systemDream/master/landscape.svg?style=flat
    :target: https://landscape.io/github/Eyepea/systemDream/master
    :alt: Code Quality Status

.. |version| image:: http://img.shields.io/pypi/v/systemdream.png?style=flat
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/systemdream

.. |downloads| image:: http://img.shields.io/pypi/dm/systemdream.png?style=flat
    :alt: PyPI Package monthly downloads
    :target: https://pypi.python.org/pypi/systemdream

.. |wheel| image:: https://pypip.in/wheel/systemdream/badge.png?style=flat
    :alt: PyPI Wheel
    :target: https://pypi.python.org/pypi/systemdream

.. |supported-versions| image:: https://pypip.in/py_versions/systemdream/badge.png?style=flat
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/systemdream

.. |supported-implementations| image:: https://pypip.in/implementation/systemdream/badge.png?style=flat
    :alt: Supported imlementations
    :target: https://pypi.python.org/pypi/systemdream

.. |scrutinizer| image:: https://img.shields.io/scrutinizer/g/Eyepea/systemDream/master.png?style=flat
    :alt: Scrutinizer Status
    :target: https://scrutinizer-ci.com/g/Eyepea/systemDream/

systemd bindings written in pure Python, based on C-bindings API of `python-systemd
<http://www.freedesktop.org/software/systemd/python-systemd/>`_.
The main goal of this library is to be very easy to install in a pyvenv or virtualenv, contrary to ``python-systemd``.

For now, only ``systemd.journal`` has been ported, pull requests are welcome.

* Free software: LGPL2 license

Installation
============

::

    pip install systemdream

Documentation
=============

You can mainly follow the official ``python-systemd`` documentation: http://www.freedesktop.org/software/systemd/python-systemd/

.. https://systemdream.readthedocs.org/

..

    Development
    ===========

    To run the all tests run::

        tox

