#!/usr/bin/env python

from setuptools import setup, find_packages

import elpy

setup(
    description="Backend for the elpy Emacs mode",
    long_description=elpy.__doc__,
    url="https://github.com/jorgenschaefer/elpy",
    author_email="contact@jorgenschaefer.de",
    license="GPL",
    include_package_data=True,
    test_suite="elpy"
)
