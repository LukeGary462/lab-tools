#!/usr/bin/env python
# python 3
#pylint: disable=import-error
##    @file:    oscilloscope.py
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
oscilloscopes
"""

from instruments.instrument import Instrument


class DS1074Z(Instrument):
    """
    This class describes a Rigol ds1074z scope.
    """

    def __init__(self, **kwargs):
        super().__init__()
        pass

