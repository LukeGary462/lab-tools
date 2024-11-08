#!/usr/bin/env python

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




