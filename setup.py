#!/usr/bin/env python

"""
instrumentation module, VISA Communication
"""

from setuptools import setup

setup(
    name='instruments',
    version='0.15',
    description='',
    url='',
    author='Luke Gary',
    author_email='',
    license='Private',
    packages=[
        'instruments',
    ],
    install_requires=[
        'pyserial',
        'numpy',
        'scipy',
        'pyvisa',
        'dacite'
    ]
)
