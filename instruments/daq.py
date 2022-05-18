#!/usr/bin/env python
# python 3
##    @file:    daq.py
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
Data Aquisition Units
"""

from instruments.instrument import Instrument


class KS34902A:
    """
    This class describes a keysight 34902a mux card.
    """
    def __init__(self, **kwargs):
        # default to slot 100
        self._address = kwargs.get('addr', '100')


class KS34972A(Instrument):
    """
    This class describes a keysight 34972a daq.
    """

    _supported_modules = {
        '34902A': KS34902A
    }

    def __init__(self, **kwargs):
        attachments = kwargs.get('attachments', None)

        if attachments and isinstance(dict, attachments):
            # install attachments
            self.modules = []
            for attachment, address in attachments:
                for _model, _class in self._supported_modules:
                    if _model in attachment:
                        self.modules.append(
                            _class(
                                addr=address
                            )
                        )




