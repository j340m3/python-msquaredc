========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis| |appveyor| |requires|
        | |coveralls| |codecov|
        | |landscape| |scrutinizer| |codacy| |codeclimate|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|

.. |docs| image:: https://readthedocs.org/projects/python-msquaredc/badge/?style=flat
    :target: https://readthedocs.org/projects/python-msquaredc
    :alt: Documentation Status

.. |travis| image:: https://travis-ci.org/j340m3/python-msquaredc.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/j340m3/python-msquaredc

.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/github/j340m3/python-msquaredc?branch=master&svg=true
    :alt: AppVeyor Build Status
    :target: https://ci.appveyor.com/project/j340m3/python-msquaredc

.. |requires| image:: https://requires.io/github/j340m3/python-msquaredc/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/j340m3/python-msquaredc/requirements/?branch=master

.. |coveralls| image:: https://coveralls.io/repos/j340m3/python-msquaredc/badge.svg?branch=master&service=github
    :alt: Coverage Status
    :target: https://coveralls.io/r/j340m3/python-msquaredc

.. |codecov| image:: https://codecov.io/github/j340m3/python-msquaredc/coverage.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/j340m3/python-msquaredc

.. |landscape| image:: https://landscape.io/github/j340m3/python-msquaredc/master/landscape.svg?style=flat
    :target: https://landscape.io/github/j340m3/python-msquaredc/master
    :alt: Code Quality Status

.. |codacy| image:: https://api.codacy.com/project/badge/Grade/f13770dd85f2400e8e37f0b4ac0fb495
    :target: https://www.codacy.com/app/j340m3/python-msquaredc
    :alt: Codacy Code Quality Status

.. |codeclimate| image:: https://codeclimate.com/github/j340m3/python-msquaredc/badges/gpa.svg
   :target: https://codeclimate.com/github/j340m3/python-msquaredc
   :alt: CodeClimate Quality Status

.. |version| image:: https://img.shields.io/pypi/v/msquaredc.svg
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/msquaredc

.. |commits-since| image:: https://img.shields.io/github/commits-since/j340m3/python-msquaredc/v0.1.0.svg
    :alt: Commits since latest release
    :target: https://github.com/j340m3/python-msquaredc/compare/v0.1.0...master

.. |wheel| image:: https://img.shields.io/pypi/wheel/msquaredc.svg
    :alt: PyPI Wheel
    :target: https://pypi.python.org/pypi/msquaredc

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/msquaredc.svg
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/msquaredc

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/msquaredc.svg
    :alt: Supported implementations
    :target: https://pypi.python.org/pypi/msquaredc

.. |scrutinizer| image:: https://img.shields.io/scrutinizer/g/j340m3/python-msquaredc/master.svg
    :alt: Scrutinizer Status
    :target: https://scrutinizer-ci.com/g/j340m3/python-msquaredc/


.. end-badges

An example package. Generated with cookiecutter-pylibrary.

* Free software: BSD license

Installation
============

::

    pip install msquaredc

Documentation
=============

https://python-msquaredc.readthedocs.io/

Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
