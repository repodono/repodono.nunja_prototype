# -*- coding: utf-8 -*-
"""Installer for the repodono.nunja package."""

from setuptools import find_packages
from setuptools import setup


long_description = (
    open('README.rst').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CHANGES.rst').read()
    + '\n')


setup(
    name='repodono.nunja',
    version='0.1',
    description="Nunjucks x Jinja2",
    long_description=long_description,
    # Get more from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Environment :: Web Environment",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords='Python',
    author='Tommy Yu',
    author_email='tommy.yu@auckland.ac.nz',
    url='http://pypi.python.org/pypi/repodono.nunja',
    license='GPL version 2',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['repodono'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools>=11.3',
        'Jinja2',
    ],
    extras_require={},
    entry_points="""
    [repodono.nunja.mold]
    repodono.nunja.molds = repodono.nunja:molds
    """,
    test_suite="repodono.nunja.tests.test_suite",
)
