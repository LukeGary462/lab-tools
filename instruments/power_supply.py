#!/usr/bin/env python
# python 3
#pylint: disable=import-error
##    @file:    power_supply.py
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
power supply interfaces
"""
from instruments.instrument import Instrument
from instruments.multi_function import U3606B
from pyvisa import (VisaIOError, VisaIOWarning, InvalidSession)

def connect_to_power_supply(model: str, supply_serial: str = None, tcpip: bool = False) -> object:
    """
    Connects to power supply based on model string.

    :param      model:          The model
    :type       model:          str
    :param      supply_serial:  The supply serial
    :type       supply_serial:  str

    :returns:   power supply object if model is valid, None if not
    :rtype:     object
    """
    power_supply_models = {
        'U3606B': U3606B,
        'DP832': DP832,
    }

    power_supply_obj = None
    power_supply = power_supply_models.get(model, None)
    if power_supply:
        try:
            power_supply_obj = power_supply(
                serial_number=supply_serial,
                include_tcpip=tcpip,
                debug=False
                )
        except (VisaIOError, VisaIOWarning, InvalidSession):
            print(f'Could not connect to power supply {model}:{supply_serial}')
            power_supply_obj = None
    return power_supply_obj

class DP832(Instrument):
    """
    This class describes a rigol dp832.
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
            # connect to the first DP832
            self.debug('No Serial Given, connecting to first DP832', enable=True)
            devices = self.list_devices()
            connected = False
            self.debug(devices)
            for device in devices:
                if device.get('model') == 'DP832':
                    self.connect(
                        serial_number=device.get('serial_number'),
                        include_tcpip=kwargs.get('include_tcpip', True)
                    )
                    connected = True
                    break
            if connected is False:
                raise InvalidSession()

    @staticmethod
    def check_channel(channel: int):
        """
        make sure channel is ok for dp832

        :param      channel:  The channel
        :type       channel:  int
        """
        if 0 < channel < 4:
            return True
        raise AttributeError(
            f'channel must be [1,3] not {channel}'
        )

    def measure_all(self, channel: int = 1) -> dict:
        """
        measure P,I,V from channel

        :param      channel:   cahnnel number
        :type       channel:   int

        :returns:   measurement dict
        :rtype:     dict
        """
        ret = None
        if self.check_channel(channel):
            res = self.query(f'meas:all:dc? ch{channel}')
            if res is None:
                return ret

            res = res.replace('\n', '')
            res = res.split(',')
            ret = {}
            ret['volts'] = res[0]
            ret['amps'] = res[1]
            ret['watts'] = res[2]
        return ret

    def measure_source_current(self, channel: int = 1) -> float:
        """
        measure channel current

        :param      channel:  The channel
        :type       channel:  number

        :returns:   current
        :rtype:     float
        """
        res = self.query(f'meas:curr? ch{channel}')
        if res is not None:
            return float(res)
        self.debug(f'Measurement Error')
        return res

    def measure_source_voltage(self, channel: int = 1) -> float:
        """
        measure channel voltage

        :param      channel:  The channel
        :type       channel:  number

        :returns:   voltage
        :rtype:     float
        """
        res = self.query(f'meas? ch{channel}')
        if res is not None:
            return float(res)
        self.debug(f'Measurement Error')
        return res

    def measure_source_power(self, channel: int = 1) -> float:
        """
        measure channel power

        :param      channel:  The channel
        :type       channel:  int

        :returns:   power
        :rtype:     float
        """
        res = self.query(f'meas:powe? ch{channel}')
        if res is not None:
            return float(res)
        self.debug(f'Measurement Error')
        return res

    def set_output_current(self, current: float, channel: int = 1):
        """
        Sets the output current.

        :param      current:  The current
        :type       current:  float
        :param      channel:  The channel
        :type       channel:  int
        """
        self.write(f'SOUR{channel}:CURR {current}')
        res = self.query(f'SOUR{channel}:CURR?')
        if float(res) != float(current):
            print(f'Error in Setting Current! sent {current}, recv {res}')

    def set_output_voltage(self, voltage: float, channel: int = 1):
        """
        Sets the output voltage.

        :param      voltage:  The voltage
        :type       voltage:  float
        :param      channel:  The channel
        :type       channel:  int
        """
        self.write(f'SOUR{channel}:VOLT {voltage}')
        res = self.query(f'SOUR{channel}:VOLT?')
        if float(res) != float(voltage):
            print(f'Error in Setting Voltage! sent {voltage}, recv {res}')

    def enable_source(self, channel: int = 1) -> bool:
        """
        Enables the source.

        :param      channel:  The channel
        :type       channel:  int

        :returns:   True if On, False if Off
        :rtype:     bool
        """
        self.write(f'outp ch{channel}, on')
        res = self.query(f'outp? ch{channel}')
        if 'ON' in res:
            return True
        return False

    def disable_source(self, channel: int = 1) -> bool:
        """
        Disables the source.

        :param      channel:  The channel
        :type       channel:  int

        :returns:   True if on, False if Off
        :rtype:     bool
        """
        self.write(f'outp ch{channel}, off')
        res = self.query(f'outp? ch{channel}')
        if 'OFF' in res:
            return True
        return False
