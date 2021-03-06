#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Author: Bradley Gram-Hansen
Time created:  12:41
Date created:  09/11/2017

License: MIT
'''

from os.path import realpath, dirname, join
from setuptools import setup, find_packages
import sys


DISTNAME = 'pyfo'
DESCRIPTION = "Python for FOPPL"
LONG_DESCRIPTION =  open('README.md').read()
MAINTAINER = 'Bradley Gram-hansen, Tobias Kohn'
MAINTAINER_EMAIL = 'bradleygramhansen@gmail.com, webmaster@tobiaskohn.ch '
AUTHOR = 'Bradley Gram-Hansen, Tobias Kohn'
AUTHOR_EMAIL = 'bradley@robots.ox.ac.uk, webmaster@tobiaskohn.ch '
URL = "http://github.com/bradleygramhansen/pyfo"
LICENSE = 'LICENSE.txt'
VERSION = "0.1.0"
PACKAGES = ['pyfo', 'pyfoppl']
classifiers = ['Development Status :: 1 - Production/UnStable',
               'Programming Language :: Python',
               'Programming Language :: Python :: 3.6',
               'License :: OSI Approved :: MIT License',
               'Intended Audience :: Science/Research',
               'Topic :: Scientific/Engineering',
               'Topic :: Scientific/Engineering :: Mathematics',
               'Operating System :: OS Independent']

PROJECT_ROOT = dirname(realpath(__file__))
REQUIREMENTS_FILE = join(PROJECT_ROOT, 'requirements.txt')

with open(REQUIREMENTS_FILE) as f:
    install_reqs = f.read().splitlines()

if sys.version_info < (3, 4):
    install_reqs.append('enum34')

# test_reqs = ['pytest', 'pytest-cov']
# if sys.version_info[0] == 2:  # py3 has mock in stdlib
#     test_reqs.append('mock')


if __name__ == "__main__":
    setup(name=DISTNAME,
          version=VERSION,
          maintainer=MAINTAINER,
          maintainer_email=MAINTAINER_EMAIL,
          description=DESCRIPTION,
          license=LICENSE,
          url=URL,
          long_description=LONG_DESCRIPTION,
          packages=find_packages(),
          package_data={'docs': ['*']},
          include_package_data=True,
          classifiers=classifiers,
          install_requires=install_reqs)
          #
          # tests_require=test_reqs,
          # test_suite='nose.collector')