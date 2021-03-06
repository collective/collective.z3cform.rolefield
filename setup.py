# -*- coding: utf-8 -*-
"""Installer for the collective.contact.plonegroup package."""

from setuptools import find_packages
from setuptools import setup


long_description = (
    open('README.rst').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.rst').read()
    + '\n' +
    open('CHANGES.rst').read()
    + '\n')


setup(
    name='collective.z3cform.rolefield',
    version='0.5.dev0',
    description="A field for managing local roles",
    long_description=long_description,
    # Get more from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 4.2",
        "Framework :: Plone :: 4.3",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
    ],
    keywords='',
    author='Ecreall, Entrouvert, IMIO',
    author_email='g.bastien@imio.be',
    url='http://pypi.python.org/pypi/collective.z3cform.rolefield',
    license='GPL',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['collective', 'collective.z3cform'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'zope.schemaevent',
        'plone.api',
    ],
    extras_require={
        'test': [
            'mock',
            'ecreall.helpers.testing',
            'plone.app.testing',
            'plone.app.dexterity',
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
