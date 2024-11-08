#!/usr/bin/env python

"""
multimeter interfaces
"""
from instruments.instrument import Instrument
from instruments.multi_function import U3606B
from pyvisa import (VisaIOError, VisaIOWarning, InvalidSession)

class MultimeterModels:
    """
    This class describes multimeter models.
    """
    def __init__(self):
        """construct"""
        self.models = {}
        self.models['U3606B'] = U3606B
        self.models['34465A'] = KS34465A
        self.models['DM3058E'] = DM3058E
        self.models['34401A'] = HP34401A

    def get(self, model: str) -> Instrument:
        """
        Gets the specified model.

        :param      model:  The model
        :type       model:  str

        :returns:   multimeter object
        :rtype:     Instrument
        """
        return self.models.get(model, None)

    def is_valid(self, model: str) -> bool:
        """
        Determines whether the specified model is valid.

        :param      model:  The model
        :type       model:  str

        :returns:   True if the specified model is valid, False otherwise.
        :rtype:     bool
        """
        return model in self.models.keys()

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
    meter_obj = None
    multimeter = MultimeterModels().get(model)
    if multimeter:
        try:
            meter_obj = multimeter(
                serial_number=meter_serial,
                include_tcpip=tcpip,
                )
        except (VisaIOError, VisaIOWarning, InvalidSession):
            print(f'Could not connect to multimeter {model}:{meter_serial}')
            meter_obj = None
    return meter_obj

class HP34401A(Instrument):
    """
    This class describes a hp 34401 a.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        kwargs['include_rs232'] = True
        kwargs['include_tcpip'] = False
        self.__inst_init__(model='34401A', **kwargs)

        ''' HP 34401a needs some lovin'''
        self.write_configs(
            configs=['syst:rem', '*cls', '*rst']
        )


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


class KS34465A(Instrument):
    """
    This class describes a Keysight 34465A Bench Meter.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__inst_init__(model='34465A', **kwargs)

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
        super().__init__(**kwargs)
        self.__inst_init__(model='DM3058E', **kwargs)

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

