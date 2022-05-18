#!/usr/bin/env python
# python 3
##    @file:    function_generator.py
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
function and arbitrary waveform generators
"""

from instruments.instrument import Instrument


class AG2062F(Instrument):
    """
    This class describes an OWON ag2062f arbitrary waveform generator.
    """

    def __init__(self, **kwargs):
        super().__init__()
        pass
