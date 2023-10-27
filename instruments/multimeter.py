#!/usr/bin/env python
# python 3
#pylint: disable=import-error
##    @file:    multimeter.py
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
multimeter interfaces
"""
from instruments.instrument import Instrument
from instruments.multi_function import U3606B
from pyvisa import (VisaIOError, VisaIOWarning, InvalidSession)

def connect_to_multimeter(model: str, meter_serial: str = None, tcpip: bool = False) -> object:
    """
    Connects to multimeter based on a model string.

    :param      model:         The model
    :type       model:         str
    :param      meter_serial:  The meter serial
    :type       meter_serial:  str

    :returns:   multimeter object if model is valid, None if not
    :rtype:     object
    """
    mutlimeter_models = {
        'U3606B': U3606B,
        '34465A': KS34465A,
        'DM3058E': DM3058E,
    }
    meter_obj = None
    multimeter = mutlimeter_models.get(model, None)
    if multimeter:
        try:
            meter_obj = multimeter(
                serial_number=meter_serial,
                include_tcpip=tcpip,
                debug=False
                )
        except (VisaIOError, VisaIOWarning, InvalidSession):
            print(f'Could not connect to multimeter {model}:{meter_serial}')
            meter_obj = None
    return meter_obj

class KS34465A(Instrument):
    """
    This class describes a Keysight 34465A Bench Meter.
    """
    def __init__(self, **kwargs):
        serial_number = kwargs.get('serial_number', None)
        tcpip = kwargs.get('include_tcpip', True)
        try:
            kwargs.pop('serial_number')
            kwargs.pop('include_tcpip')
        except KeyError:
            pass
        super().__init__(**kwargs)
        if serial_number:
            self.debug(f'Attempting Connect to {serial_number}', enable=True)
            self.connect(
                serial_number=serial_number,
                include_tcpip=tcpip
            )
        else:
            # connect to the first 34465A
            self.debug('No Serial Given, connecting to first 34465A', enable=True)
            devices = self.list_devices()
            connected = False
            for device in devices:
                if device.get('model') == '34465A':
                    self.debug(f'Attempt connect to KS34465A - {device.get("serial_number")}')
                    self.connect(
                        serial_number=device.get('serial_number'),
                        include_tcpip=kwargs.get('include_tcpip', True)
                    )
                    connected = True
                    break
            if connected is False:
                raise InvalidSession(f'Could not connect to {serial_number}')

    def measure_voltage(self):
        """
        measure dmm voltage, autoranging by default
        """
        res = self.query(f'meas:volt:dc?')
        if res is not None:
            return float(res)
        self.debug(f'Measurement Error')
        return res

    def measure_current(self):
        """
        measure dmm current, autoranging by default
        """
        res = self.query(f'meas:curr:dc?')
        if res is not None:
            return float(res)
        self.debug(f'Measurement Error')
        return res

    def measure_resistance(self):
        """
        measure dmm resistance, autoranging by default
        """
        res = self.query('meas:res?')
        if res is not None:
            return float(res)
        self.debug(f'Measurement Error')
        return res

    def measure_continuity(self):
        """
        measure dmm continuity
        """
        res = self.query('meas:cont?')
        if res is not None:
            return float(res)
        self.debug(f'Measurement Error')
        return res

class DM3058E(Instrument):
    """
    This class describes a DM3058E Bench Meter.
    """
    def __init__(self, **kwargs):
        serial_number = kwargs.get('serial_number', None)
        tcpip = kwargs.get('include_tcpip', True)
        try:
            kwargs.pop('serial_number')
            kwargs.pop('include_tcpip')
        except KeyError:
            pass
        super().__init__(**kwargs)
        if serial_number:
            self.debug(f'Attempting Connect to {serial_number}', enable=True)
            self.connect(
                serial_number=serial_number,
                include_tcpip=tcpip
            )
        else:
            # connect to the first DM3058E
            self.debug('No Serial Given, connecting to first DM3058E', enable=True)
            devices = self.list_devices()
            connected = False
            for device in devices:
                if device.get('model') == 'DM3058E':
                    self.connect(
                        serial_number=device.get('serial_number'),
                        include_tcpip=kwargs.get('include_tcpip', True)
                    )
                    connected = True
                    break
            if connected is False:
                raise InvalidSession(f'Could not connect to {serial_number}')

    def measure_voltage(self):
        """
        measure dmm voltage, autoranging by default
        """
        res = self.query(f'meas:volt:dc?')
        if res is not None:
            return float(res)
        self.debug(f'Measurement Error')
        return res

    def measure_current(self):
        """
        measure dmm current, autoranging by default
        """
        res = self.query(f'meas:curr:dc?')
        if res is not None:
            return float(res)
        self.debug(f'Measurement Error')
        return res

    def measure_resistance(self):
        """
        measure dmm resistance, autoranging by default
        """
        res = self.query('meas:res?')
        if res is not None:
            return float(res)
        self.debug(f'Measurement Error')
        return res

    def measure_continuity(self):
        """
        measure dmm continuity
        """
        res = self.query('meas:cont?')
        if res is not None:
            return float(res)
        self.debug(f'Measurement Error')
        return res
