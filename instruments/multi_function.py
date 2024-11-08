#!/usr/bin/env python

"""
multi-function bench equipment
"""

from instruments.instrument import Instrument
from pyvisa import (InvalidSession)

class MultiFunctionModels:
    """
    This class describes oscilloscope models.
    """
    def __init__(self):
        self.models = {}
        self.models['U3606B'] = U3606B

    def get(self, model: str) -> Instrument:
        """
        Gets the specified model.

        :param      model:  The model
        :type       model:  str

        :returns:   class
        :rtype:     Instrument
        """
        return self.models.get(model, None)

    def is_valid(self, model: str) -> bool:
        return model in self.models.keys()

class U3606B(Instrument):
    """
    This class describes a Keysight U3606B PSU/Meter.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__inst_init__(model='U3606B', **kwargs)

    def measure_all(self, channel: int = 1) -> dict:
        """
        measure P,I,V from channel

        :param      channel:   cahnnel number
        :type       channel:   int

        :returns:   measurement dict
        :rtype:     dict
        """
        res = self.query(f'meas:all:dc? ch{channel}')
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
        del channel
        res = self.query('sens:curr?')
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
        del channel
        res = self.query('sens:volt?')
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
        del channel
        volts = self.measure_source_voltage()
        amps = self.measure_source_current()
        return volts*amps

    def set_output_current(self, current: float, channel: int = 1):
        """
        Sets the output current.

        :param      current:  The current
        :type       current:  float
        :param      channel:  The channel
        :type       channel:  int
        """
        del channel
        # sour:curry
        self.write(f'sour:curr {current}')
        res = self.query(f'sour:curr?')
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
        del channel
        self.write(f'volt {voltage}')
        return self.measure_source_voltage()

    def enable_source(self, channel: int = 1) -> bool:
        """
        Enables the source.

        :param      channel:  The channel
        :type       channel:  int

        :returns:   True if On, False if Off
        :rtype:     bool
        """
        del channel
        self.write(f'outp on')
        res = self.query(f'outp?')
        if '1' in res:
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
        del channel
        self.write(f'outp off')
        res = self.query(f'outp? ')
        if '0' in res:
            return True
        return False

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
