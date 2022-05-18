#!/usr/bin/env python
# python 3
##    @file:    setup.py
#     @name:    Luke Gary
#  @company:    RyeEffectsResearch
#     @date:    2020/3/10
################################################################################
# @copyright
#   Copyright 2020 RyeEffectsResearch as an  unpublished work.
#   All Rights Reserved.
#
# @license The information contained herein is confidential
#   property of RyeEffectsResearch. The user, copying, transfer or
#   disclosure of such information is prohibited except
#   by express written agreement with RyeEffectsResearch.
################################################################################

"""
instrumentation module, VISA Communication
"""

from setuptools import setup

setup(
    name='lab instrumentation module',
    version='0.1',
    description='lab instrument communication classes',
    url='https://github.com/LukeGary462/lab-tools/master/',
    author='Luke Gary',
    author_email='sales.reffects@gmail.com',
    license='public',
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
